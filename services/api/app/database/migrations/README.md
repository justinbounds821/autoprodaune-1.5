# Migrații Baza de Date - AutoPro Daune

Acest director conține migrațiile pentru baza de date PostgreSQL.

## Structura Migrațiilor

### 001_financial_tables.sql
**Descriere**: Creează tabelele necesare pentru tracking financiar
**Tabele create**:
- `api_costs` - Costuri API externe
- `revenue` - Venituri obținute
- `financial_metrics` - Metrici financiare agregate
- `campaign_metrics` - Metrici specifice campaniilor
- `credit_balances` - Solduri credite disponibile
- `budget_alerts` - Alerte de buget și praguri

**Funcții create**:
- `calculate_roi()` - Calculează ROI-ul
- `calculate_net_profit()` - Calculează profitul net
- `update_updated_at_column()` - Actualizează automat timestamp-ul

## Cum să Rulezi Migrațiile

### Metoda 1: Direct SQL
```bash
# Conectează-te la baza de date PostgreSQL
psql -h localhost -U autoprodaune_user -d autoprodaune_db

# Rulează migrația
\i services/api/app/database/migrations/001_financial_tables.sql
```

### Metoda 2: Din Docker
```bash
# Copiază migrația în container
docker cp services/api/app/database/migrations/001_financial_tables.sql \
  autoprodaune-1-db-1:/tmp/

# Rulează migrația în container
docker exec -i autoprodaune-1-db-1 psql -U autoprodaune_user -d autoprodaune_db < /tmp/001_financial_tables.sql
```

### Metoda 3: Cu Python Script
```python
import psycopg2
from pathlib import Path

# Conectează-te la baza de date
conn = psycopg2.connect(
    host="localhost",
    database="autoprodaune_db", 
    user="autoprodaune_user",
    password="your_password"
)

# Citește și rulează migrația
migration_file = Path("services/api/app/database/migrations/001_financial_tables.sql")
with open(migration_file, 'r') as f:
    migration_sql = f.read()

cursor = conn.cursor()
cursor.execute(migration_sql)
conn.commit()
cursor.close()
conn.close()
```

## Verificare Migrație

După rularea migrației, verifică că tabelele au fost create:

```sql
-- Verifică tabelele create
\dt

-- Verifică structura unei tabele
\d api_costs

-- Verifică datele inițiale
SELECT * FROM credit_balances;
SELECT * FROM budget_alerts;
```

## Rollback (dacă e necesar)

Pentru a anula migrația:

```sql
-- Șterge tabelele (ATENȚIE: Va șterge toate datele!)
DROP TABLE IF EXISTS budget_alerts CASCADE;
DROP TABLE IF EXISTS credit_balances CASCADE;
DROP TABLE IF EXISTS campaign_metrics CASCADE;
DROP TABLE IF EXISTS financial_metrics CASCADE;
DROP TABLE IF EXISTS revenue CASCADE;
DROP TABLE IF EXISTS api_costs CASCADE;

-- Șterge funcțiile
DROP FUNCTION IF EXISTS calculate_roi(DECIMAL, DECIMAL);
DROP FUNCTION IF EXISTS calculate_net_profit(DECIMAL, DECIMAL);
DROP FUNCTION IF EXISTS update_updated_at_column();
```

## Note Importante

1. **Backup**: Întotdeauna fă backup înainte de a rula migrații în producție
2. **Testare**: Testează migrațiile pe un mediu de test înainte de producție
3. **Ordine**: Respectă ordinea numerotării migrațiilor
4. **Dependențe**: Unele migrații pot depinde de altele anterioare

## Următoarele Migrații

- `002_*.sql` - Tabele pentru social media tracking
- `003_*.sql` - Tabele pentru video generation
- `004_*.sql` - Tabele pentru analytics și reporting
