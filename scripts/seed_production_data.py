#!/usr/bin/env python3
"""
Production Seed Data Script
Script pentru popularea bazei de date cu date demo/test în producție
"""

import os
import sys
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List
import psycopg2
from psycopg2.extras import RealDictCursor
import json

# Configurează logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/seed_data.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ProductionDataSeeder:
    """Clasa pentru popularea cu date demo"""
    
    def __init__(self):
        self.db_config = self._load_db_config()
        self.demo_data_enabled = os.getenv('ENABLE_TEST_DATA', 'false').lower() == 'true'
        
    def _load_db_config(self) -> Dict[str, Any]:
        """Încarcă configurația bazei de date"""
        return {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': int(os.getenv('POSTGRES_PORT', 5432)),
            'database': os.getenv('POSTGRES_DB', 'autopro_daune_prod'),
            'user': os.getenv('POSTGRES_USER', 'autopro_user'),
            'password': os.getenv('POSTGRES_PASSWORD', ''),
        }
    
    def _get_connection(self) -> psycopg2.connection:
        """Creează conexiunea la baza de date"""
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except Exception as e:
            logger.error(f"Eroare la conectarea la baza de date: {str(e)}")
            raise
    
    def check_if_data_exists(self) -> bool:
        """Verifică dacă există deja date în baza de date"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Verifică dacă există date în tabelele principale
            cursor.execute("SELECT COUNT(*) FROM api_costs")
            api_costs_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM revenues")
            revenues_count = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            total_count = api_costs_count + revenues_count
            logger.info(f"Există {total_count} înregistrări în baza de date")
            
            return total_count > 0
            
        except Exception as e:
            logger.error(f"Eroare la verificarea datelor existente: {str(e)}")
            return False
    
    def seed_credit_balances(self) -> bool:
        """Populează tabela credit_balances cu date demo"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Verifică dacă există deja date
            cursor.execute("SELECT COUNT(*) FROM credit_balances")
            if cursor.fetchone()[0] > 0:
                logger.info("Credit balances există deja, sări peste")
                cursor.close()
                conn.close()
                return True
            
            credit_providers = [
                {'provider': 'pika', 'initial_balance': 1000.0},
                {'provider': 'heygen', 'initial_balance': 500.0},
                {'provider': 'openai', 'initial_balance': 250.0},
                {'provider': 'anthropic', 'initial_balance': 100.0}
            ]
            
            for provider_data in credit_providers:
                cursor.execute("""
                    INSERT INTO credit_balances (
                        provider, current_balance, total_credits_purchased,
                        total_credits_used, last_updated, status
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    provider_data['provider'],
                    provider_data['initial_balance'],
                    provider_data['initial_balance'] * 1.2,  # 20% mai mult cumpărat
                    provider_data['initial_balance'] * 0.2,  # 20% folosit
                    datetime.now(),
                    'active'
                ))
            
            conn.commit()
            logger.info(f"Adăugate {len(credit_providers)} înregistrări în credit_balances")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Eroare la popularea credit_balances: {str(e)}")
            return False
    
    def seed_api_costs(self, count: int = 50) -> bool:
        """Populează tabela api_costs cu date demo"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            services = ['pika', 'heygen', 'openai', 'anthropic', 'google']
            operations = ['video_generation', 'text_generation', 'image_generation', 'api_call']
            
            for i in range(count):
                service = random.choice(services)
                operation = random.choice(operations)
                
                # Simulează costuri realiste
                if service == 'pika':
                    cost = round(random.uniform(0.5, 2.0), 2)
                    credits_used = random.randint(5, 20)
                elif service == 'heygen':
                    cost = round(random.uniform(0.1, 0.8), 2)
                    credits_used = random.randint(2, 10)
                elif service in ['openai', 'anthropic']:
                    cost = round(random.uniform(0.01, 0.5), 2)
                    credits_used = random.randint(1, 5)
                else:
                    cost = round(random.uniform(0.001, 0.1), 3)
                    credits_used = random.randint(1, 3)
                
                # Generează timestamp aleatoriu în ultimele 30 de zile
                timestamp = datetime.now() - timedelta(
                    days=random.randint(0, 30),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
                
                cursor.execute("""
                    INSERT INTO api_costs (
                        service, operation, cost, credits_used,
                        duration, quality, timestamp, metadata
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    service,
                    operation,
                    cost,
                    credits_used,
                    random.randint(10, 120),  # duration în secunde
                    random.choice(['low', 'medium', 'high']),
                    timestamp,
                    json.dumps({
                        'request_id': f'req_{i:06d}',
                        'user_id': f'user_{random.randint(1, 10):03d}',
                        'session_id': f'sess_{random.randint(1, 100):04d}'
                    })
                ))
            
            conn.commit()
            logger.info(f"Adăugate {count} înregistrări în api_costs")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Eroare la popularea api_costs: {str(e)}")
            return False
    
    def seed_revenues(self, count: int = 30) -> bool:
        """Populează tabela revenues cu date demo"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            revenue_sources = [
                'policy_sales', 'renewals', 'upgrades', 'add_ons',
                'referrals', 'partnerships', 'consulting'
            ]
            
            policy_types = [
                'comprehensive', 'third_party', 'fire_theft', 'casco',
                'rca', 'travel', 'health'
            ]
            
            for i in range(count):
                source = random.choice(revenue_sources)
                
                # Simulează venituri realiste
                if source == 'policy_sales':
                    amount = round(random.uniform(200, 800), 2)
                elif source == 'renewals':
                    amount = round(random.uniform(150, 600), 2)
                elif source == 'upgrades':
                    amount = round(random.uniform(50, 300), 2)
                else:
                    amount = round(random.uniform(20, 150), 2)
                
                # Generează timestamp aleatoriu în ultimele 30 de zile
                timestamp = datetime.now() - timedelta(
                    days=random.randint(0, 30),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
                
                cursor.execute("""
                    INSERT INTO revenues (
                        source, amount, currency, description,
                        customer_id, policy_type, timestamp, metadata
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    source,
                    amount,
                    'RON',
                    f'Demo revenue from {source}',
                    f'cust_{random.randint(1, 50):03d}',
                    random.choice(policy_types) if source in ['policy_sales', 'renewals', 'upgrades'] else None,
                    timestamp,
                    json.dumps({
                        'campaign_id': f'camp_{random.randint(1, 10):02d}',
                        'lead_source': random.choice(['website', 'social_media', 'referral', 'direct']),
                        'sales_rep': f'rep_{random.randint(1, 5):02d}'
                    })
                ))
            
            conn.commit()
            logger.info(f"Adăugate {count} înregistrări în revenues")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Eroare la popularea revenues: {str(e)}")
            return False
    
    def seed_financial_metrics(self) -> bool:
        """Populează tabela financial_metrics cu date demo"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Calculează metrici pe baza datelor existente
            cursor.execute("""
                SELECT 
                    SUM(cost) as total_costs,
                    COUNT(*) as total_transactions
                FROM api_costs
            """)
            cost_data = cursor.fetchone()
            
            cursor.execute("""
                SELECT 
                    SUM(amount) as total_revenue,
                    COUNT(*) as total_sales
                FROM revenues
            """)
            revenue_data = cursor.fetchone()
            
            total_costs = cost_data[0] or 0
            total_revenue = revenue_data[0] or 0
            
            # Calculează ROI
            roi_percentage = ((total_revenue - total_costs) / total_costs * 100) if total_costs > 0 else 0
            profit_margin = ((total_revenue - total_costs) / total_revenue * 100) if total_revenue > 0 else 0
            
            # Generează date pentru ultimele 30 de zile
            for i in range(30):
                date = datetime.now().date() - timedelta(days=i)
                
                # Simulează variații zilnice
                daily_costs = round(total_costs / 30 * random.uniform(0.8, 1.2), 2)
                daily_revenue = round(total_revenue / 30 * random.uniform(0.7, 1.3), 2)
                daily_leads = random.randint(5, 25)
                daily_conversions = random.randint(1, 8)
                
                cursor.execute("""
                    INSERT INTO financial_metrics (
                        date, total_revenue, total_costs, roi_percentage,
                        profit_margin, conversion_rate, avg_deal_size,
                        customer_acquisition_cost, lifetime_value, metadata
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    date,
                    daily_revenue,
                    daily_costs,
                    round(roi_percentage * random.uniform(0.9, 1.1), 2),
                    round(profit_margin * random.uniform(0.9, 1.1), 2),
                    round((daily_conversions / daily_leads * 100) if daily_leads > 0 else 0, 2),
                    round(daily_revenue / max(daily_conversions, 1), 2),
                    round(daily_costs / max(daily_leads, 1), 2),
                    round(daily_revenue * 2.5, 2),  # LTV estimat
                    json.dumps({
                        'leads_count': daily_leads,
                        'conversions_count': daily_conversions,
                        'period': 'daily'
                    })
                ))
            
            conn.commit()
            logger.info("Adăugate 30 înregistrări în financial_metrics")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Eroare la popularea financial_metrics: {str(e)}")
            return False
    
    def seed_campaign_metrics(self) -> bool:
        """Populează tabela campaign_metrics cu date demo"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            campaigns = [
                {'name': 'Summer Campaign 2024', 'type': 'seasonal'},
                {'name': 'TikTok Video Series', 'type': 'social_media'},
                {'name': 'Google Ads Q4', 'type': 'paid_search'},
                {'name': 'Referral Program', 'type': 'referral'},
                {'name': 'Email Newsletter', 'type': 'email_marketing'}
            ]
            
            for campaign in campaigns:
                # Generează date pentru fiecare campanie
                start_date = datetime.now().date() - timedelta(days=random.randint(15, 60))
                end_date = start_date + timedelta(days=random.randint(7, 30))
                
                budget = round(random.uniform(500, 5000), 2)
                spent = round(budget * random.uniform(0.6, 1.0), 2)
                impressions = random.randint(10000, 100000)
                clicks = random.randint(100, 10000)
                conversions = random.randint(10, 100)
                
                cursor.execute("""
                    INSERT INTO campaign_metrics (
                        campaign_name, campaign_type, start_date, end_date,
                        budget, spent, impressions, clicks, conversions,
                        ctr, conversion_rate, cost_per_click, cost_per_conversion,
                        roi_percentage, status, metadata
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    campaign['name'],
                    campaign['type'],
                    start_date,
                    end_date,
                    budget,
                    spent,
                    impressions,
                    clicks,
                    conversions,
                    round((clicks / impressions * 100) if impressions > 0 else 0, 2),
                    round((conversions / clicks * 100) if clicks > 0 else 0, 2),
                    round(spent / max(clicks, 1), 2),
                    round(spent / max(conversions, 1), 2),
                    round(((conversions * 200 - spent) / spent * 100) if spent > 0 else 0, 2),
                    random.choice(['active', 'completed', 'paused']),
                    json.dumps({
                        'platforms': random.sample(['facebook', 'google', 'tiktok', 'instagram'], 
                                                 random.randint(1, 3)),
                        'target_audience': f'age_{random.randint(18, 65)}',
                        'creative_count': random.randint(3, 15)
                    })
                ))
            
            conn.commit()
            logger.info(f"Adăugate {len(campaigns)} înregistrări în campaign_metrics")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Eroare la popularea campaign_metrics: {str(e)}")
            return False
    
    def seed_budget_alerts(self) -> bool:
        """Populează tabela budget_alerts cu date demo"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            alert_types = [
                'api_cost_threshold', 'low_revenue', 'high_spending',
                'low_roi', 'budget_exceeded', 'credit_low'
            ]
            
            alert_levels = ['info', 'warning', 'critical']
            
            for i in range(20):
                alert_type = random.choice(alert_types)
                level = random.choice(alert_levels)
                
                # Generează timestamp aleatoriu în ultimele 7 zile
                timestamp = datetime.now() - timedelta(
                    days=random.randint(0, 7),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
                
                # Simulează valori și praguri
                if alert_type == 'api_cost_threshold':
                    threshold = 100.0
                    current_value = random.uniform(80, 120)
                elif alert_type == 'low_revenue':
                    threshold = 500.0
                    current_value = random.uniform(300, 600)
                elif alert_type == 'low_roi':
                    threshold = 50.0
                    current_value = random.uniform(30, 70)
                else:
                    threshold = random.uniform(50, 200)
                    current_value = random.uniform(threshold * 0.8, threshold * 1.2)
                
                cursor.execute("""
                    INSERT INTO budget_alerts (
                        alert_type, level, threshold, current_value,
                        message, is_resolved, created_at, resolved_at, metadata
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    alert_type,
                    level,
                    threshold,
                    round(current_value, 2),
                    f"Demo alert: {alert_type} - {level} level",
                    random.choice([True, False]),
                    timestamp,
                    timestamp + timedelta(hours=random.randint(1, 24)) if random.choice([True, False]) else None,
                    json.dumps({
                        'source': random.choice(['automated', 'manual', 'scheduled']),
                        'user_id': f'user_{random.randint(1, 10):02d}',
                        'action_taken': random.choice(['none', 'investigation', 'fix_applied'])
                    })
                ))
            
            conn.commit()
            logger.info(f"Adăugate 20 înregistrări în budget_alerts")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Eroare la popularea budget_alerts: {str(e)}")
            return False
    
    def run_seed_data(self) -> bool:
        """Rulează procesul complet de populare cu date"""
        logger.info("=== Începe popularea cu date demo ===")
        
        if not self.demo_data_enabled:
            logger.info("Demo data este dezactivată prin ENV")
            return True
        
        try:
            # Verifică dacă există deja date
            if self.check_if_data_exists():
                response = input("Există deja date în baza de date. Continuăm? (y/N): ")
                if response.lower() != 'y':
                    logger.info("Popularea anulată de utilizator")
                    return True
            
            # Populează tabelele în ordine
            success = True
            
            if not self.seed_credit_balances():
                success = False
            
            if not self.seed_api_costs(50):
                success = False
            
            if not self.seed_revenues(30):
                success = False
            
            if not self.seed_financial_metrics():
                success = False
            
            if not self.seed_campaign_metrics():
                success = False
            
            if not self.seed_budget_alerts():
                success = False
            
            if success:
                logger.info("=== Popularea cu date demo completată cu succes! ===")
            else:
                logger.error("=== Popularea cu date demo a avut erori ===")
            
            return success
            
        except Exception as e:
            logger.error(f"Eroare în timpul populării cu date: {str(e)}")
            return False

def main():
    """Funcția principală"""
    seeder = ProductionDataSeeder()
    
    success = seeder.run_seed_data()
    
    if success:
        logger.info("Popularea cu date a fost completată cu succes!")
        sys.exit(0)
    else:
        logger.error("Popularea cu date a eșuat!")
        sys.exit(1)

if __name__ == "__main__":
    main()
