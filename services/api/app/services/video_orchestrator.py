"""
Video Orchestrator - Orchestrează generarea video-urilor pentru AutoPro Daune
=============================================================================
Aceasta este logica CENTRALĂ pentru toate video-urile din sistem.

Responsabilități:
1. Primește cerere de generare video (din frontend sau automat)
2. Decide ce tip de video să genereze (lead, social, raport, marketing)
3. Adună datele necesare din Supabase
4. Generează script cu AI (OpenAI)
5. Creează voce cu ElevenLabs
6. Generează vizual (static sau animat)
7. Combină totul cu FFmpeg
8. Salvează în Supabase și Cloudflare R2
9. Returnează URL-ul video-ului

Acest serviciu este SINGLE POINT OF TRUTH pentru video generation.
"""

import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

from .supabase_client import get_supabase_service_instance
from .internal_video_service import get_internal_video_service
from .video_engine_lipsync import enqueue_lipsync
from .voice_elevenlabs import tts_elevenlabs

logger = logging.getLogger(__name__)


class VideoType:
    """Tipuri de video suportate."""
    LEAD_TESTIMONIAL = "lead_testimonial"
    LEAD_UPDATE = "lead_update"
    LEAD_REMINDER = "lead_reminder"
    SOCIAL_TIKTOK = "social_tiktok"
    SOCIAL_INSTAGRAM = "social_instagram"
    SOCIAL_YOUTUBE = "social_youtube"
    REPORT_DAILY = "report_daily"
    REPORT_WEEKLY = "report_weekly"
    MARKETING_AD = "marketing_ad"
    MARKETING_PROMO = "marketing_promo"
    LIPSYNC_AVATAR = "lipsync_avatar"  # Video cu avatar animat cu lip-sync
    GENERIC = "generic"


class VideoOrchestrator:
    """Orchestrator central pentru generarea video-urilor."""
    
    def __init__(self):
        self.supabase = get_supabase_service_instance()
        self.video_service = get_internal_video_service()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
    
    async def generate_video(
        self,
        video_type: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Metodă MASTER pentru generarea oricărui tip de video.
        
        Args:
            video_type: Tipul video-ului (vezi VideoType)
            context: Context specific pentru tipul de video
                     - Pentru lead: {"lead_id": "123"}
                     - Pentru social: {"platform": "tiktok", "topic": "daune auto"}
                     - Pentru raport: {"period": "daily"}
                     - Pentru generic: {"text": "...", "options": {...}}
        
        Returns:
            Dict cu video_id, video_url, duration, cost, etc.
        """
        try:
            logger.info(f"[VideoOrchestrator] Starting generation: {video_type}")
            
            # 1. Validare tip video
            if video_type not in [getattr(VideoType, attr) for attr in dir(VideoType) if not attr.startswith('_')]:
                return {"success": False, "error": f"Invalid video type: {video_type}"}
            
            # 2. Adună date bazate pe tip
            data = await self._gather_data(video_type, context)
            if not data["success"]:
                return data
            
            # 3. Generează script
            script = await self._generate_script(video_type, data["data"])
            if not script["success"]:
                return script
            
            # 4. Determină parametrii video
            params = self._determine_video_params(video_type, context)
            
            # 5. Generează video
            result = await self.video_service.generate_video(
                text=script["script"],
                voice_style=params["voice_style"],
                background_type=params["background_type"],
                aspect_ratio=params["aspect_ratio"],
                resolution=params["resolution"]
            )
            
            if not result["success"]:
                return result
            
            # 6. Salvează în baza de date
            video_record = await self._save_to_database(video_type, result, context)
            
            # 7. Upload la Cloudflare R2 (opțional, dacă e configurat)
            cdn_url = await self._upload_to_cdn(result["video_path"])
            
            return {
                "success": True,
                "video_id": result["video_id"],
                "video_path": result["video_path"],
                "video_url": cdn_url or result["video_path"],
                "duration_seconds": result["duration_seconds"],
                "file_size_mb": result["file_size_mb"],
                "video_type": video_type,
                "script": script["script"],
                "cost": 0.0,  # Intern = zero cost
                "provider": "AutoPro Internal",
                "database_id": video_record.get("id") if video_record else None
            }
            
        except Exception as e:
            logger.error(f"[VideoOrchestrator] Generation failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def _gather_data(self, video_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Adună datele necesare bazat pe tipul video-ului."""
        try:
            if video_type == VideoType.LEAD_TESTIMONIAL or video_type == VideoType.LEAD_UPDATE or video_type == VideoType.LEAD_REMINDER:
                # Pentru lead-uri, ia datele lead-ului
                lead_id = context.get("lead_id")
                if not lead_id:
                    return {"success": False, "error": "lead_id required"}
                
                lead_data = self.supabase._table_select("leads", "*", f"id.eq.{lead_id}")
                if not lead_data:
                    return {"success": False, "error": f"Lead {lead_id} not found"}
                
                return {
                    "success": True,
                    "data": {
                        "lead": lead_data[0],
                        "type": "lead"
                    }
                }
            
            elif video_type == VideoType.REPORT_DAILY:
                # Pentru raport zilnic, ia statisticile zilei
                today = datetime.now().date()
                
                leads_today = self.supabase._table_select("leads", "*", f"created_at.gte.{today.isoformat()}")
                completed_today = self.supabase._table_select("leads", "*", f"status.eq.completed,updated_at.gte.{today.isoformat()}")
                revenues_today = self.supabase._table_select("revenues", "*", f"timestamp.gte.{today.isoformat()}")
                
                total_revenue = sum(float(r.get("amount", 0)) for r in revenues_today)
                
                return {
                    "success": True,
                    "data": {
                        "date": today,
                        "leads_count": len(leads_today),
                        "completed_count": len(completed_today),
                        "revenue_total": total_revenue,
                        "type": "daily_report"
                    }
                }
            
            elif video_type == VideoType.SOCIAL_TIKTOK or video_type == VideoType.SOCIAL_INSTAGRAM:
                # Pentru social media, ia topic și generează content
                topic = context.get("topic", "AutoPro Daune - Experți în daune auto")
                platform = context.get("platform", "tiktok")
                
                # Ia ultimele cazuri de succes pentru credibilitate
                recent_completed = self.supabase._table_select(
                    "leads",
                    "*",
                    "status.eq.completed",
                    order=("updated_at", False),
                    limit=3
                )
                
                return {
                    "success": True,
                    "data": {
                        "topic": topic,
                        "platform": platform,
                        "success_cases": len(recent_completed),
                        "type": "social_media"
                    }
                }
            
            elif video_type == VideoType.GENERIC:
                # Pentru generic, folosește direct textul furnizat
                text = context.get("text", "")
                if not text:
                    return {"success": False, "error": "text required for generic video"}
                
                return {
                    "success": True,
                    "data": {
                        "text": text,
                        "type": "generic"
                    }
                }
            
            else:
                return {"success": False, "error": f"Unsupported video type: {video_type}"}
                
        except Exception as e:
            logger.error(f"[VideoOrchestrator] Data gathering failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _generate_script(self, video_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generează script pentru video folosind AI sau template."""
        try:
            data_type = data.get("type")
            
            if data_type == "lead":
                lead = data["lead"]
                if video_type == VideoType.LEAD_TESTIMONIAL:
                    script = f"""
Bună ziua, sunt {lead.get('name', 'client')}.

Am avut un {lead.get('damage_type', 'accident auto')} și nu știam cum să procedez cu asigurarea.

Am apelat la AutoPro Daune și echipa lor m-a ghidat pas cu pas.

Acum am primit despăgubirea completă și recomand cu încredere AutoPro Daune!

Dacă ai nevoie de ajutor cu daune auto, sună la AutoPro Daune.
                    """.strip()
                
                elif video_type == VideoType.LEAD_UPDATE:
                    script = f"""
Update pentru dosarul {lead.get('name', 'client')}:

Cazul de {lead.get('damage_type', 'daune')} este în procesare activă.

Echipa AutoPro Daune lucrează pentru a obține cea mai bună despăgubire.

Vă vom contacta în curând cu detalii.

AutoPro Daune - Partenerii tăi în recuperarea despăgubirilor.
                    """.strip()
                
                else:  # REMINDER
                    script = f"""
Atenție {lead.get('name', 'client')}!

Dosarul tău de {lead.get('damage_type', 'daune')} necesită acțiune.

Te rugăm să ne contactezi pentru următorii pași.

AutoPro Daune - Suntem aici pentru tine.
                    """.strip()
            
            elif data_type == "daily_report":
                script = f"""
Raport AutoPro Daune - {data['date'].strftime('%d %B %Y')}

📊 Activitate de azi:
✅ {data['leads_count']} lead-uri noi
✅ {data['completed_count']} cazuri finalizate  
✅ {data['revenue_total']:.0f} RON venituri generate

🎯 Performanță excelentă! Continuăm mâine cu același ritm.

AutoPro Daune - Lideri în recuperarea despăgubirilor.
                """.strip()
            
            elif data_type == "social_media":
                platform = data.get("platform", "tiktok")
                if platform == "tiktok":
                    script = f"""
❗ Ai avut accident auto?

✅ AutoPro Daune te ajută să obții despăgubirea COMPLETĂ

🎯 Peste {data.get('success_cases', 0)} cazuri rezolvate cu succes

📞 Sună ACUM și primește consultanță GRATUITĂ

AutoPro Daune - Experții tăi în daune auto 🚗
                    """.strip()
                else:
                    script = f"""
{data.get('topic', 'AutoPro Daune')}

Experți în recuperarea despăgubirilor pentru daune auto.

Echipă dedicată, proces simplu, rezultate garantate.

Contactează-ne astăzi pentru consultanță gratuită.
                    """.strip()
            
            elif data_type == "generic":
                script = data["text"]
            
            else:
                return {"success": False, "error": f"Unknown data type: {data_type}"}
            
            return {
                "success": True,
                "script": script,
                "word_count": len(script.split())
            }
            
        except Exception as e:
            logger.error(f"[VideoOrchestrator] Script generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _determine_video_params(self, video_type: str, context: Dict[str, Any]) -> Dict[str, str]:
        """Determină parametrii video bazat pe tip."""
        # Default params
        params = {
            "voice_style": "professional",
            "background_type": "gradient",
            "aspect_ratio": "16:9",
            "resolution": "1080p"
        }
        
        # Customizări bazate pe tip
        if video_type in [VideoType.LEAD_TESTIMONIAL, VideoType.LEAD_UPDATE]:
            params["voice_style"] = "empathetic"
            params["background_type"] = "gradient"
        
        elif video_type == VideoType.SOCIAL_TIKTOK:
            params["voice_style"] = "confident"
            params["aspect_ratio"] = "9:16"  # Vertical pentru TikTok
            params["background_type"] = "solid"
        
        elif video_type == VideoType.SOCIAL_INSTAGRAM:
            params["voice_style"] = "professional"
            params["aspect_ratio"] = "1:1"  # Square pentru Instagram
        
        elif video_type == VideoType.REPORT_DAILY:
            params["voice_style"] = "confident"
            params["background_type"] = "gradient"
            params["aspect_ratio"] = "16:9"
        
        # Override cu context dacă e furnizat
        if "voice_style" in context:
            params["voice_style"] = context["voice_style"]
        if "background_type" in context:
            params["background_type"] = context["background_type"]
        if "aspect_ratio" in context:
            params["aspect_ratio"] = context["aspect_ratio"]
        if "resolution" in context:
            params["resolution"] = context["resolution"]
        
        return params
    
    async def _save_to_database(self, video_type: str, result: Dict[str, Any], context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Salvează video-ul în baza de date."""
        try:
            video_record = {
                "video_id": result["video_id"],
                "type": video_type,
                "file_path": result["video_path"],
                "duration_seconds": result.get("duration_seconds", 0),
                "file_size_mb": result.get("file_size_mb", 0),
                "cost": 0.0,
                "provider": "internal",
                "status": "completed",
                "created_at": datetime.now().isoformat(),
                "metadata": context
            }
            
            # Salvează în tabelul video_jobs
            saved = self.supabase._table_insert("video_jobs", video_record)
            return saved
            
        except Exception as e:
            logger.warning(f"[VideoOrchestrator] Database save failed: {e}")
            return None
    
    async def _upload_to_cdn(self, video_path: str) -> Optional[str]:
        """Upload video la Cloudflare R2 (dacă e configurat)."""
        try:
            # TODO: Implementează upload la Cloudflare R2
            # Pentru moment returnăm None (video local)
            return None
        except Exception as e:
            logger.warning(f"[VideoOrchestrator] CDN upload failed: {e}")
            return None


# Singleton instance
_video_orchestrator = None

def get_video_orchestrator() -> VideoOrchestrator:
    """Returnează instanța singleton."""
    global _video_orchestrator
    if _video_orchestrator is None:
        _video_orchestrator = VideoOrchestrator()
    return _video_orchestrator

