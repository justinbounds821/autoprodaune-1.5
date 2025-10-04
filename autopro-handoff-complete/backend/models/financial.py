"""
Modele financiare pentru AutoPro Daune.

Acest modul definește modelele de bază de date pentru tracking financiar,
inclusiv costuri API, venituri și metrici financiare.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, Date, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from ..database import Base


class APICost(Base):
    """
    Model pentru înregistrarea costurilor API externe.
    
    Acest tabel înregistrează fiecare cost API extern (ex: Pika, HeyGen, TikTok, etc.)
    cu detalii despre provider, operația efectuată și costul asociat.
    """
    __tablename__ = "api_costs"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(50), nullable=False, index=True)  # ex: "Pika", "HeyGen", "TikTok"
    operation = Column(String(100), nullable=False)  # ex: "generate_video", "upload_content"
    cost = Column(DECIMAL(10, 2), nullable=False)  # costul în dolari
    credits_used = Column(Integer, nullable=True)  # creditele consumate (dacă aplicabil)
    currency = Column(String(3), default="USD")  # moneda (default USD)
    extra_data = Column(Text, nullable=True)  # JSON cu detalii suplimentare
    timestamp = Column(DateTime, default=func.now(), nullable=False, index=True)
    
    def __repr__(self):
        return f"<APICost(id={self.id}, provider='{self.provider}', operation='{self.operation}', cost={self.cost})>"


class Revenue(Base):
    """
    Model pentru înregistrarea veniturilor obținute.
    
    Acest tabel înregistrează veniturile provenite din conversii, leads vânduți,
    sau alte surse de venit asociate cu campaniile de marketing.
    """
    __tablename__ = "revenue"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), nullable=False, index=True)  # ex: "TikTokAds", "LeadConversion", "Referral"
    amount = Column(DECIMAL(10, 2), nullable=False)  # suma în dolari
    lead_id = Column(Integer, nullable=True, index=True)  # ID-ul lead-ului asociat (dacă aplicabil)
    conversion_type = Column(String(50), nullable=True)  # ex: "insurance_sale", "consultation"
    currency = Column(String(3), default="USD")  # moneda (default USD)
    extra_data = Column(Text, nullable=True)  # JSON cu detalii suplimentare
    timestamp = Column(DateTime, default=func.now(), nullable=False, index=True)
    
    def __repr__(self):
        return f"<Revenue(id={self.id}, source='{self.source}', amount={self.amount}, lead_id={self.lead_id})>"


class FinancialMetrics(Base):
    """
    Model pentru metricile financiare agregate pe zile.
    
    Acest tabel stochează metricile calculate zilnic pentru analiza ROI,
    profit/loss și alte KPI-uri financiare importante.
    """
    __tablename__ = "financial_metrics"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, unique=True, index=True)  # data pentru care se calculează metricile
    
    # Costuri
    total_costs = Column(DECIMAL(10, 2), default=Decimal('0.00'), nullable=False)
    api_costs = Column(DECIMAL(10, 2), default=Decimal('0.00'), nullable=False)
    advertising_costs = Column(DECIMAL(10, 2), default=Decimal('0.00'), nullable=False)
    other_costs = Column(DECIMAL(10, 2), default=Decimal('0.00'), nullable=False)
    
    # Venituri
    total_revenue = Column(DECIMAL(10, 2), default=Decimal('0.00'), nullable=False)
    lead_conversion_revenue = Column(DECIMAL(10, 2), default=Decimal('0.00'), nullable=False)
    referral_revenue = Column(DECIMAL(10, 2), default=Decimal('0.00'), nullable=False)
    other_revenue = Column(DECIMAL(10, 2), default=Decimal('0.00'), nullable=False)
    
    # Metrici calculate
    net_profit = Column(DECIMAL(10, 2), default=Decimal('0.00'), nullable=False)
    roi_percentage = Column(DECIMAL(5, 2), default=Decimal('0.00'), nullable=False)  # ROI în procente
    
    # Contoare
    total_leads = Column(Integer, default=0, nullable=False)
    converted_leads = Column(Integer, default=0, nullable=False)
    total_referrals = Column(Integer, default=0, nullable=False)
    
    # Timestamp pentru tracking
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<FinancialMetrics(date={self.date}, profit={self.net_profit}, roi={self.roi_percentage}%)>"


class CampaignMetrics(Base):
    """
    Model pentru metricile specifice campaniilor de marketing.
    
    Acest tabel permite tracking-ul performanței per campanie,
    per platformă sau per perioadă specifică.
    """
    __tablename__ = "campaign_metrics"

    id = Column(Integer, primary_key=True, index=True)
    campaign_name = Column(String(100), nullable=False, index=True)  # numele campaniei
    platform = Column(String(50), nullable=False, index=True)  # ex: "TikTok", "Instagram", "YouTube"
    period_start = Column(Date, nullable=False, index=True)  # începutul perioadei
    period_end = Column(Date, nullable=False, index=True)  # sfârșitul perioadei
    
    # Metrici de cost
    total_spent = Column(DECIMAL(10, 2), default=Decimal('0.00'), nullable=False)
    cost_per_lead = Column(DECIMAL(10, 2), default=Decimal('0.00'), nullable=False)
    cost_per_conversion = Column(DECIMAL(10, 2), default=Decimal('0.00'), nullable=False)
    
    # Metrici de performanță
    total_leads = Column(Integer, default=0, nullable=False)
    total_conversions = Column(Integer, default=0, nullable=False)
    conversion_rate = Column(DECIMAL(5, 2), default=Decimal('0.00'), nullable=False)  # în procente
    
    # Metrici de engagement (pentru social media)
    total_views = Column(Integer, default=0, nullable=False)
    total_likes = Column(Integer, default=0, nullable=False)
    total_shares = Column(Integer, default=0, nullable=False)
    engagement_rate = Column(DECIMAL(5, 2), default=Decimal('0.00'), nullable=False)  # în procente
    
    # ROI și profit
    total_revenue = Column(DECIMAL(10, 2), default=Decimal('0.00'), nullable=False)
    net_profit = Column(DECIMAL(10, 2), default=Decimal('0.00'), nullable=False)
    roi_percentage = Column(DECIMAL(5, 2), default=Decimal('0.00'), nullable=False)
    
    # Metadata suplimentară
    extra_data = Column(Text, nullable=True)  # JSON cu detalii suplimentare
    
    # Timestamp
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<CampaignMetrics(campaign='{self.campaign_name}', platform='{self.platform}', roi={self.roi_percentage}%)>"


class CreditBalance(Base):
    """
    Model pentru tracking-ul creditelor disponibile la providerii externi.
    
    Acest tabel păstrează evidența creditelor rămase la diverse servicii
    (Pika, HeyGen, etc.) pentru a evita supratransformarea.
    """
    __tablename__ = "credit_balances"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(50), nullable=False, unique=True, index=True)  # ex: "Pika", "HeyGen"
    credit_type = Column(String(50), nullable=False)  # ex: "video_seconds", "api_calls", "credits"
    current_balance = Column(DECIMAL(10, 2), nullable=False)  # soldul curent
    total_allocated = Column(DECIMAL(10, 2), nullable=False)  # totalul alocat
    last_updated = Column(DateTime, default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<CreditBalance(provider='{self.provider}', balance={self.current_balance}/{self.total_allocated})>"


class BudgetAlert(Base):
    """
    Model pentru alertele de buget și praguri financiare.
    
    Acest tabel stochează alertele configurate pentru depășirea unor praguri
    de cost, ROI negativ sau alte condiții financiare critice.
    """
    __tablename__ = "budget_alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_name = Column(String(100), nullable=False)  # numele alertei
    alert_type = Column(String(50), nullable=False, index=True)  # ex: "budget_exceeded", "negative_roi", "low_credits"
    threshold_value = Column(DECIMAL(10, 2), nullable=False)  # valoarea pragului
    current_value = Column(DECIMAL(10, 2), nullable=False)  # valoarea curentă
    is_triggered = Column(Integer, default=0, nullable=False)  # 0 = nu, 1 = da
    is_active = Column(Integer, default=1, nullable=False)  # 0 = inactiv, 1 = activ
    
    # Detalii alerte
    message = Column(Text, nullable=True)  # mesajul alertei
    notification_sent = Column(DateTime, nullable=True)  # când a fost trimisă ultima notificare
    
    # Timestamp
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<BudgetAlert(name='{self.alert_name}', type='{self.alert_type}', triggered={bool(self.is_triggered)})>"


# Enum-uri pentru validare
class ProviderType:
    """Tipuri de provideri API suportați."""
    PIKA = "Pika"
    HEYGEN = "HeyGen"
    TIKTOK = "TikTok"
    INSTAGRAM = "Instagram"
    YOUTUBE = "YouTube"
    PUBLER = "Publer"
    GOOGLE_SHEETS = "GoogleSheets"
    TELEGRAM = "Telegram"   # deprecated (compatibility)
    WHATSAPP = "WhatsApp"


class OperationType:
    """Tipuri de operații API."""
    GENERATE_VIDEO = "generate_video"
    UPLOAD_CONTENT = "upload_content"
    POST_CONTENT = "post_content"
    READ_SHEETS = "read_sheets"
    WRITE_SHEETS = "write_sheets"
    SEND_MESSAGE = "send_message"


class RevenueSource:
    """Surse de venit."""
    LEAD_CONVERSION = "LeadConversion"
    REFERRAL = "Referral"
    CONSULTATION = "Consultation"
    INSURANCE_SALE = "InsuranceSale"
    OTHER = "Other"


class AlertType:
    """Tipuri de alerte."""
    BUDGET_EXCEEDED = "budget_exceeded"
    NEGATIVE_ROI = "negative_roi"
    LOW_CREDITS = "low_credits"
    HIGH_COST_PER_LEAD = "high_cost_per_lead"
    LOW_CONVERSION_RATE = "low_conversion_rate"
