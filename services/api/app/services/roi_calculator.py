"""
Serviciu pentru calcularea ROI și analiza profitabilității - AutoPro Daune.

Acest modul implementează serviciul pentru calcularea ROI-ului,
analiza profitabilității și optimizarea investițiilor.
"""

import logging
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
from dataclasses import dataclass

from ..models.financial import FinancialMetrics, CampaignMetrics
from ..schemas.financial import ROIAnalysisResponse, ProfitLossResponse

@dataclass
class ROIData:
    """Data class pentru rezultatele analizei ROI."""
    period: str
    roi_percentage: Decimal
    total_revenue: Decimal
    total_costs: Decimal
    net_profit: Decimal
    cost_breakdown: Dict[str, Decimal]
    revenue_breakdown: Dict[str, Decimal]


class ROIMethod(Enum):
    """Metode de calculare ROI."""
    SIMPLE = "simple"
    ANNUALIZED = "annualized"
    COMPOUND = "compound"


class ROICalculator:
    """
    Serviciu pentru calcularea ROI și analiza profitabilității.
    
    Acest serviciu oferă funcționalități pentru:
    - Calcularea ROI-ului pentru diverse perioade
    - Analiza profitabilității campaniilor
    - Compararea performanței între diferite investiții
    - Optimizarea alocării bugetului
    """
    
    def __init__(self):
        """Inițializează ROICalculator."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.precision = 4  # Precizia pentru calculele cu Decimal
    
    # ==================== CALCULARE ROI ====================
    
    def calculate_roi(
        self, 
        investment: Decimal, 
        return_value: Decimal, 
        method: ROIMethod = ROIMethod.SIMPLE
    ) -> Dict[str, Any]:
        """
        Calculează ROI-ul pentru o investiție.
        
        Args:
            investment: Suma investită
            return_value: Valoarea returnată
            method: Metoda de calculare
            
        Returns:
            Dicționar cu rezultatul calculului
            
        Raises:
            ValueError: Dacă parametrii sunt invalizi
        """
        try:
            if investment <= 0:
                raise ValueError("Investiția trebuie să fie pozitivă")
            
            if return_value < 0:
                raise ValueError("Valoarea returnată nu poate fi negativă")
            
            # Calculează profitul net
            net_profit = return_value - investment
            
            # Calculează ROI-ul în funcție de metodă
            if method == ROIMethod.SIMPLE:
                roi_percentage = (net_profit / investment) * 100
            elif method == ROIMethod.ANNUALIZED:
                # ROI anualizat (presupunem 365 zile)
                roi_percentage = (net_profit / investment) * 100
            else:  # COMPOUND
                # ROI compus
                roi_percentage = (float(return_value / investment) ** (1/1) - 1) * 100
                roi_percentage = Decimal(str(roi_percentage))
            
            # Calculează metrici suplimentare
            roi_ratio = net_profit / investment
            payback_period = self._calculate_payback_period(investment, net_profit)
            
            return {
                "investment": investment,
                "return_value": return_value,
                "net_profit": net_profit,
                "roi_percentage": round(roi_percentage, self.precision),
                "roi_ratio": round(roi_ratio, self.precision),
                "payback_period_days": payback_period,
                "method": method.value,
                "calculation_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Eroare la calcularea ROI: {e}")
            raise
    
    def calculate_campaign_roi(
        self, 
        campaign_data: CampaignMetrics
    ) -> Dict[str, Any]:
        """
        Calculează ROI-ul pentru o campanie specifică.
        
        Args:
            campaign_data: Datele campaniei
            
        Returns:
            Dicționar cu ROI-ul campaniei
        """
        try:
            # Calculează ROI-ul de bază
            base_roi = self.calculate_roi(
                campaign_data.total_spend, 
                campaign_data.total_revenue
            )
            
            # Calculează metrici suplimentare pentru campanie
            cost_per_lead = campaign_data.total_spend / max(campaign_data.leads_generated, 1)
            cost_per_conversion = campaign_data.total_spend / max(campaign_data.conversions, 1)
            conversion_rate = (campaign_data.conversions / max(campaign_data.leads_generated, 1)) * 100
            
            # Calculează durata campaniei
            start_date = campaign_data.start_date
            end_date = campaign_data.end_date or date.today()
            campaign_duration = (end_date - start_date).days
            
            # Calculează ROI zilnic
            daily_roi = base_roi["roi_percentage"] / max(campaign_duration, 1)
            
            return {
                **base_roi,
                "campaign_name": campaign_data.campaign_name,
                "campaign_type": campaign_data.campaign_type.value,
                "campaign_duration_days": campaign_duration,
                "daily_roi": round(daily_roi, self.precision),
                "cost_per_lead": round(cost_per_lead, self.precision),
                "cost_per_conversion": round(cost_per_conversion, self.precision),
                "conversion_rate": round(conversion_rate, self.precision),
                "leads_generated": campaign_data.leads_generated,
                "conversions": campaign_data.conversions
            }
            
        except Exception as e:
            self.logger.error(f"Eroare la calcularea ROI campanie: {e}")
            raise
    
    def calculate_period_roi(
        self, 
        start_date: date, 
        end_date: date,
        financial_metrics: List[FinancialMetrics]
    ) -> ROIAnalysisResponse:
        """
        Calculează ROI-ul pentru o perioadă specificată.
        
        Args:
            start_date: Data de început
            end_date: Data de sfârșit
            financial_metrics: Lista cu metricile financiare
            
        Returns:
            Obiect ROIAnalysisResponse cu rezultatul
        """
        try:
            # Filtrează metricile pentru perioada specificată
            period_metrics = [
                m for m in financial_metrics 
                if start_date <= m.date <= end_date
            ]
            
            if not period_metrics:
                return ROIAnalysisResponse(
                    period=f"{start_date} to {end_date}",
                    roi_percentage=Decimal('0.00'),
                    total_revenue=Decimal('0.00'),
                    total_costs=Decimal('0.00'),
                    net_profit=Decimal('0.00')
                )
            
            # Calculează totalurile
            total_costs = sum(m.total_costs for m in period_metrics)
            total_revenue = sum(m.total_revenue for m in period_metrics)
            net_profit = total_revenue - total_costs
            
            # Calculează ROI-ul
            roi_percentage = Decimal('0.00')
            if total_costs > 0:
                roi_percentage = (net_profit / total_costs) * 100
            
            return ROIData(
                period=f"{start_date} to {end_date}",
                roi_percentage=round(roi_percentage, self.precision),
                total_revenue=round(total_revenue, self.precision),
                total_costs=round(total_costs, self.precision),
                net_profit=round(net_profit, self.precision)
            )
            
        except Exception as e:
            self.logger.error(f"Eroare la calcularea ROI perioadă: {e}")
            raise
    
    # ==================== ANALIZA PROFITABILITĂȚII ====================
    
    def analyze_profitability(
        self, 
        financial_metrics: List[FinancialMetrics],
        period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Analizează profitabilitatea pentru o perioadă specificată.
        
        Args:
            financial_metrics: Lista cu metricile financiare
            period_days: Perioada în zile
            
        Returns:
            Dicționar cu analiza profitabilității
        """
        try:
            if not financial_metrics:
                return self._empty_profitability_analysis()
            
            # Sortează metricile după dată
            sorted_metrics = sorted(financial_metrics, key=lambda x: x.date)
            
            # Analizează perioada specificată
            end_date = date.today()
            start_date = end_date - timedelta(days=period_days)
            
            period_metrics = [
                m for m in sorted_metrics 
                if start_date <= m.date <= end_date
            ]
            
            if not period_metrics:
                return self._empty_profitability_analysis()
            
            # Calculează metrici de bază
            total_costs = sum(m.total_costs for m in period_metrics)
            total_revenue = sum(m.total_revenue for m in period_metrics)
            net_profit = total_revenue - total_costs
            
            # Calculează ROI-ul
            roi_percentage = Decimal('0.00')
            if total_costs > 0:
                roi_percentage = (net_profit / total_costs) * 100
            
            # Analizează tendințele
            trends = self._analyze_trends(period_metrics)
            
            # Calculează metrici de performanță
            performance_metrics = self._calculate_performance_metrics(period_metrics)
            
            return {
                "period_days": period_days,
                "start_date": start_date,
                "end_date": end_date,
                "total_costs": round(total_costs, self.precision),
                "total_revenue": round(total_revenue, self.precision),
                "net_profit": round(net_profit, self.precision),
                "roi_percentage": round(roi_percentage, self.precision),
                "trends": trends,
                "performance_metrics": performance_metrics,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Eroare la analiza profitabilității: {e}")
            raise
    
    def compare_campaigns(
        self, 
        campaigns: List[CampaignMetrics]
    ) -> Dict[str, Any]:
        """
        Compară performanța mai multor campanii.
        
        Args:
            campaigns: Lista cu campaniile de comparat
            
        Returns:
            Dicționar cu comparația
        """
        try:
            if not campaigns:
                return {"error": "Nu există campanii de comparat"}
            
            # Calculează ROI-ul pentru fiecare campanie
            campaign_rois = []
            for campaign in campaigns:
                roi_data = self.calculate_campaign_roi(campaign)
                campaign_rois.append(roi_data)
            
            # Sortează după ROI
            campaign_rois.sort(key=lambda x: x["roi_percentage"], reverse=True)
            
            # Calculează statistici
            rois = [roi["roi_percentage"] for roi in campaign_rois]
            avg_roi = sum(rois) / len(rois)
            best_roi = max(rois)
            worst_roi = min(rois)
            
            # Identifică campania cea mai profitabilă
            best_campaign = campaign_rois[0]
            
            return {
                "total_campaigns": len(campaigns),
                "average_roi": round(avg_roi, self.precision),
                "best_roi": round(best_roi, self.precision),
                "worst_roi": round(worst_roi, self.precision),
                "best_campaign": best_campaign,
                "campaign_rankings": campaign_rois,
                "comparison_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Eroare la compararea campaniilor: {e}")
            raise
    
    # ==================== OPTIMIZARE BUGET ====================
    
    def optimize_budget_allocation(
        self, 
        total_budget: Decimal,
        campaign_performance: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Optimizează alocarea bugetului bazată pe performanța campaniilor.
        
        Args:
            total_budget: Bugetul total disponibil
            campaign_performance: Lista cu performanța campaniilor
            
        Returns:
            Dicționar cu alocarea optimizată
        """
        try:
            if total_budget <= 0:
                raise ValueError("Bugetul trebuie să fie pozitiv")
            
            if not campaign_performance:
                return {"error": "Nu există date de performanță"}
            
            # Sortează campaniile după ROI
            sorted_campaigns = sorted(
                campaign_performance, 
                key=lambda x: x.get("roi_percentage", 0), 
                reverse=True
            )
            
            # Alocă bugetul proporțional cu ROI-ul
            total_roi = sum(campaign.get("roi_percentage", 0) for campaign in sorted_campaigns)
            
            if total_roi <= 0:
                # Dacă toate campaniile au ROI negativ, distribuie uniform
                allocation = total_budget / len(sorted_campaigns)
                return {
                    "allocation_method": "uniform",
                    "total_budget": total_budget,
                    "allocations": [
                        {
                            "campaign_name": campaign["campaign_name"],
                            "allocated_budget": round(allocation, self.precision),
                            "allocation_percentage": round(100 / len(sorted_campaigns), 2)
                        }
                        for campaign in sorted_campaigns
                    ]
                }
            
            # Alocă proporțional cu ROI-ul
            allocations = []
            for campaign in sorted_campaigns:
                roi_percentage = campaign.get("roi_percentage", 0)
                allocation_percentage = (roi_percentage / total_roi) * 100
                allocated_budget = total_budget * (allocation_percentage / 100)
                
                allocations.append({
                    "campaign_name": campaign["campaign_name"],
                    "allocated_budget": round(allocated_budget, self.precision),
                    "allocation_percentage": round(allocation_percentage, 2),
                    "roi_percentage": roi_percentage
                })
            
            return {
                "allocation_method": "roi_based",
                "total_budget": total_budget,
                "allocations": allocations,
                "optimization_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Eroare la optimizarea bugetului: {e}")
            raise
    
    # ==================== METODE PRIVATE ====================
    
    def _calculate_payback_period(
        self, 
        investment: Decimal, 
        net_profit: Decimal
    ) -> Optional[int]:
        """
        Calculează perioada de rambursare în zile.
        
        Args:
            investment: Investiția inițială
            net_profit: Profitul net zilnic estimat
            
        Returns:
            Perioada de rambursare în zile sau None dacă nu e aplicabil
        """
        if net_profit <= 0:
            return None
        
        # Presupunem că profitul net este zilnic
        return int(investment / net_profit)
    
    def _empty_profitability_analysis(self) -> Dict[str, Any]:
        """Returnează o analiză goală de profitabilitate."""
        return {
            "period_days": 0,
            "start_date": None,
            "end_date": None,
            "total_costs": Decimal('0.00'),
            "total_revenue": Decimal('0.00'),
            "net_profit": Decimal('0.00'),
            "roi_percentage": Decimal('0.00'),
            "trends": {},
            "performance_metrics": {},
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def _analyze_trends(self, metrics: List[FinancialMetrics]) -> Dict[str, Any]:
        """Analizează tendințele în metricile financiare."""
        if len(metrics) < 2:
            return {"trend": "insufficient_data"}
        
        # Calculează tendința pentru costuri
        costs = [m.total_costs for m in metrics]
        revenues = [m.total_revenue for m in metrics]
        
        cost_trend = "stable"
        if len(costs) >= 2:
            if costs[-1] > costs[0] * Decimal('1.1'):
                cost_trend = "increasing"
            elif costs[-1] < costs[0] * Decimal('0.9'):
                cost_trend = "decreasing"
        
        revenue_trend = "stable"
        if len(revenues) >= 2:
            if revenues[-1] > revenues[0] * Decimal('1.1'):
                revenue_trend = "increasing"
            elif revenues[-1] < revenues[0] * Decimal('0.9'):
                revenue_trend = "decreasing"
        
        return {
            "cost_trend": cost_trend,
            "revenue_trend": revenue_trend,
            "data_points": len(metrics)
        }
    
    def _calculate_performance_metrics(
        self, 
        metrics: List[FinancialMetrics]
    ) -> Dict[str, Any]:
        """Calculează metrici de performanță."""
        if not metrics:
            return {}
        
        rois = [m.roi_percentage for m in metrics if m.roi_percentage is not None]
        
        if not rois:
            return {"error": "Nu există date ROI"}
        
        return {
            "average_roi": round(sum(rois) / len(rois), self.precision),
            "max_roi": round(max(rois), self.precision),
            "min_roi": round(min(rois), self.precision),
            "roi_volatility": round(max(rois) - min(rois), self.precision),
            "positive_roi_days": sum(1 for roi in rois if roi > 0),
            "total_days": len(rois)
        }


def get_roi_calculator() -> "ROICalculator":
    """Factory function that returns a ``ROICalculator`` instance."""
    return ROICalculator()
