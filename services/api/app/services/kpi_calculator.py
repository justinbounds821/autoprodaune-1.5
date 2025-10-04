"""
KPI Calculator - Serviciu pentru calcularea indicatorilor cheie de performanță
"""

import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
import math

# Configurează logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KPICategory(Enum):
    """Categoriile de KPI-uri"""
    FINANCIAL = "financial"
    MARKETING = "marketing"
    OPERATIONAL = "operational"
    CUSTOMER = "customer"
    TECHNICAL = "technical"

class KPIStatus(Enum):
    """Statusul unui KPI"""
    EXCELLENT = "excellent"
    GOOD = "good"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

@dataclass
class KPIValue:
    """Reprezentarea unei valori KPI"""
    name: str
    value: Union[int, float]
    target: Optional[Union[int, float]] = None
    previous_value: Optional[Union[int, float]] = None
    status: KPIStatus = KPIStatus.UNKNOWN
    category: KPICategory = KPICategory.OPERATIONAL
    unit: str = ""
    description: str = ""
    timestamp: datetime = None  # type: ignore
    trend: Optional[float] = None  # Procentaj de schimbare
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        
        # Calculează trend-ul dacă există valoarea anterioară
        if self.previous_value is not None and self.previous_value != 0:
            self.trend = ((self.value - self.previous_value) / self.previous_value) * 100
        elif self.previous_value == 0 and self.value > 0:
            self.trend = 100.0  # Creștere de la 0
        else:
            self.trend = 0.0

@dataclass
class KPIAnalysis:
    """Analiza unui KPI"""
    kpi: KPIValue
    benchmark: Optional[float] = None
    industry_average: Optional[float] = None
    recommendations: List[str] = None  # type: ignore
    alerts: List[str] = None  # type: ignore
    
    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []
        if self.alerts is None:
            self.alerts = []

class FinancialKPICalculator:
    """Calculator pentru KPI-uri financiare"""
    
    @staticmethod
    def calculate_roi(revenue: float, costs: float) -> KPIValue:
        """Calculează ROI (Return on Investment)"""
        roi = ((revenue - costs) / costs * 100) if costs > 0 else 0
        
        # Determină statusul pe baza valorii ROI
        if roi >= 200:
            status = KPIStatus.EXCELLENT
        elif roi >= 100:
            status = KPIStatus.GOOD
        elif roi >= 50:
            status = KPIStatus.WARNING
        else:
            status = KPIStatus.CRITICAL
        
        return KPIValue(
            name="ROI",
            value=roi,
            target=150.0,
            status=status,
            category=KPICategory.FINANCIAL,
            unit="%",
            description="Return on Investment - profitul generat pentru fiecare leu investit"
        )
    
    @staticmethod
    def calculate_cost_per_lead(total_costs: float, total_leads: int) -> KPIValue:
        """Calculează costul per lead"""
        cpl = total_costs / total_leads if total_leads > 0 else 0
        
        # Determină statusul pe baza costului per lead
        if cpl <= 10:
            status = KPIStatus.EXCELLENT
        elif cpl <= 20:
            status = KPIStatus.GOOD
        elif cpl <= 30:
            status = KPIStatus.WARNING
        else:
            status = KPIStatus.CRITICAL
        
        return KPIValue(
            name="Cost Per Lead",
            value=cpl,
            target=15.0,
            status=status,
            category=KPICategory.FINANCIAL,
            unit="RON",
            description="Costul mediu pentru obținerea unui lead"
        )
    
    @staticmethod
    def calculate_revenue_per_lead(total_revenue: float, total_leads: int) -> KPIValue:
        """Calculează venitul per lead"""
        rpl = total_revenue / total_leads if total_leads > 0 else 0
        
        # Determină statusul pe baza venitului per lead
        if rpl >= 50:
            status = KPIStatus.EXCELLENT
        elif rpl >= 30:
            status = KPIStatus.GOOD
        elif rpl >= 20:
            status = KPIStatus.WARNING
        else:
            status = KPIStatus.CRITICAL
        
        return KPIValue(
            name="Revenue Per Lead",
            value=rpl,
            target=40.0,
            status=status,
            category=KPICategory.FINANCIAL,
            unit="RON",
            description="Venitul mediu generat de un lead"
        )
    
    @staticmethod
    def calculate_net_profit_margin(revenue: float, costs: float) -> KPIValue:
        """Calculează marja de profit net"""
        margin = ((revenue - costs) / revenue * 100) if revenue > 0 else 0
        
        # Determină statusul pe baza marjei
        if margin >= 40:
            status = KPIStatus.EXCELLENT
        elif margin >= 25:
            status = KPIStatus.GOOD
        elif margin >= 15:
            status = KPIStatus.WARNING
        else:
            status = KPIStatus.CRITICAL
        
        return KPIValue(
            name="Net Profit Margin",
            value=margin,
            target=30.0,
            status=status,
            category=KPICategory.FINANCIAL,
            unit="%",
            description="Marja de profit net ca procent din venituri"
        )

class MarketingKPICalculator:
    """Calculator pentru KPI-uri de marketing"""
    
    @staticmethod
    def calculate_conversion_rate(conversions: int, total_visitors: int) -> KPIValue:
        """Calculează rata de conversie"""
        rate = (conversions / total_visitors * 100) if total_visitors > 0 else 0
        
        # Determină statusul pe baza ratei de conversie
        if rate >= 5:
            status = KPIStatus.EXCELLENT
        elif rate >= 3:
            status = KPIStatus.GOOD
        elif rate >= 1:
            status = KPIStatus.WARNING
        else:
            status = KPIStatus.CRITICAL
        
        return KPIValue(
            name="Conversion Rate",
            value=rate,
            target=4.0,
            status=status,
            category=KPICategory.MARKETING,
            unit="%",
            description="Procentul de vizitatori care se convertește în leads/clienți"
        )
    
    @staticmethod
    def calculate_engagement_rate(likes: int, comments: int, shares: int, followers: int) -> KPIValue:
        """Calculează rata de engagement"""
        total_engagement = likes + comments + shares
        rate = (total_engagement / followers * 100) if followers > 0 else 0
        
        # Determină statusul pe baza ratei de engagement
        if rate >= 8:
            status = KPIStatus.EXCELLENT
        elif rate >= 5:
            status = KPIStatus.GOOD
        elif rate >= 3:
            status = KPIStatus.WARNING
        else:
            status = KPIStatus.CRITICAL
        
        return KPIValue(
            name="Engagement Rate",
            value=rate,
            target=6.0,
            status=status,
            category=KPICategory.MARKETING,
            unit="%",
            description="Rata de engagement pe rețelele sociale"
        )
    
    @staticmethod
    def calculate_click_through_rate(clicks: int, impressions: int) -> KPIValue:
        """Calculează rata de click-through"""
        ctr = (clicks / impressions * 100) if impressions > 0 else 0
        
        # Determină statusul pe baza CTR
        if ctr >= 3:
            status = KPIStatus.EXCELLENT
        elif ctr >= 2:
            status = KPIStatus.GOOD
        elif ctr >= 1:
            status = KPIStatus.WARNING
        else:
            status = KPIStatus.CRITICAL
        
        return KPIValue(
            name="Click Through Rate",
            value=ctr,
            target=2.5,
            status=status,
            category=KPICategory.MARKETING,
            unit="%",
            description="Rata de click-through pentru anunțuri și postări"
        )

class OperationalKPICalculator:
    """Calculator pentru KPI-uri operaționale"""
    
    @staticmethod
    def calculate_response_time(response_times: List[float]) -> KPIValue:
        """Calculează timpul mediu de răspuns"""
        if not response_times:
            avg_time = 0
        else:
            avg_time = int(statistics.mean(response_times))
        
        # Determină statusul pe baza timpului de răspuns
        if avg_time <= 1:
            status = KPIStatus.EXCELLENT
        elif avg_time <= 2:
            status = KPIStatus.GOOD
        elif avg_time <= 5:
            status = KPIStatus.WARNING
        else:
            status = KPIStatus.CRITICAL
        
        return KPIValue(
            name="Average Response Time",
            value=avg_time,
            target=1.5,
            status=status,
            category=KPICategory.OPERATIONAL,
            unit="minutes",
            description="Timpul mediu de răspuns la întrebările clienților"
        )
    
    @staticmethod
    def calculate_success_rate(successful_operations: int, total_operations: int) -> KPIValue:
        """Calculează rata de succes"""
        rate = (successful_operations / total_operations * 100) if total_operations > 0 else 0
        
        # Determină statusul pe baza ratei de succes
        if rate >= 98:
            status = KPIStatus.EXCELLENT
        elif rate >= 95:
            status = KPIStatus.GOOD
        elif rate >= 90:
            status = KPIStatus.WARNING
        else:
            status = KPIStatus.CRITICAL
        
        return KPIValue(
            name="Success Rate",
            value=rate,
            target=96.0,
            status=status,
            category=KPICategory.OPERATIONAL,
            unit="%",
            description="Rata de succes a operațiunilor"
        )
    
    @staticmethod
    def calculate_uptime(downtime_minutes: float, total_minutes: float) -> KPIValue:
        """Calculează uptime-ul sistemului"""
        uptime = ((total_minutes - downtime_minutes) / total_minutes * 100) if total_minutes > 0 else 0
        
        # Determină statusul pe baza uptime-ului
        if uptime >= 99.9:
            status = KPIStatus.EXCELLENT
        elif uptime >= 99.5:
            status = KPIStatus.GOOD
        elif uptime >= 99.0:
            status = KPIStatus.WARNING
        else:
            status = KPIStatus.CRITICAL
        
        return KPIValue(
            name="System Uptime",
            value=uptime,
            target=99.7,
            status=status,
            category=KPICategory.OPERATIONAL,
            unit="%",
            description="Procentul de timp când sistemul este operațional"
        )

class CustomerKPICalculator:
    """Calculator pentru KPI-uri ale clienților"""
    
    @staticmethod
    def calculate_customer_satisfaction(satisfaction_scores: List[int]) -> KPIValue:
        """Calculează satisfacția clienților"""
        if not satisfaction_scores:
            avg_score = 0
        else:
            avg_score = int(statistics.mean(satisfaction_scores))
        
        # Determină statusul pe baza satisfacției
        if avg_score >= 4.5:
            status = KPIStatus.EXCELLENT
        elif avg_score >= 4.0:
            status = KPIStatus.GOOD
        elif avg_score >= 3.5:
            status = KPIStatus.WARNING
        else:
            status = KPIStatus.CRITICAL
        
        return KPIValue(
            name="Customer Satisfaction",
            value=avg_score,
            target=4.2,
            status=status,
            category=KPICategory.CUSTOMER,
            unit="/5",
            description="Satisfacția medie a clienților (scara 1-5)"
        )
    
    @staticmethod
    def calculate_customer_retention_rate(retained_customers: int, total_customers: int) -> KPIValue:
        """Calculează rata de retenție a clienților"""
        rate = (retained_customers / total_customers * 100) if total_customers > 0 else 0
        
        # Determină statusul pe baza ratei de retenție
        if rate >= 85:
            status = KPIStatus.EXCELLENT
        elif rate >= 75:
            status = KPIStatus.GOOD
        elif rate >= 65:
            status = KPIStatus.WARNING
        else:
            status = KPIStatus.CRITICAL
        
        return KPIValue(
            name="Customer Retention Rate",
            value=rate,
            target=80.0,
            status=status,
            category=KPICategory.CUSTOMER,
            unit="%",
            description="Procentul de clienți care rămân activi"
        )

class KPICalculator:
    """Calculator principal pentru KPI-uri"""
    
    def __init__(self):
        self.financial = FinancialKPICalculator()
        self.marketing = MarketingKPICalculator()
        self.operational = OperationalKPICalculator()
        self.customer = CustomerKPICalculator()
    
    def calculate_all_kpis(self, data: Dict[str, Any]) -> List[KPIValue]:
        """
        Calculează toate KPI-urile pe baza datelor furnizate
        
        Args:
            data: Dicționar cu datele pentru calcularea KPI-urilor
            
        Returns:
            Lista cu toate KPI-urile calculate
        """
        kpis = []
        
        try:
            # KPI-uri financiare
            if "revenue" in data and "costs" in data:
                kpis.append(self.financial.calculate_roi(data["revenue"], data["costs"]))
                kpis.append(self.financial.calculate_net_profit_margin(data["revenue"], data["costs"]))
            
            if "total_costs" in data and "total_leads" in data:
                kpis.append(self.financial.calculate_cost_per_lead(data["total_costs"], data["total_leads"]))
            
            if "total_revenue" in data and "total_leads" in data:
                kpis.append(self.financial.calculate_revenue_per_lead(data["total_revenue"], data["total_leads"]))
            
            # KPI-uri de marketing
            if "conversions" in data and "total_visitors" in data:
                kpis.append(self.marketing.calculate_conversion_rate(data["conversions"], data["total_visitors"]))
            
            if "clicks" in data and "impressions" in data:
                kpis.append(self.marketing.calculate_click_through_rate(data["clicks"], data["impressions"]))
            
            if all(key in data for key in ["likes", "comments", "shares", "followers"]):
                kpis.append(self.marketing.calculate_engagement_rate(
                    data["likes"], data["comments"], data["shares"], data["followers"]
                ))
            
            # KPI-uri operaționale
            if "response_times" in data:
                kpis.append(self.operational.calculate_response_time(data["response_times"]))
            
            if "successful_operations" in data and "total_operations" in data:
                kpis.append(self.operational.calculate_success_rate(
                    data["successful_operations"], data["total_operations"]
                ))
            
            if "downtime_minutes" in data and "total_minutes" in data:
                kpis.append(self.operational.calculate_uptime(
                    data["downtime_minutes"], data["total_minutes"]
                ))
            
            # KPI-uri ale clienților
            if "satisfaction_scores" in data:
                kpis.append(self.customer.calculate_customer_satisfaction(data["satisfaction_scores"]))
            
            if "retained_customers" in data and "total_customers" in data:
                kpis.append(self.customer.calculate_customer_retention_rate(
                    data["retained_customers"], data["total_customers"]
                ))
            
            logger.info(f"Calculate {len(kpis)} KPI-uri")
            
        except Exception as e:
            logger.error(f"Eroare la calcularea KPI-urilor: {str(e)}")
        
        return kpis
    
    def analyze_kpi(self, kpi: KPIValue) -> KPIAnalysis:
        """
        Analizează un KPI și oferă recomandări
        
        Args:
            kpi: KPI-ul de analizat
            
        Returns:
            KPIAnalysis cu analiza și recomandările
        """
        analysis = KPIAnalysis(kpi=kpi)
        
        # Adaugă recomandări bazate pe status
        if kpi.status == KPIStatus.CRITICAL:
            analysis.alerts.append(f"⚠️ {kpi.name} este în stare critică!")
            analysis.recommendations.append(f"Urgent: Îmbunătățește {kpi.name} pentru a atinge targetul de {kpi.target}")
        elif kpi.status == KPIStatus.WARNING:
            analysis.alerts.append(f"⚠️ {kpi.name} necesită atenție")
            analysis.recommendations.append(f"Monitorizează {kpi.name} și ia măsuri preventive")
        elif kpi.status == KPIStatus.GOOD:
            analysis.recommendations.append(f"✅ {kpi.name} este în stare bună, menține performanța")
        elif kpi.status == KPIStatus.EXCELLENT:
            analysis.recommendations.append(f"🎉 {kpi.name} este excelent! Poți lua în considerare să crești targetul")
        
        # Adaugă recomandări bazate pe trend
        if kpi.trend is not None:
            if kpi.trend > 10:
                analysis.recommendations.append(f"📈 {kpi.name} crește cu {kpi.trend:.1f}% - continuă strategia actuală")
            elif kpi.trend < -10:
                analysis.alerts.append(f"📉 {kpi.name} scade cu {abs(kpi.trend):.1f}% - investighează cauzele")
        
        return analysis
    
    def get_kpis_by_category(self, kpis: List[KPIValue], category: KPICategory) -> List[KPIValue]:
        """Returnează KPI-urile dintr-o categorie specifică"""
        return [kpi for kpi in kpis if kpi.category == category]
    
    def get_kpis_by_status(self, kpis: List[KPIValue], status: KPIStatus) -> List[KPIValue]:
        """Returnează KPI-urile cu un status specific"""
        return [kpi for kpi in kpis if kpi.status == status]
    
    def get_critical_kpis(self, kpis: List[KPIValue]) -> List[KPIValue]:
        """Returnează KPI-urile critice"""
        return self.get_kpis_by_status(kpis, KPIStatus.CRITICAL)
    
    def get_warning_kpis(self, kpis: List[KPIValue]) -> List[KPIValue]:
        """Returnează KPI-urile cu avertismente"""
        return self.get_kpis_by_status(kpis, KPIStatus.WARNING)

# Singleton instance
_kpi_calculator = None

def get_kpi_calculator() -> KPICalculator:
    """Returnează instanța singleton a KPICalculator"""
    global _kpi_calculator
    if _kpi_calculator is None:
        _kpi_calculator = KPICalculator()
    return _kpi_calculator

# Funcții helper pentru calcularea rapidă
def calculate_financial_kpis(revenue: float, costs: float, leads: int) -> List[KPIValue]:
    """
    Funcție helper pentru calcularea KPI-urilor financiare
    
    Args:
        revenue: Venitul total
        costs: Costurile totale
        leads: Numărul total de leads
        
    Returns:
        Lista cu KPI-urile financiare
    """
    calculator = get_kpi_calculator()
    data = {
        "revenue": revenue,
        "costs": costs,
        "total_revenue": revenue,
        "total_costs": costs,
        "total_leads": leads
    }
    
    financial_kpis = calculator.get_kpis_by_category(
        calculator.calculate_all_kpis(data), 
        KPICategory.FINANCIAL
    )
    
    return financial_kpis

def calculate_marketing_kpis(
    conversions: int, 
    visitors: int, 
    likes: int, 
    comments: int, 
    shares: int, 
    followers: int
) -> List[KPIValue]:
    """
    Funcție helper pentru calcularea KPI-urilor de marketing
    
    Returns:
        Lista cu KPI-urile de marketing
    """
    calculator = get_kpi_calculator()
    data = {
        "conversions": conversions,
        "total_visitors": visitors,
        "likes": likes,
        "comments": comments,
        "shares": shares,
        "followers": followers
    }
    
    marketing_kpis = calculator.get_kpis_by_category(
        calculator.calculate_all_kpis(data), 
        KPICategory.MARKETING
    )
    
    return marketing_kpis
