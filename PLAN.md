# Price Comparator - Implementation Plan

## Milestones

### M1 - Walking Skeleton
**Requirements:** R1, R8, E2, E7, E8
**Verify:** `cd backend && python -m pytest tests/test_m1_skeleton.py -v`

- FastAPI app with health check endpoint
- Database connection (PostgreSQL async)
- Alembic migrations for all models
- Settings from .env
- Basic auth (register, login, JWT)
- User location update endpoint
- Docker Compose for local dev

---

### M2 - Supermarket & Product CRUD + Search
**Requirements:** R1, R2, R10, E1, E2
**Verify:** `cd backend && python -m pytest tests/test_m2_crud_search.py -v`

- Supermarket CRUD (admin)
- Supermarket nearby search with PostGIS-style distance calculation
- Category tree endpoint
- Product CRUD (admin)
- Product search with filters (query, category, brand, barcode, price range, location, radius, promotion, in_stock)
- Pagination
- Seed script for demo data

---

### M3 - Price Management & Comparison
**Requirements:** R3, E6, E12
**Verify:** `cd backend && python -m pytest tests/test_m3_prices.py -v`

- Price CRUD (admin/scraper)
- Price comparison endpoint (cheapest, most_expensive, average, spread)
- Decimal handling with quantize
- Promotion expiry logic
- Price stats per product

---

### M4 - Price History & Alerts
**Requirements:** R4, R5, R6, E3, E4, E9, E11
**Verify:** `cd backend && python -m pytest tests/test_m4_history_alerts.py -v`

- Price history recording (on price create/update)
- Price history endpoint with period filter
- Alert CRUD for authenticated users
- Alert validation (active product, limit, duplicates)
- Background alert checker job (Celery beat)
- Email notification stub

---

### M5 - Legal Scraping Engine
**Requirements:** R7, E5, E10
**Verify:** `cd backend && python -m pytest tests/test_m5_scraping.py -v`

- Scraping job model and endpoints
- Robots.txt parser and checker
- Rate limiting per domain (delay min/max)
- Playwright-based scraper base class
- Configurable selectors per supermarket (CSS/XPath)
- Mock scrapers for 3 chains (Carrefour, Leclerc, Auchan)
- Job status tracking (pending/running/completed/failed)
- Concurrent job prevention

---

### M6 - User Features & Polish
**Requirements:** R8, R9, E7, E8
**Verify:** `cd backend && python -m pytest tests/test_m6_users.py -v`

- User profile management
- Favorites (products, supermarkets)
- Password change
- Token refresh (optional)
- API documentation (Swagger UI)
- Input validation hardening
- Rate limiting on auth endpoints

---

### M7 - Frontend (React + TypeScript)
**Requirements:** R1-R9 (UI for all)
**Verify:** `cd frontend && npm run build && npm run test`

- Vite + React 18 + TypeScript + Tailwind CSS
- Pages: Home, Search, Product Detail, Comparison, History Chart, Alerts, Favorites, Profile, Login/Register
- Components: ProductCard, PriceList, HistoryChart (Recharts), AlertForm, SupermarketMap (Leaflet)
- State management: React Query (TanStack Query) for server state
- Auth context with JWT storage
- Geolocation API for nearby search
- Responsive design
- PWA manifest

---

## Demo

**Install:**
```bash
# Clone and setup
git clone <repo>
cd price-comparator

# Backend
cd backend
cp .env.example .env
# Edit .env with DATABASE_URL, REDIS_URL, SECRET_KEY
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
alembic upgrade head
python scripts/seed.py

# Frontend
cd ../frontend
npm install
```

**Run:**
```bash
# Terminal 1: PostgreSQL & Redis (Docker)
docker compose up -d postgres redis

# Terminal 2: Backend
cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000

# Terminal 3: Celery worker
cd backend && source venv/bin/activate && celery -A app.worker.celery_app worker --loglevel=info

# Terminal 4: Celery beat (scheduler)
cd backend && source venv/bin/activate && celery -A app.worker.celery_app beat --loglevel=info

# Terminal 5: Frontend
cd frontend && npm run dev
```

**Test:** Open http://localhost:5173 - Search "lait", see nearby supermarkets, compare prices, view history, create alert.