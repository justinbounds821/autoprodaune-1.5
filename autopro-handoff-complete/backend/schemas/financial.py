"""
Scheme Pydantic pentru validarea datelor financiare.

Acest modul definește schemele pentru validarea și serializarea datelor
pentru endpoint-urile API financiare.
"""

from datetime import datetime, date as Date
from decimal import Decimal
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator, model_validator


# ==================== SCHEME DE BAZĂ ====================

class APICostCreate(BaseModel):
    """Schema pentru crearea unei înregistrări de cost API."""
    provider: str = Field(..., min_length=1, max_length=50, description="Providerul API (ex: Pika, HeyGen)")
    operation: str = Field(..., min_length=1, max_length=100, description="Operația efectuată")
    cost: Decimal = Field(..., gt=0, decimal_places=2, description="Costul în dolari")
    credits_used: Optional[int] = Field(None, ge=0, description="Creditele consumate")
    currency: str = Field("USD", max_length=3, description="Moneda (default USD)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata suplimentară")
    
    @validator('currency')
    def validate_currency(cls, v):
        """Validează că moneda este suportată."""
        supported_currencies = ['USD', 'EUR', 'RON']
        if v.upper() not in supported_currencies:
            raise ValueError(f'Moneda {v} nu este suportată. Monede suportate: {supported_currencies}')
        return v.upper()


class APICostResponse(BaseModel):
    """Schema pentru răspunsul cu date despre cost API."""
    id: int
    provider: str
    operation: str
    cost: Decimal
    credits_used: Optional[int]
    currency: str
    metadata: Optional[Dict[str, Any]]
    timestamp: datetime
    
    class Config:
        from_attributes = True


class RevenueCreate(BaseModel):
    """Schema pentru crearea unei înregistrări de venit."""
    source: str = Field(..., min_length=1, max_length=50, description="Sursa venitului")
    amount: Decimal = Field(..., gt=0, decimal_places=2, description="Suma în dolari")
    lead_id: Optional[int] = Field(None, ge=1, description="ID-ul lead-ului asociat")
    conversion_type: Optional[str] = Field(None, max_length=50, description="Tipul conversiei")
    currency: str = Field("USD", max_length=3, description="Moneda (default USD)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata suplimentară")
    
    @validator('currency')
    def validate_currency(cls, v):
        """Validează că moneda este suportată."""
        supported_currencies = ['USD', 'EUR', 'RON']
        if v.upper() not in supported_currencies:
            raise ValueError(f'Moneda {v} nu este suportată. Monede suportate: {supported_currencies}')
        return v.upper()


class RevenueResponse(BaseModel):
    """Schema pentru răspunsul cu date despre venit."""
    id: int
    source: str
    amount: Decimal
    lead_id: Optional[int]
    conversion_type: Optional[str]
    currency: str
    metadata: Optional[Dict[str, Any]]
    timestamp: datetime
    
    class Config:
        from_attributes = True


# ==================== SCHEME PENTRU METRICI FINANCIARE ====================

class FinancialMetricsResponse(BaseModel):
    """Schema pentru răspunsul cu metrici financiare."""
    id: int
    date: Date
    
    # Costuri
    total_costs: Decimal
    api_costs: Decimal
    advertising_costs: Decimal
    other_costs: Decimal
    
    # Venituri
    total_revenue: Decimal
    lead_conversion_revenue: Decimal
    referral_revenue: Decimal
    other_revenue: Decimal
    
    # Metrici calculate
    net_profit: Decimal
    roi_percentage: Decimal
    
    # Contoare
    total_leads: int
    converted_leads: int
    total_referrals: int
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FinancialMetricsCreate(BaseModel):
    """Schema pentru crearea metricilor financiare (folosit pentru calcul automat)."""
    date: Date = Field(..., description="Data pentru care se calculează metricile")
    
    @validator('date')
    def validate_date(cls, v):
        """Validează că data nu este în viitor."""
        if v > Date.today():
            raise ValueError('Data nu poate fi în viitor')
        return v


# ==================== SCHEME PENTRU CAMPANII ====================

class CampaignMetricsCreate(BaseModel):
    """Schema pentru crearea metricilor de campanie."""
    campaign_name: str = Field(..., min_length=1, max_length=100, description="Numele campaniei")
    platform: str = Field(..., min_length=1, max_length=50, description="Platforma (ex: TikTok, Instagram)")
    period_start: Date = Field(..., description="Începutul perioadei")
    period_end: Date = Field(..., description="Sfârșitul perioadei")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata suplimentară")
    
    @model_validator(mode='after')
    def validate_period(self):
        """Validează că perioada este logică."""
        if self.period_start and self.period_end and self.period_start > self.period_end:
            raise ValueError('Data de început trebuie să fie înainte de data de sfârșit')
        
        if self.period_end and self.period_end > Date.today():
            raise ValueError('Data de sfârșit nu poate fi în viitor')
        
        return self


class CampaignMetricsResponse(BaseModel):
    """Schema pentru răspunsul cu metrici de campanie."""
    id: int
    campaign_name: str
    platform: str
    period_start: Date
    period_end: Date
    
    # Metrici de cost
    total_spent: Decimal
    cost_per_lead: Decimal
    cost_per_conversion: Decimal
    
    # Metrici de performanță
    total_leads: int
    total_conversions: int
    conversion_rate: Decimal
    
    # Metrici de engagement
    total_views: int
    total_likes: int
    total_shares: int
    engagement_rate: Decimal
    
    # ROI și profit
    total_revenue: Decimal
    net_profit: Decimal
    roi_percentage: Decimal
    
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== SCHEME PENTRU CREDITE ====================

class CreditBalanceResponse(BaseModel):
    """Schema pentru răspunsul cu soldul creditelor."""
    id: int
    provider: str
    credit_type: str
    current_balance: Decimal
    total_allocated: Decimal
    last_updated: datetime
    
    # Proprietăți calculate
    usage_percentage: Optional[Decimal] = None
    remaining_credits: Optional[Decimal] = None
    
    class Config:
        from_attributes = True


class CreditBalanceUpdate(BaseModel):
    """Schema pentru actualizarea soldului creditelor."""
    current_balance: Decimal = Field(..., ge=0, decimal_places=2, description="Soldul curent")
    credit_type: Optional[str] = Field(None, max_length=50, description="Tipul creditului")


# ==================== SCHEME PENTRU ALERTE ====================

class BudgetAlertCreate(BaseModel):
    """Schema pentru crearea unei alerte de buget."""
    alert_name: str = Field(..., min_length=1, max_length=100, description="Numele alertei")
    alert_type: str = Field(..., min_length=1, max_length=50, description="Tipul alertei")
    threshold_value: Decimal = Field(..., decimal_places=2, description="Valoarea pragului")
    message: Optional[str] = Field(None, description="Mesajul alertei")
    is_active: bool = Field(True, description="Dacă alerta este activă")
    
    @validator('alert_type')
    def validate_alert_type(cls, v):
        """Validează tipul alertei."""
        valid_types = [
            'budget_exceeded', 'negative_roi', 'low_credits',
            'high_cost_per_lead', 'low_conversion_rate'
        ]
        if v not in valid_types:
            raise ValueError(f'Tip alerte invalid: {v}. Tipuri valide: {valid_types}')
        return v


class BudgetAlertResponse(BaseModel):
    """Schema pentru răspunsul cu date despre alertă."""
    id: int
    alert_name: str
    alert_type: str
    threshold_value: Decimal
    current_value: Decimal
    is_triggered: bool
    is_active: bool
    message: Optional[str]
    notification_sent: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== SCHEME PENTRU DASHBOARD ====================

class FinancialDashboardResponse(BaseModel):
    """Schema pentru răspunsul cu datele dashboard-ului financiar."""
    # Metrici zilnice
    today_costs: Decimal
    today_revenue: Decimal
    today_profit: Decimal
    today_roi: Decimal
    
    # Metrici săptămânale
    weekly_costs: Decimal
    weekly_revenue: Decimal
    weekly_profit: Decimal
    weekly_roi: Decimal
    
    # Metrici lunare
    monthly_costs: Decimal
    monthly_revenue: Decimal
    monthly_profit: Decimal
    monthly_roi: Decimal
    
    # Trend-uri
    cost_trend: str  # "up", "down", "stable"
    revenue_trend: str
    profit_trend: str
    
    # Alerte active
    active_alerts: List[BudgetAlertResponse]
    
    # Top costuri
    top_cost_providers: List[Dict[str, Any]]
    
    # Top surse de venit
    top_revenue_sources: List[Dict[str, Any]]


class ROIAnalysisRequest(BaseModel):
    """Schema pentru cererea de analiză ROI."""
    period: str = Field(..., description="Perioada pentru analiză: '7d', '30d', '90d', 'all'")
    start_date: Optional[Date] = Field(None, description="Data de început (opțional)")
    end_date: Optional[Date] = Field(None, description="Data de sfârșit (opțional)")
    
    @validator('period')
    def validate_period(cls, v):
        """Validează perioada."""
        valid_periods = ['7d', '30d', '90d', 'all']
        if v not in valid_periods:
            raise ValueError(f'Perioada invalidă: {v}. Perioade valide: {valid_periods}')
        return v
    
    @model_validator(mode='after')
    def validate_dates(self):
        """Validează datele."""
        if self.period == 'all' and (self.start_date or self.end_date):
            raise ValueError('Pentru perioada "all" nu trebuie specificate date')
        
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError('Data de început trebuie să fie înainte de data de sfârșit')
        
        return self


class ROIAnalysisResponse(BaseModel):
    """Schema pentru răspunsul cu analiza ROI."""
    period: str
    start_date: Optional[Date]
    end_date: Optional[Date]
    
    # Metrici totale
    total_costs: Decimal
    total_revenue: Decimal
    net_profit: Decimal
    roi_percentage: Decimal
    
    # Metrici detaliate
    cost_breakdown: Dict[str, Decimal]
    revenue_breakdown: Dict[str, Decimal]
    
    # Comparații cu perioada anterioară
    cost_change_percentage: Decimal
    revenue_change_percentage: Decimal
    profit_change_percentage: Decimal
    roi_change_percentage: Decimal
    
    # Recomandări
    recommendations: List[str]


class ProfitLossRequest(BaseModel):
    """Schema pentru cererea de analiză profit/pierdere."""
    start_date: Date = Field(..., description="Data de început")
    end_date: Date = Field(..., description="Data de sfârșit")
    
    @validator('start_date', 'end_date')
    def validate_dates(cls, v):
        """Validează datele."""
        if v > Date.today():
            raise ValueError('Datele nu pot fi în viitor')
        return v
    
    @model_validator(mode='after')
    def validate_period(self):
        """Validează perioada."""
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError('Data de început trebuie să fie înainte de data de sfârșit')
        
        return self


class ProfitLossResponse(BaseModel):
    """Schema pentru răspunsul cu analiza profit/pierdere."""
    start_date: Date
    end_date: Date
    
    # Totale
    total_costs: Decimal
    total_revenue: Decimal
    net_profit: Decimal
    roi_percentage: Decimal
    
    # Breakdown zilnic
    daily_metrics: List[Dict[str, Any]]
    
    # Breakdown pe categorii
    cost_categories: Dict[str, Decimal]
    revenue_categories: Dict[str, Decimal]
    
    # Statistici
    avg_daily_profit: Decimal
    best_day_profit: Decimal
    worst_day_profit: Decimal
    profit_volatility: Decimal


# ==================== SCHEME PENTRU BULK OPERATIONS ====================

class BulkAPICostCreate(BaseModel):
    """Schema pentru crearea în masă a costurilor API."""
    costs: List[APICostCreate] = Field(..., min_items=1, max_items=100, description="Lista de costuri")
    
    @validator('costs')
    def validate_costs_list(cls, v):
        """Validează lista de costuri."""
        if not v:
            raise ValueError('Lista de costuri nu poate fi goală')
        return v


class BulkRevenueCreate(BaseModel):
    """Schema pentru crearea în masă a veniturilor."""
    revenues: List[RevenueCreate] = Field(..., min_items=1, max_items=100, description="Lista de venituri")
    
    @validator('revenues')
    def validate_revenues_list(cls, v):
        """Validează lista de venituri."""
        if not v:
            raise ValueError('Lista de venituri nu poate fi goală')
        return v


# ==================== SCHEME PENTRU STATISTICI ====================

class FinancialStatsResponse(BaseModel):
    """Schema pentru răspunsul cu statistici financiare."""
    # Statistici generale
    total_api_costs: Decimal
    total_revenue: Decimal
    total_profit: Decimal
    overall_roi: Decimal
    
    # Statistici pe provideri
    provider_stats: Dict[str, Dict[str, Any]]
    
    # Statistici pe surse de venit
    revenue_source_stats: Dict[str, Dict[str, Any]]
    
    # Top performeri
    top_performing_campaigns: List[Dict[str, Any]]
    most_costly_operations: List[Dict[str, Any]]
    
    # Trend-uri
    monthly_trends: Dict[str, Any]
    weekly_trends: Dict[str, Any]
    
    # Alerte
    active_alerts_count: int
    critical_alerts_count: int


# ==================== SCHEME PENTRU EXPORT ====================

class ExportRequest(BaseModel):
    """Schema pentru cererea de export date financiare."""
    format: str = Field(..., description="Formatul de export: 'csv', 'excel', 'json'")
    start_date: Optional[Date] = Field(None, description="Data de început")
    end_date: Optional[Date] = Field(None, description="Data de sfârșit")
    include_costs: bool = Field(True, description="Include costurile")
    include_revenue: bool = Field(True, description="Include veniturile")
    include_metrics: bool = Field(True, description="Include metricile")
    
    @validator('format')
    def validate_format(cls, v):
        """Validează formatul de export."""
        valid_formats = ['csv', 'excel', 'json']
        if v.lower() not in valid_formats:
            raise ValueError(f'Format invalid: {v}. Formate valide: {valid_formats}')
        return v.lower()


class ExportResponse(BaseModel):
    """Schema pentru răspunsul cu link-ul de download."""
    download_url: str = Field(..., description="URL-ul pentru download")
    file_name: str = Field(..., description="Numele fișierului")
    file_size: int = Field(..., description="Mărimea fișierului în bytes")
    expires_at: datetime = Field(..., description="Când expiră link-ul")
