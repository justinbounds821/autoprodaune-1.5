"""
REAL Financial Service - AutoPro Daune
Revenue tracking, cost tracking, profit calculation
NO MOCKS - All calculations from database
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from decimal import Decimal
from .supabase_client import get_supabase_service_instance
from fastapi import HTTPException
import logging
import csv
import io

logger = logging.getLogger(__name__)

class FinancialService:
    """Real financial tracking with database persistence"""
    
    def __init__(self):
        self.supabase = get_supabase_service_instance()
    
    async def create_transaction(
        self,
        user_id: UUID,
        type: str,
        category: str,
        amount: float,
        description: Optional[str] = None,
        source: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> Dict[str, Any]:
        """Create financial transaction"""
        try:
            transaction_data = {
                'user_id': str(user_id),
                'type': type,
                'category': category,
                'amount': amount,
                'currency': 'RON',
                'description': description,
                'source': source,
                'metadata': metadata or {},
                'transaction_date': datetime.utcnow().isoformat()
            }
            
            result = self.supabase.client.table('financial_transactions')\
                .insert(transaction_data)\
                .execute()
            
            logger.info(f"Transaction created: {type} {amount} RON")
            return result.data[0] if result.data else {}
            
        except Exception as e:
            logger.error(f"Error creating transaction: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def track_api_cost(
        self,
        provider: str,
        operation_type: str,
        units_consumed: float,
        cost_per_unit: float,
        total_cost: float,
        metadata: Optional[dict] = None
    ) -> Dict[str, Any]:
        """Track API usage cost"""
        try:
            cost_data = {
                'provider': provider,
                'operation_type': operation_type,
                'units_consumed': units_consumed,
                'cost_per_unit': cost_per_unit,
                'total_cost': total_cost,
                'currency': 'USD',
                'metadata': metadata or {}
            }
            
            result = self.supabase.client.table('api_costs')\
                .insert(cost_data)\
                .execute()
            
            logger.info(f"API cost tracked: {provider} {total_cost} USD")
            return result.data[0] if result.data else {}
            
        except Exception as e:
            logger.error(f"Error tracking API cost: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def record_revenue(
        self,
        lead_id: Optional[UUID],
        amount: float,
        source: str,
        description: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> Dict[str, Any]:
        """Record revenue from lead conversion"""
        try:
            revenue_data = {
                'lead_id': str(lead_id) if lead_id else None,
                'amount': amount,
                'currency': 'RON',
                'source': source,
                'description': description,
                'metadata': metadata or {}
            }
            
            result = self.supabase.client.table('revenues')\
                .insert(revenue_data)\
                .execute()
            
            logger.info(f"Revenue recorded: {amount} RON from {source}")
            return result.data[0] if result.data else {}
            
        except Exception as e:
            logger.error(f"Error recording revenue: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_revenue_summary(
        self,
        user_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        period: str = "30d"
    ) -> Dict[str, Any]:
        """REAL revenue calculation from database"""
        try:
            # Calculate date range
            if not end_date:
                end_date = datetime.utcnow()
            if not start_date:
                if period == "7d":
                    start_date = end_date - timedelta(days=7)
                elif period == "30d":
                    start_date = end_date - timedelta(days=30)
                elif period == "90d":
                    start_date = end_date - timedelta(days=90)
                else:
                    start_date = end_date - timedelta(days=30)
            
            # Query revenues
            query = self.supabase.client.table('revenues')\
                .select('*')\
                .gte('created_at', start_date.isoformat())\
                .lte('created_at', end_date.isoformat())
            
            result = query.execute()
            revenues = result.data or []
            
            # Calculate totals
            total_revenue = sum(float(r.get('amount', 0)) for r in revenues)
            
            # Breakdown by source
            by_source = {}
            for rev in revenues:
                source = rev.get('source', 'unknown')
                by_source[source] = by_source.get(source, 0) + float(rev.get('amount', 0))
            
            # Daily breakdown
            daily_breakdown = {}
            for rev in revenues:
                date = rev.get('created_at', '')[:10]  # YYYY-MM-DD
                daily_breakdown[date] = daily_breakdown.get(date, 0) + float(rev.get('amount', 0))
            
            return {
                'total': round(total_revenue, 2),
                'period': period,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'currency': 'RON',
                'count': len(revenues),
                'average_per_transaction': round(total_revenue / len(revenues), 2) if revenues else 0,
                'by_source': by_source,
                'daily_breakdown': [
                    {'date': date, 'amount': round(amount, 2)}
                    for date, amount in sorted(daily_breakdown.items())
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting revenue summary: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_cost_breakdown(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        period: str = "30d"
    ) -> Dict[str, Any]:
        """REAL cost calculation from database"""
        try:
            # Calculate date range
            if not end_date:
                end_date = datetime.utcnow()
            if not start_date:
                if period == "7d":
                    start_date = end_date - timedelta(days=7)
                elif period == "30d":
                    start_date = end_date - timedelta(days=30)
                elif period == "90d":
                    start_date = end_date - timedelta(days=90)
                else:
                    start_date = end_date - timedelta(days=30)
            
            # Query API costs
            api_result = self.supabase.client.table('api_costs')\
                .select('*')\
                .gte('created_at', start_date.isoformat())\
                .lte('created_at', end_date.isoformat())\
                .execute()
            
            api_costs = api_result.data or []
            
            # Query financial transactions (costs)
            trans_result = self.supabase.client.table('financial_transactions')\
                .select('*')\
                .eq('type', 'cost')\
                .gte('transaction_date', start_date.isoformat())\
                .lte('transaction_date', end_date.isoformat())\
                .execute()
            
            transactions = trans_result.data or []
            
            # Calculate API costs by provider (in USD, convert to RON)
            USD_TO_RON = 4.95  # Exchange rate
            
            by_provider = {}
            for cost in api_costs:
                provider = cost.get('provider', 'unknown')
                amount_usd = float(cost.get('total_cost', 0))
                amount_ron = amount_usd * USD_TO_RON
                by_provider[provider] = by_provider.get(provider, 0) + amount_ron
            
            total_api_costs = sum(by_provider.values())
            
            # Calculate other costs by category
            by_category = {
                'api_costs': total_api_costs,
                'infrastructure': 0,
                'marketing': 0,
                'other': 0
            }
            
            for trans in transactions:
                category = trans.get('category', 'other')
                amount = float(trans.get('amount', 0))
                
                if 'infrastructure' in category.lower() or 'supabase' in category.lower() or 'cloudflare' in category.lower():
                    by_category['infrastructure'] += amount
                elif 'marketing' in category.lower() or 'ads' in category.lower():
                    by_category['marketing'] += amount
                else:
                    by_category['other'] += amount
            
            total_costs = sum(by_category.values())
            
            # Percentage breakdown
            percentages = {
                cat: round((amount / total_costs * 100), 2) if total_costs > 0 else 0
                for cat, amount in by_category.items()
            }
            
            return {
                'total': round(total_costs, 2),
                'period': period,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'currency': 'RON',
                'breakdown': {
                    cat: round(amount, 2)
                    for cat, amount in by_category.items()
                },
                'percentages': percentages,
                'api_costs_by_provider': {
                    provider: round(amount, 2)
                    for provider, amount in by_provider.items()
                },
                'api_cost_count': len(api_costs),
                'transaction_count': len(transactions)
            }
            
        except Exception as e:
            logger.error(f"Error getting cost breakdown: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_profit(
        self,
        period: str = "30d"
    ) -> Dict[str, Any]:
        """Calculate REAL profit (revenue - costs)"""
        try:
            # Get revenue and costs for same period
            revenue_data = await self.get_revenue_summary(period=period)
            cost_data = await self.get_cost_breakdown(period=period)
            
            total_revenue = revenue_data['total']
            total_costs = cost_data['total']
            profit = total_revenue - total_costs
            
            # Calculate margins
            profit_margin = (profit / total_revenue * 100) if total_revenue > 0 else 0
            roi = (profit / total_costs * 100) if total_costs > 0 else 0
            
            return {
                'period': period,
                'revenue': round(total_revenue, 2),
                'costs': round(total_costs, 2),
                'profit': round(profit, 2),
                'profit_margin_percent': round(profit_margin, 2),
                'roi_percent': round(roi, 2),
                'currency': 'RON',
                'is_profitable': profit > 0
            }
            
        except Exception as e:
            logger.error(f"Error calculating profit: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_dashboard_metrics(
        self,
        user_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """REAL dashboard financial metrics"""
        try:
            # Today's metrics
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = datetime.utcnow()
            
            # Today's revenue
            today_revenue = await self.get_revenue_summary(
                user_id=user_id,
                start_date=today_start,
                end_date=today_end
            )
            
            # This month's metrics
            month_start = today_start.replace(day=1)
            month_metrics = await self.get_profit(period="30d")
            
            # This week's metrics
            week_metrics = await self.get_profit(period="7d")
            
            return {
                'today': {
                    'revenue': today_revenue['total'],
                    'currency': 'RON'
                },
                'this_week': {
                    'revenue': week_metrics['revenue'],
                    'costs': week_metrics['costs'],
                    'profit': week_metrics['profit'],
                    'roi': week_metrics['roi_percent']
                },
                'this_month': {
                    'revenue': month_metrics['revenue'],
                    'costs': month_metrics['costs'],
                    'profit': month_metrics['profit'],
                    'profit_margin': month_metrics['profit_margin_percent'],
                    'roi': month_metrics['roi_percent']
                },
                'currency': 'RON',
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard metrics: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def export_financial_csv(
        self,
        user_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        type: Optional[str] = None
    ) -> str:
        """Export financial data to CSV"""
        try:
            if not end_date:
                end_date = datetime.utcnow()
            if not start_date:
                start_date = end_date - timedelta(days=90)
            
            # Get all transactions
            query = self.supabase.client.table('financial_transactions')\
                .select('*')\
                .gte('transaction_date', start_date.isoformat())\
                .lte('transaction_date', end_date.isoformat())
            
            if type:
                query = query.eq('type', type)
            
            result = query.order('transaction_date', desc=True).execute()
            transactions = result.data or []
            
            # Create CSV
            output = io.StringIO()
            fieldnames = [
                'date', 'type', 'category', 'amount', 'currency',
                'description', 'source'
            ]
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            for trans in transactions:
                writer.writerow({
                    'date': trans.get('transaction_date', '')[:10],
                    'type': trans.get('type', ''),
                    'category': trans.get('category', ''),
                    'amount': float(trans.get('amount', 0)),
                    'currency': trans.get('currency', 'RON'),
                    'description': trans.get('description', ''),
                    'source': trans.get('source', '')
                })
            
            logger.info(f"Exported {len(transactions)} financial transactions")
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Error exporting financial data: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

# Singleton
_financial_service = None

def get_financial_service() -> FinancialService:
    global _financial_service
    if _financial_service is None:
        _financial_service = FinancialService()
    return _financial_service
