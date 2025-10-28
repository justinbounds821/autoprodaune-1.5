#!/usr/bin/env python3
"""
SupabaseService – strat unic de acces la date pentru AutoPro Daune
Single Source of Truth (SSOT) pe Supabase/Postgres.

- CRUD Leads & Referrals
- Evenimente financiare (cost/revenue) + dashboards
- Social summary & post logs
- Video queue (jobs) + retry
- Logs (aplicație) + stats
- Notificări (persistă evenimentul; trimiterea efectivă o face alt serviciu)

Necesită:
  pip install supabase==2.* httpx tenacity python-dotenv

ENV necesare:
  SUPABASE_URL
  SUPABASE_SERVICE_KEY
  SUPABASE_SCHEMA=public (opțional)
"""

from __future__ import annotations

import os
import time
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError
from supabase import create_client, Client


# -----------------------------
# Config & Helpers
# -----------------------------

log = logging.getLogger("SupabaseService")
if not log.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

def _env(name: str, default: Optional[str] = None) -> str:
    v = os.getenv(name, default)
    if v is None:
        raise RuntimeError(f"Missing required env var: {name}")
    return v

def utc_now_iso() -> str:
    return datetime.utcnow().isoformat()

@dataclass(frozen=True)
class SBConfig:
    url: str
    service_key: str
    schema: str = "public"

# -----------------------------
# SupabaseService
# -----------------------------

class SupabaseService:
    def __init__(self, client: Optional[Client] = None) -> None:
        """
        Dacă primești un client din exterior (ex: pentru teste), îl folosești.
        Altfel construiește din ENV.
        """
        if client:
            self.sb = client
            self.config = SBConfig(url="external", service_key="external", schema=os.getenv("SUPABASE_SCHEMA", "public"))
        else:
            # Assert required environment variables
            missing = [k for k in ("SUPABASE_URL", "SUPABASE_SERVICE_KEY") if not os.getenv(k)]
            if missing:
                raise RuntimeError(f"Missing required env var: {', '.join(missing)}")
            
            cfg = SBConfig(
                url=_env("SUPABASE_URL"),
                service_key=_env("SUPABASE_SERVICE_KEY"),
                schema=os.getenv("SUPABASE_SCHEMA", "public"),
            )
            self.sb = create_client(cfg.url, cfg.service_key)
            self.config = cfg

        # lazy HTTP client pt. webhook-uri (ex. n8n), dacă e nevoie
        self.http = httpx.Client(timeout=10.0)

        log.info("SupabaseService initialized; schema=%s", self.config.schema)

    @property
    def client(self):
        """Backward compatibility property for accessing the Supabase client."""
        return self.sb
    
    # -----------------------------
    # Generic helpers
    # -----------------------------

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, min=0.5, max=3))
    def _table_select(self, table: str, *cols: str, **kwargs) -> List[Dict[str, Any]]:
        q = self.sb.table(table).select(",".join(cols) if cols else "*")
        if "order" in kwargs:
            name, desc = kwargs["order"]
            q = q.order(name, desc=desc)
        if "filters" in kwargs:
            for f in kwargs["filters"]:
                # f: Tuple[str, str, Any] -> ("eq","field","value")
                op, field, value = f
                q = getattr(q, op)(field, value)
        res = q.execute()
        return res.data or []

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, min=0.5, max=3))
    def _table_insert(self, table: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        res = self.sb.table(table).insert(payload).select("*").execute()
        return res.data[0] if res.data else {}

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, min=0.5, max=3))
    def _table_update_eq(self, table: str, field: str, value: Any, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        res = self.sb.table(table).update(payload).eq(field, value).execute()
        return res.data or []

    def _table_update(self, table: str, payload: Dict[str, Any], filters: List[tuple]) -> List[Dict[str, Any]]:
        """Update with flexible filters (similar to _table_select)."""
        q = self.sb.table(table).update(payload)
        for f in filters:
            op, field, value = f
            q = getattr(q, op)(field, value)
        res = q.execute()
        return res.data or []

    def _table_delete(self, table: str, filters: List[tuple]) -> Dict[str, Any]:
        """Delete with flexible filters."""
        q = self.sb.table(table).delete()
        for f in filters:
            op, field, value = f
            q = getattr(q, op)(field, value)
        res = q.execute()
        return {"success": True, "deleted": len(res.data or [])}

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, min=0.5, max=3))
    def _table_delete_eq(self, table: str, field: str, value: Any) -> Dict[str, Any]:
        self.sb.table(table).delete().eq(field, value).execute()
        return {"success": True, "id": value}

    # -----------------------------
    # Leads
    # -----------------------------

    def leads_list(self, limit: int = 500) -> List[Dict[str, Any]]:
        return self._table_select("leads", "*", order=("created_at", True))[:limit]

    def lead_create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # sanitizare minimă
        p = {
            "name": payload.get("name") or payload.get("nume") or "Unknown",
            "phone": payload.get("phone"),
            "email": payload.get("email"),
            "location": payload.get("location"),
            "damage_type": payload.get("damage_type"),
            "priority": payload.get("priority", "medium"),
            "details": payload.get("details"),
            "files": payload.get("files", []),
            "status": payload.get("status", "new"),
            "source": payload.get("source", "web"),
            "medium": payload.get("medium"),
            "campaign": payload.get("campaign"),
            "created_at": utc_now_iso(),
            "updated_at": utc_now_iso(),
        }
        return self._table_insert("leads", p)

    def lead_delete(self, lead_id: int) -> Dict[str, Any]:
        return self._table_delete_eq("leads", "id", lead_id)

    def lead_update(self, lead_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        update_data["updated_at"] = utc_now_iso()
        result = self._table_update_eq("leads", "id", lead_id, update_data)
        if result:
            return {
                "success": True,
                "message": f"Lead {lead_id} actualizat cu succes",
                "data": result[0]
            }
        else:
            return {
                "success": False,
                "message": f"Lead {lead_id} nu a fost găsit"
            }
    
    # -----------------------------
    # Referrals
    # -----------------------------

    def referrals_list(self, limit: int = 500) -> List[Dict[str, Any]]:
        return self._table_select("referrals", "*", order=("created_at", True))[:limit]

    def referral_create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        p = {
            "referrer_name": payload.get("referrer_name"),
            "referrer_phone": payload.get("referrer_phone"),
            "referred_name": payload.get("referred_name"),
            "referred_phone": payload.get("referred_phone"),
            "referral_type": payload.get("referral_type", "friend"),
            "bonus_amount": payload.get("bonus_amount", 50.0),
            "status": payload.get("status", "pending"),
            "created_at": utc_now_iso(),
            "updated_at": utc_now_iso(),
        }
        return self._table_insert("referrals", p)

    def referral_complete(self, referral_id: int) -> Dict[str, Any]:
        update_data = {
            "status": "completed",
            "completed_at": utc_now_iso(),
            "updated_at": utc_now_iso()
        }
        result = self._table_update_eq("referrals", "id", referral_id, update_data)
        if result:
            return {
                "success": True,
                "message": f"Referral {referral_id} marcat ca completat",
                "data": result[0]
            }
        else:
            return {
                "success": False,
                "message": f"Referral {referral_id} nu a fost găsit"
            }

    def referral_stats(self) -> Dict[str, Any]:
        """Get referral statistics."""
        referrals = self._table_select("referrals", "*")
        
        total_referrals = len(referrals)
        completed_referrals = len([r for r in referrals if r.get("status") == "completed"])
        pending_referrals = len([r for r in referrals if r.get("status") == "pending"])
        
        total_bonus_paid = sum([r.get("bonus_amount", 0) for r in referrals if r.get("status") == "completed"])
        average_bonus = total_bonus_paid / completed_referrals if completed_referrals > 0 else 0
        
        # Find top referrer
        referrer_counts: Dict[str, int] = {}
        for r in referrals:
            referrer = r.get("referrer_name", "Unknown")
            referrer_counts[referrer] = referrer_counts.get(referrer, 0) + 1
        
        top_referrer = max(referrer_counts.items(), key=lambda x: x[1]) if referrer_counts else ("N/A", 0)
        
        return {
            "total_referrals": total_referrals,
            "completed_referrals": completed_referrals,
            "pending_referrals": pending_referrals,
            "total_bonus_paid": total_bonus_paid,
            "average_bonus": average_bonus,
            "top_referrer": {
                "name": top_referrer[0],
                "referrals_count": top_referrer[1],
                "total_bonus": sum([r.get("bonus_amount", 0) for r in referrals if r.get("referrer_name") == top_referrer[0] and r.get("status") == "completed"])
            }
        }
    
    # -----------------------------
    # Financial (costs / revenue)
    # -----------------------------

    def financial_add_event(self, kind: str, amount: float, provider: Optional[str] = None,
                            operation: Optional[str] = None, extra_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if kind not in ("cost", "revenue"):
            raise ValueError("kind must be 'cost' or 'revenue'")
        
        # Map to our existing schema
        if kind == "cost":
            table = "api_costs"
            payload = {
                "provider": provider or "unknown",
                "operation": operation or "unknown",
                "cost": float(amount),
                "currency": "EUR",
                "metadata": extra_data or {},
                "timestamp": utc_now_iso(),
            }
        else:  # revenue
            table = "revenues"
            payload = {
                "source": provider or "unknown",
                "amount": float(amount),
                "currency": "EUR",
                "metadata": extra_data or {},
                "timestamp": utc_now_iso(),
            }
        
        return self._table_insert(table, payload)

    def financial_dashboard(self) -> Dict[str, Any]:
        # fără RPC, calculăm în client
        costs = self._table_select("api_costs", "cost", "timestamp")
        revs  = self._table_select("revenues", "amount", "timestamp")
        total_costs = sum(float(x["cost"]) for x in costs)
        total_revenue = sum(float(x["amount"]) for x in revs)
        profit = total_revenue - total_costs
        roi = (profit / total_costs * 100.0) if total_costs else 0.0
        
        # Get recent data
        recent_costs = sorted(costs, key=lambda x: x.get("timestamp", ""), reverse=True)[:5]
        recent_revenues = sorted(revs, key=lambda x: x.get("timestamp", ""), reverse=True)[:5]
        
        return {
            "total_costs": round(total_costs, 2),
            "total_revenue": round(total_revenue, 2),
            "net_profit": round(profit, 2),
            "roi_percentage": round(roi, 2),
            "recent_costs": recent_costs,
            "recent_revenues": recent_revenues,
        }

    def financial_profit_loss(self, days: int = 30) -> Dict[str, Any]:
        start = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        # Get costs in date range
        costs = self.sb.table("api_costs").select("*").gte("timestamp", start).execute().data or []
        # Get revenues in date range  
        revenues = self.sb.table("revenues").select("*").gte("timestamp", start).execute().data or []
        
        # Group by date
        by_day: Dict[str, Dict[str, float]] = {}
        for r in costs:
            day = r["timestamp"][:10]
            d = by_day.setdefault(day, {"revenue": 0.0, "costs": 0.0})
            d["costs"] += float(r["cost"])
            
        for r in revenues:
            day = r["timestamp"][:10]
            d = by_day.setdefault(day, {"revenue": 0.0, "costs": 0.0})
            d["revenue"] += float(r["amount"])
            
        series = []
        for day in sorted(by_day.keys()):
            revenue = by_day[day]["revenue"]
            costs = by_day[day]["costs"]
            series.append({
                "date": day,
                "revenue": round(revenue, 2),
                "costs": round(costs, 2),
                "profit": round(revenue - costs, 2)
            })
        return {"series": series}
    
    # -----------------------------
    # Social summary & posts
    # -----------------------------

    def social_summary(self) -> Dict[str, Any]:
        # citește agregate simple din tabelul social_posts (dacă există)
        rows = self._table_select("social_posts", "*", order=("posted_at", True))
        summary: Dict[str, Dict[str, Any]] = {}
        for r in rows:
            p = r.get("platform", "unknown")
            entry = summary.setdefault(p, {"status": "online", "posts_today": 0, "engagement_rate": 0.0,
                                           "followers": 0, "revenue": 0.0})
            # posts today
            if r["posted_at"][:10] == datetime.utcnow().strftime("%Y-%m-%d"):
                entry["posts_today"] += 1
            entry["revenue"] += float(r.get("revenue") or 0.0)
            # engagement_rate/followers pot veni din alt tabel sau din r["metrics"]
        return summary

    def social_log_post(self, platform: str, post_id: str, content_type: str, engagement_rate: float = 0.0,
                        revenue_generated: float = 0.0, metrics: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = {
            "platform": platform,
            "content": f"Post {post_id}",
            "engagement": int(engagement_rate * 1000),  # Convert to integer
            "views": metrics.get("views", 0) if metrics else 0,
            "likes": metrics.get("likes", 0) if metrics else 0,
            "comments": metrics.get("comments", 0) if metrics else 0,
            "shares": metrics.get("shares", 0) if metrics else 0,
            "revenue": float(revenue_generated),
            "status": "published",
            "posted_at": utc_now_iso(),
            "created_at": utc_now_iso(),
        }
        return self._table_insert("social_posts", payload)
    
    # -----------------------------
    # Video queue
    # -----------------------------

    def video_queue_list(self, status: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        query = self._table_select("video_jobs", "*", order=("created_at", True))
        if status:
            query = [job for job in query if job.get("status") == status]
        return query[:limit]

    def video_queue_enqueue(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        p = {
            "client_job_id": payload.get("client_job_id"),
            "filename": payload.get("filename", "unknown.mp4"),
            "status": payload.get("status", "pending"),
            "progress": payload.get("progress", 0),
            "duration_seconds": payload.get("duration_seconds"),
            "resolution": payload.get("resolution", "1080p"),
            "file_size_mb": payload.get("file_size_mb"),
            "output_url": payload.get("output_url"),
            "error_message": payload.get("error_message"),
            "created_at": payload.get("created_at", utc_now_iso()),
            "updated_at": payload.get("updated_at", utc_now_iso()),
            "completed_at": payload.get("completed_at"),
            "type": payload.get("type", "basic"),
        }
        # Add payload field if schema supports it (fallback if not)
        try:
            p["payload"] = payload.get("payload", payload)
        except:
            pass  # Ignore if payload column doesn't exist yet
        
        return self._table_insert("video_jobs", p)

    def video_queue_retry(self, job_id: str) -> Dict[str, Any]:
        self._table_update_eq("video_jobs", "id", job_id, {"status": "retry", "updated_at": utc_now_iso()})
        return {"job_id": job_id, "status": "retry"}
    
    # -----------------------------
    # Logs & notifications
    # -----------------------------

    def app_log(self, level: str, service: str, message: str, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = {
            "level": level.lower(),
            "service": service,
            "message": message,
            "details": meta or {},
            "timestamp": utc_now_iso(),
        }
        return self._table_insert("logs", payload)

    def logs_list(self, level: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        filters = []
        if level:
            filters.append(("eq", "level", level.lower()))
        return self._table_select("logs", "*", order=("timestamp", True), filters=filters)[:limit]

    def notification_enqueue(self, kind: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        p = {
            "type": kind,
            "recipient": payload.get("recipient", ""),
            "subject": payload.get("subject", ""),
            "message": payload.get("message", ""),
            "status": "pending",
            "created_at": utc_now_iso()
        }
        return self._table_insert("notifications", p)

    # -----------------------------
    # WhatsApp messages
    # -----------------------------

    def whatsapp_message_create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new WhatsApp message record in the database."""
        p = {
            "message_id": payload.get("message_id"),
            "from_number": payload.get("from_number"),
            "to_number": payload.get("to_number"),
            "message_type": payload.get("message_type", "text"),
            "content": payload.get("content"),
            "status": payload.get("status", "received"),
            "metadata": payload.get("metadata", {}),
            "created_at": utc_now_iso(),
        }
        return self._table_insert("whatsapp_messages", p)

    def whatsapp_messages_list(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List WhatsApp messages sorted by creation date descending."""
        return self._table_select("whatsapp_messages", "*", order=("created_at", True))[:limit]

    def whatsapp_stats(self) -> Dict[str, Any]:
        """Get WhatsApp messaging statistics."""
        messages = self._table_select("whatsapp_messages", "*")
        
        total_messages = len(messages)
        received_messages = len([m for m in messages if m.get("status") == "received"])
        sent_messages = len([m for m in messages if m.get("status") == "sent"])
        
        # Group by date for daily stats
        by_day: Dict[str, int] = {}
        for msg in messages:
            day = msg["created_at"][:10] if msg.get("created_at") else "unknown"
            by_day[day] = by_day.get(day, 0) + 1
        
        # Get unique contacts
        unique_contacts = set()
        for msg in messages:
            from_num = msg.get("from_number")
            to_num = msg.get("to_number")
            if from_num:
                unique_contacts.add(from_num)
            if to_num:
                unique_contacts.add(to_num)
        
        return {
            "total_messages": total_messages,
            "received_messages": received_messages,
            "sent_messages": sent_messages,
            "unique_contacts": len(unique_contacts),
            "messages_by_day": by_day
        }

    # -----------------------------
    # Storage upload
    # -----------------------------
    
    def upload_from_path(self, bucket: str, key: str, local_path: str) -> str:
        """Upload file from local path to Supabase Storage and return public URL."""
        try:
            # Upload file to storage
            self.sb.storage.from_(bucket).upload(
                path=key, 
                file=local_path, 
                file_options={"cacheControl": "3600", "upsert": True}
            )
            
            # Try to get public URL (robust to client variants)
            try:
                res = self.sb.storage.from_(bucket).get_public_url(key)
                if isinstance(res, str):
                    return res
                if isinstance(res, dict):
                    return res.get("publicUrl") or res.get("publicURL") or (res.get("data", {}) or {}).get("publicUrl")
                return key  # Fallback to key
            except Exception:
                return key  # Fallback to key if public URL fails
                
        except Exception as e:
            logging.error(f"Upload failed for {local_path} to {bucket}/{key}: {e}")
            return key  # Fallback to key


# -----------------------------
# Singleton accessor (optional)
# -----------------------------

_service_singleton: Optional[SupabaseService] = None

def get_supabase_service() -> SupabaseService:
    global _service_singleton
    if _service_singleton is None:
        _service_singleton = SupabaseService()
    return _service_singleton


# -----------------------------
# Self-test (dev only)
# -----------------------------
if __name__ == "__main__":
    # rulați:  python services/supabase_client.py
    s = get_supabase_service()
    log.info("Health test: listing leads…")
    leads = s.leads_list()
    log.info("Leads found: %d", len(leads))
    log.info("Dashboard: %s", json.dumps(s.financial_dashboard(), indent=2))

# Global instance pentru backward compatibility - lazy initialization
supabase_service = None

def get_supabase_service_instance():
    global supabase_service
    if supabase_service is None:
        supabase_service = get_supabase_service()
    return supabase_service
