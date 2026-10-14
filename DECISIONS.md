# Price Comparator - Technical Decisions

## Language & Framework

- **Python 3.12 + FastAPI**: Modern async framework, excellent type hints, automatic OpenAPI docs, great ecosystem.
- **React 18 + TypeScript + Vite**: Industry standard, great DX, fast HMR, strong typing.
- **Tailwind CSS**: Utility-first, rapid UI development, small bundle, no context switching.

## Database

- **PostgreSQL 16 + asyncpg**: Robust, supports JSONB, PostGIS for geo queries (later), async driver for FastAPI.
- **SQLAlchemy 2.0 (async)**: Modern ORM, type-safe, declarative models, migration support via Alembic.
- **Decimal for prices**: `DECIMAL(10,2)` in DB, `Decimal` in Python/Pydantic. Quantize with `ROUND_HALF_UP` for storage. Avoids float errors (0.1+0.2=0.30000000000000004).

## Caching & Queue

- **Redis 7**: Celery broker, result backend, rate limiting, session cache.
- **Celery 5 + Redis**: Distributed task queue for scraping, alert checking. Beat scheduler for periodic tasks.
- **APScheduler alternative**: Celery beat chosen for persistence and distributed workers.

## Scraping

- **Playwright (Chromium)**: Handles JS-rendered pages, stealth mode, screenshots for debugging.
- **robots.txt compliance**: `robotparser` stdlib, check before each request.
- **Rate limiting**: Random delay 2-5s between requests per domain (configurable).
- **User-Agent**: `PriceComparator/1.0 (+https://example.com/bot)` identifying bot.
- **Selectors per supermarket**: JSON config (CSS/XPath) for product name, price, image, promotion, availability.
- **Mock scrapers for MVP**: Real scraping requires legal review, CAPTCHA handling, maintenance. Mock returns seeded data.

## Authentication

- **JWT (HS256)**: Stateless, short expiry (30 min), stored in HttpOnly cookie + localStorage for SPA.
- **bcrypt**: Slow salted hash via `passlib`, cost factor 12.
- **OAuth2PasswordBearer**: Standard FastAPI integration.
- **No refresh tokens in MVP**: Simpler, user re-logs in after expiry.

## Geo/Location

- **Haversine formula in SQL**: For nearby search without PostGIS extension (simpler deploy). Formula: `6371 * acos(cos(radians(lat1)) * cos(radians(lat2)) * cos(radians(lon2) - radians(lon1)) + sin(radians(lat1)) * sin(radians(lat2)))`.
- **OpenStreetMap Nominatim**: Free geocoding for address -> lat/lon (rate limited, cache results).

## Frontend Architecture

- **TanStack Query (React Query)**: Server state, caching, deduplication, background refetch.
- **React Router v6**: Client-side routing.
- **Zod + React Hook Form**: Validation, type-safe forms.
- **Recharts**: Price history charts (line/area).
- **Leaflet + React-Leaflet**: Supermarket map (free, no API key).

## Project Structure

```
price-comparator/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/    # Route handlers
│   │   ├── core/                # Config, DB, security
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic
│   │   ├── tasks/               # Celery tasks
│   │   ├── scraping/            # Scraper base + implementations
│   │   └── main.py              # FastAPI app
│   ├── alembic/                 # Migrations
│   ├── scripts/                 # Seed, utilities
│   ├── tests/                   # Pytest tests
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/            # API client
│   │   ├── contexts/
│   │   └── types/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── SPEC.md
├── PLAN.md
└── DECISIONS.md
```

## Configuration

- **Pydantic Settings**: `.env` file, validated, typed.
- **Environment-specific**: `.env.local`, `.env.production` (gitignored).
- **Secrets**: Never in code, always in env.

## Testing

- **pytest + pytest-asyncio**: Async test support.
- **httpx.AsyncClient**: FastAPI test client.
- **Testcontainers**: PostgreSQL, Redis for integration tests (optional, use local for speed).
- **Factory Boy**: Test data factories.
- **Coverage target**: >80% for services, >60% overall.

## Deployment (Future)

- **Docker Compose**: Local dev, single-server prod.
- **GitHub Actions**: CI (lint, type-check, test, build).
- **Reverse proxy**: Nginx/Traefik for SSL, static files.
- **Monitoring**: Prometheus + Grafana (later).

## Decisions from Review

- **PostGIS vs Haversine**: Kept Haversine in SQL for M1-M3 simplicity. PostGIS can be added later for better performance on large datasets. *Reason: Avoids extension dependency, works on any PostgreSQL.*
- **Real vs Mock Scraping**: Mock scrapers for MVP. *Reason: Legal compliance, CAPTCHA, maintenance burden. Framework ready for real implementation.*
- **Refresh Tokens**: Deferred. *Reason: Adds complexity (token rotation, storage, revocation). 30-min JWT + re-login acceptable for MVP.*
- **Push Notifications**: Out of scope. *Reason: Requires service workers, VAPID keys, browser permission UX. Email sufficient for MVP.*
- **Admin UI**: API-only. *Reason: Frontend effort better spent on user features. Admin can use Swagger UI or direct DB.*