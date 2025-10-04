#!/usr/bin/env python3
"""
Production Migration Script
Script pentru migrarea bazei de date în producție
"""

import os
import sys
import logging
import subprocess
import time
from datetime import datetime
from typing import Dict, Any, List
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import json

# Configurează logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/migration.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ProductionMigrator:
    """Clasa pentru migrarea în producție"""
    
    def __init__(self):
        self.db_config = self._load_db_config()
        self.migration_files = []
        self.backup_enabled = True
        
    def _load_db_config(self) -> Dict[str, Any]:
        """Încarcă configurația bazei de date"""
        return {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': int(os.getenv('POSTGRES_PORT', 5432)),
            'database': os.getenv('POSTGRES_DB', 'autopro_daune_prod'),
            'user': os.getenv('POSTGRES_USER', 'autopro_user'),
            'password': os.getenv('POSTGRES_PASSWORD', ''),
        }
    
    def _get_connection(self, database: str = None) -> psycopg2.connection:
        """Creează conexiunea la baza de date"""
        config = self.db_config.copy()
        if database:
            config['database'] = database
        
        try:
            conn = psycopg2.connect(**config)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            return conn
        except Exception as e:
            logger.error(f"Eroare la conectarea la baza de date: {str(e)}")
            raise
    
    def check_database_connection(self) -> bool:
        """Verifică conexiunea la baza de date"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            logger.info(f"Conexiune la PostgreSQL: {version}")
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Eroare la verificarea conexiunii: {str(e)}")
            return False
    
    def create_database_if_not_exists(self) -> bool:
        """Creează baza de date dacă nu există"""
        try:
            # Conectează-te la postgres pentru a crea baza de date
            conn = self._get_connection('postgres')
            cursor = conn.cursor()
            
            # Verifică dacă baza de date există
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (self.db_config['database'],)
            )
            
            if cursor.fetchone():
                logger.info(f"Baza de date {self.db_config['database']} există deja")
                return True
            
            # Creează baza de date
            cursor.execute(
                f"CREATE DATABASE {self.db_config['database']} "
                f"WITH ENCODING='UTF8' "
                f"LC_COLLATE='ro_RO.UTF-8' "
                f"LC_CTYPE='ro_RO.UTF-8'"
            )
            
            logger.info(f"Baza de date {self.db_config['database']} creată cu succes")
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Eroare la crearea bazei de date: {str(e)}")
            return False
    
    def create_migrations_table(self) -> bool:
        """Creează tabela pentru tracking migrări"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    id SERIAL PRIMARY KEY,
                    version VARCHAR(50) UNIQUE NOT NULL,
                    description TEXT,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    checksum VARCHAR(64),
                    execution_time_ms INTEGER
                );
            """)
            
            logger.info("Tabela schema_migrations creată/verificată")
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Eroare la crearea tabelei de migrări: {str(e)}")
            return False
    
    def get_applied_migrations(self) -> List[str]:
        """Returnează lista migrărilor aplicate"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT version FROM schema_migrations ORDER BY version")
            migrations = [row[0] for row in cursor.fetchall()]
            
            cursor.close()
            conn.close()
            return migrations
            
        except Exception as e:
            logger.error(f"Eroare la obținerea migrărilor aplicate: {str(e)}")
            return []
    
    def get_migration_files(self) -> List[str]:
        """Returnează lista fișierelor de migrare"""
        migrations_dir = '/app/services/api/app/database/migrations'
        
        if not os.path.exists(migrations_dir):
            logger.warning(f"Directorul de migrări nu există: {migrations_dir}")
            return []
        
        migration_files = []
        for file in sorted(os.listdir(migrations_dir)):
            if file.endswith('.sql'):
                migration_files.append(os.path.join(migrations_dir, file))
        
        logger.info(f"Găsite {len(migration_files)} fișiere de migrare")
        return migration_files
    
    def calculate_checksum(self, file_path: str) -> str:
        """Calculează checksum-ul unui fișier"""
        import hashlib
        
        with open(file_path, 'rb') as f:
            content = f.read()
            return hashlib.sha256(content).hexdigest()
    
    def apply_migration(self, migration_file: str) -> bool:
        """Aplică o migrare"""
        try:
            start_time = time.time()
            
            # Extrage versiunea din numele fișierului
            filename = os.path.basename(migration_file)
            version = filename.split('_')[0]
            
            # Calculează checksum
            checksum = self.calculate_checksum(migration_file)
            
            # Verifică dacă migrarea a fost deja aplicată
            applied_migrations = self.get_applied_migrations()
            if version in applied_migrations:
                logger.info(f"Migrarea {version} a fost deja aplicată")
                return True
            
            # Citește și execută migrarea
            conn = self._get_connection()
            cursor = conn.cursor()
            
            with open(migration_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # Execută migrarea
            cursor.execute(sql_content)
            
            # Înregistrează migrarea
            execution_time = int((time.time() - start_time) * 1000)
            description = f"Migration from {filename}"
            
            cursor.execute("""
                INSERT INTO schema_migrations (version, description, checksum, execution_time_ms)
                VALUES (%s, %s, %s, %s)
            """, (version, description, checksum, execution_time))
            
            logger.info(f"Migrarea {version} aplicată cu succes în {execution_time}ms")
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Eroare la aplicarea migrării {migration_file}: {str(e)}")
            return False
    
    def create_backup(self) -> bool:
        """Creează backup al bazei de date"""
        if not self.backup_enabled:
            logger.info("Backup dezactivat")
            return True
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"/backups/pre_migration_{timestamp}.sql"
            
            # Creează directorul de backup dacă nu există
            os.makedirs(os.path.dirname(backup_file), exist_ok=True)
            
            # Comandă pg_dump
            cmd = [
                'pg_dump',
                '-h', self.db_config['host'],
                '-p', str(self.db_config['port']),
                '-U', self.db_config['user'],
                '-d', self.db_config['database'],
                '-f', backup_file,
                '--verbose',
                '--no-password'
            ]
            
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_config['password']
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Backup creat cu succes: {backup_file}")
                return True
            else:
                logger.error(f"Eroare la crearea backup-ului: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Eroare la crearea backup-ului: {str(e)}")
            return False
    
    def verify_migration(self) -> bool:
        """Verifică integritatea migrării"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Verifică tabelele principale
            expected_tables = [
                'api_costs',
                'revenues',
                'financial_metrics',
                'campaign_metrics',
                'credit_balances',
                'budget_alerts',
                'schema_migrations'
            ]
            
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            missing_tables = set(expected_tables) - set(existing_tables)
            if missing_tables:
                logger.error(f"Tabele lipsă: {missing_tables}")
                return False
            
            logger.info("Toate tabelele sunt prezente")
            
            # Verifică indexurile
            cursor.execute("""
                SELECT indexname 
                FROM pg_indexes 
                WHERE schemaname = 'public'
                ORDER BY indexname
            """)
            
            indexes = [row[0] for row in cursor.fetchall()]
            logger.info(f"Găsite {len(indexes)} indexuri")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Eroare la verificarea migrării: {str(e)}")
            return False
    
    def run_migration(self) -> bool:
        """Rulează procesul complet de migrare"""
        logger.info("=== Începe migrarea în producție ===")
        
        try:
            # 1. Verifică conexiunea
            if not self.check_database_connection():
                logger.error("Nu se poate conecta la baza de date")
                return False
            
            # 2. Creează baza de date dacă nu există
            if not self.create_database_if_not_exists():
                logger.error("Nu s-a putut crea baza de date")
                return False
            
            # 3. Creează tabela de migrări
            if not self.create_migrations_table():
                logger.error("Nu s-a putut crea tabela de migrări")
                return False
            
            # 4. Creează backup
            if not self.create_backup():
                logger.warning("Nu s-a putut crea backup-ul, dar continuăm")
            
            # 5. Aplică migrările
            migration_files = self.get_migration_files()
            if not migration_files:
                logger.warning("Nu s-au găsit fișiere de migrare")
                return True
            
            applied_count = 0
            for migration_file in migration_files:
                if self.apply_migration(migration_file):
                    applied_count += 1
                else:
                    logger.error(f"Migrarea {migration_file} a eșuat")
                    return False
            
            # 6. Verifică migrarea
            if not self.verify_migration():
                logger.error("Verificarea migrării a eșuat")
                return False
            
            logger.info(f"=== Migrarea completată cu succes! {applied_count} migrări aplicate ===")
            return True
            
        except Exception as e:
            logger.error(f"Eroare în timpul migrării: {str(e)}")
            return False

def main():
    """Funcția principală"""
    migrator = ProductionMigrator()
    
    success = migrator.run_migration()
    
    if success:
        logger.info("Migrarea a fost completată cu succes!")
        sys.exit(0)
    else:
        logger.error("Migrarea a eșuat!")
        sys.exit(1)

if __name__ == "__main__":
    main()
