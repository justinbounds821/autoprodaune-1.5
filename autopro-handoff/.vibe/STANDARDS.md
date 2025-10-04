# STANDARDS – Reguli de Execuție

Aceste reguli asigură consistență, mentenabilitate și scalabilitate în codul AutoPro Daune. Sunt bazate pe best practices + constrângeri specifice proiectului.

---

## 1. File Length & Structure

**Regulă:** Max **500 linii/fișier**. Split when approaching **400**.

**Motivație:**
- Fișiere mari (1000+ linii) devin god classes/modules
- Dificil de navigat, reviewuit, testat
- Merge conflicts frecvente

**Aplicare:**
```python
# ❌ BAD: services/video_generator.py – 1200 linii
class VideoGenerator:
    def generate(self): ...  # 300 linii
    def upload(self): ...     # 400 linii
    def watermark(self): ...  # 500 linii

# ✅ GOOD: split în module separate
# services/video/generator.py – 300 linii
# services/video/uploader.py – 250 linii
# services/video/watermark.py – 200 linii
```

**Excepții:**
- Generated code (ex: openapi types)
- Config/constants files (acceptabil până la 800 linii dacă sunt doar definiții)

---

## 2. Function & Class Size

**Regulă:**
- Funcții: max **40 linii** (ideal <25)
- Clase: max **200 linii** (ideal <150)
- Metode de clasă: max **30 linii**

**Motivație:**
- Funcții lungi = multiple responsabilități (violează SRP)
- Hard to test, hard to debug
- Cognitive load prea mare

**Aplicare:**
```typescript
// ❌ BAD: funcție de 150 linii care face totul
async function processPayment(data: any) {
  // validare 20 linii
  // calcul taxe 30 linii
  // update DB 40 linii
  // trimitere email 30 linii
  // logging 30 linii
}

// ✅ GOOD: split în funcții specializate
async function processPayment(data: PaymentData) {
  const validated = validatePayment(data);  // 15 linii
  const withTaxes = calculateTaxes(validated);  // 20 linii
  const saved = await savePayment(withTaxes);  // 10 linii
  await notifyUser(saved);  // 10 linii
  logPaymentEvent(saved);  // 5 linii
  return saved;
}
```

**Tool:** eslint rule `max-lines-per-function: 40`, pylint `max-function-lines: 40`

---

## 3. Single Responsibility Principle (SRP)

**Regulă:** O funcție/clasă face **UN singur lucru** și îl face bine.

**Anti-pattern:** "Și mai..."
```python
# ❌ BAD
def create_user_and_send_email_and_log(user_data):
    user = User(**user_data)
    db.add(user)
    db.commit()
    send_email(user.email, "Welcome")
    logger.info(f"Created user {user.id}")
    return user

# ✅ GOOD
def create_user(user_data):
    user = User(**user_data)
    db.add(user)
    db.commit()
    return user

# Separat:
email_service.send_welcome(user)
logger.info(f"Created user {user.id}")
```

**Test:** Dacă numele funcției conține "and", probabil încalci SRP.

---

## 4. Modular Design & Avoid God Classes

**Regulă:** Clasele cu >10 metode publice sunt suspecte. Split în module/services.

**Exemplu:**
```python
# ❌ BAD: god class
class AutoProService:
    def get_leads(self): ...
    def create_lead(self): ...
    def get_payments(self): ...
    def create_payment(self): ...
    def generate_video(self): ...
    def upload_video(self): ...
    def send_notification(self): ...
    def calculate_roi(self): ...
    # ... 50 metode

# ✅ GOOD: module separate
class LeadService:
    def get(self): ...
    def create(self): ...

class PaymentService:
    def get(self): ...
    def create(self): ...

class VideoService:
    def generate(self): ...
    def upload(self): ...
```

**Organizare:**
```
services/
├── leads/
│   ├── service.py
│   ├── repository.py
│   └── schemas.py
├── payments/
│   ├── service.py
│   ├── repository.py
│   └── schemas.py
└── video/
    ├── generator.py
    ├── uploader.py
    └── schemas.py
```

---

## 5. Naming & Readability

**Regulă:** Nume clare, fără abrevieri obscure.

**Anti-patterns:**
- `data`, `info`, `temp`, `obj`, `thing` → prea generic
- `d`, `x`, `tmp` → prea scurt (OK doar în lambda/comprehension)
- `getUserDataFromDatabaseAndReturnAsJson` → prea lung (simplify)

**Examples:**
```python
# ❌ BAD
def get_data(id):
    info = db.query(Thing).filter(Thing.id == id).first()
    return info

# ✅ GOOD
def get_lead_by_id(lead_id: int) -> Lead:
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    return lead
```

**Conventions:**
- Python: `snake_case` pentru funcții/variabile, `PascalCase` pentru clase
- TypeScript: `camelCase` pentru funcții/variabile, `PascalCase` pentru clase/interfaces
- SQL: `snake_case` pentru tabele/coloane

---

## 6. Scalability Mindset

**Regulă:** Gândește la 10x load când scrii cod.

**Questions:**
- Dacă am 10k requests/min în loc de 100, codul ține?
- Dacă tabelul are 10M rows, query-ul e eficient?
- Dacă sunt 100 users concurenți, apar race conditions?

**Patterns:**
- **Pagination:** ÎNTOTDEAUNA pentru liste (default `limit=50`, max `limit=1000`)
- **Indexes:** pe coloane folosite în WHERE/JOIN
- **Caching:** Redis pentru date read-heavy (ex: avatars list)
- **Rate limiting:** protejează endpoints costisitori (ex: video generation)
- **Async:** folosește `async/await` pentru I/O operations

```python
# ❌ BAD: load toate lead-urile în memorie
def get_all_leads():
    return db.query(Lead).all()  # 💥 dacă sunt 1M leads

# ✅ GOOD: pagination
def get_leads(page: int = 1, limit: int = 50):
    offset = (page - 1) * limit
    leads = db.query(Lead).offset(offset).limit(limit).all()
    total = db.query(Lead).count()
    return {"items": leads, "total": total, "page": page, "limit": limit}
```

---

## 7. Dependency Injection (unde are sens)

**Regulă:** Injectează dependențele în loc de hardcodare.

**Motivație:**
- Testabilitate (mock DB, services)
- Flexibilitate (swap implementations)
- Decoupling

```python
# ❌ BAD: hardcoded
class LeadService:
    def create(self, data):
        db = get_database()  # hardcoded
        lead = Lead(**data)
        db.add(lead)
        db.commit()
        send_email(lead.email, "Welcome")  # hardcoded

# ✅ GOOD: dependency injection
class LeadService:
    def __init__(self, db: Database, email_service: EmailService):
        self.db = db
        self.email_service = email_service

    def create(self, data):
        lead = Lead(**data)
        self.db.add(lead)
        self.db.commit()
        self.email_service.send_welcome(lead.email)

# Injecție în FastAPI:
@app.post("/api/leads")
def create_lead(data: LeadCreate, db: Database = Depends(get_db)):
    service = LeadService(db, email_service)
    return service.create(data)
```

**Atenție:** Nu abuza de DI pentru lucruri simple (ex: `datetime.now()` nu trebuie injectat mereu).

---

## 8. Error Handling & Logging

**Regulă:**
- Catch specific exceptions, nu `except Exception` peste tot
- Log la nivel potrivit: DEBUG/INFO/WARNING/ERROR
- User-facing errors trebuie să fie friendly (nu stack traces)

```python
# ❌ BAD
try:
    user = get_user(id)
except:  # prea larg
    pass  # pierde eroarea

# ✅ GOOD
try:
    user = get_user(user_id)
except UserNotFoundError:
    logger.warning(f"User {user_id} not found")
    raise HTTPException(404, "User not found")
except DatabaseError as e:
    logger.error(f"DB error fetching user {user_id}: {e}")
    raise HTTPException(500, "Internal server error")
```

**Log levels:**
- **DEBUG:** detalii pentru development (`logger.debug(f"Query: {sql}")`)
- **INFO:** evenimente normale (`logger.info("User created")`)
- **WARNING:** ceva suspect dar non-fatal (`logger.warning("Redis unavailable, using in-memory")`)
- **ERROR:** erori care afectează funcționalitatea (`logger.error("Failed to send email")`)

---

## 9. Testing Mindset (chiar dacă nu scriem teste acum)

**Regulă:** Scrie cod care **poate fi testat**.

**Signs of testable code:**
- Funcții pure (no side effects când e posibil)
- Dependințe injectate (nu hardcoded)
- Single responsibility (test 1 thing per test)

```python
# ❌ HARD TO TEST
def calculate_total():
    items = db.query(Item).all()  # hardcoded DB
    total = sum(i.price for i in items)
    return total

# ✅ EASY TO TEST
def calculate_total(items: List[Item]) -> float:
    return sum(i.price for i in items)

# Test:
def test_calculate_total():
    items = [Item(price=10), Item(price=20)]
    assert calculate_total(items) == 30
```

---

## 10. Commit Policy (din CONTRACT.json)

**Regulă:**
- Max **200 linii schimbate** per commit
- Format conventional: `feat|fix|refactor|docs(scope): message`
- Commits trebuie să fie atomic (1 schimbare logică = 1 commit)

**Examples:**
```
✅ feat(payments): add update and delete endpoints
✅ fix(heygen): handle missing API key gracefully
✅ refactor(api-client): unify error handling
✅ docs(handoff): add integration spec and troubleshooting
❌ update stuff  (prea vag)
❌ feat: add 15 new features (prea mare, split)
```

**Tool:** pre-commit hook pentru validare automată.

---

## Summary Checklist

Înainte de commit/PR, verifică:
- [ ] Niciun fișier >500 linii (split dacă >400)
- [ ] Nicio funcție >40 linii (split dacă >30)
- [ ] Nicio clasă >200 linii
- [ ] Nume clare (fără `data`, `info`, `temp`, `x`)
- [ ] Single responsibility (fiecare funcție face 1 lucru)
- [ ] Error handling specific (nu `except Exception` peste tot)
- [ ] Logging la nivel potrivit (DEBUG/INFO/WARNING/ERROR)
- [ ] Pagination pentru liste (default `limit=50`)
- [ ] Conventional commits (`feat|fix|...`)
- [ ] Max 200 LOC per commit

**Motto:** "Code is read 10x more than it's written. Optimize for readability."
