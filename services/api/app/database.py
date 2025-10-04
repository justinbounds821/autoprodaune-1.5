"""
Configurația bazei de date pentru AutoPro Daune.

Acest modul configurează conexiunea la baza de date PostgreSQL
și oferă funcții pentru gestionarea sesiunilor.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Încarcă variabilele de mediu
load_dotenv()

# Configurația bazei de date
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://autopro:autopro123@localhost:5432/autoprodaune"
)

# Creează engine-ul SQLAlchemy (doar când este necesar)
engine = None
SessionLocal = None

def get_engine():
    """Obține engine-ul SQLAlchemy, creându-l dacă este necesar."""
    global engine
    if engine is None:
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False  # Setează True pentru debug SQL
        )
    return engine

def get_session_local():
    """Obține sesiunea SQLAlchemy, creând-o dacă este necesară."""
    global SessionLocal
    if SessionLocal is None:
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return SessionLocal

# Base pentru modelele declarative
Base = declarative_base()


def get_db():
    """
    Dependency pentru a obține o sesiune de bază de date.
    
    Yields:
        Session: Sesiunea SQLAlchemy
    """
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Creează toate tabelele în baza de date.
    
    Această funcție ar trebui să fie apelată la pornirea aplicației
    pentru a crea tabelele necesare.
    """
    # Importă toate modelele pentru a le înregistra
    from .models import financial
    
    # Creează toate tabelele
    Base.metadata.create_all(bind=get_engine())


def drop_tables():
    """
    Șterge toate tabelele din baza de date.
    
    ATENȚIE: Această funcție va șterge toate datele!
    """
    # Importă toate modelele pentru a le înregistra
    from .models import financial
    
    # Șterge toate tabelele
    Base.metadata.drop_all(bind=get_engine())


def check_database_connection():
    """
    Verifică conexiunea la baza de date.
    
    Returns:
        bool: True dacă conexiunea este OK, False altfel
    """
    try:
        SessionLocal = get_session_local()
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        print(f"Eroare la conexiunea la baza de date: {e}")
        return False


if __name__ == "__main__":
    # Pentru testare standalone
    if check_database_connection():
        print("✅ Conexiunea la baza de date este OK")
    else:
        print("❌ Eroare la conexiunea la baza de date")

