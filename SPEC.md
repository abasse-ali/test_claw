# Price Comparator - Specification

## Requirements

### Core Features

**R1: Supermarket Management** - Users can view supermarkets near their location.
- Check: `curl -s http://localhost:8000/api/v1/supermarkets/nearby?lat=48.8566&lon=2.3522&radius=10` -> Returns JSON list of supermarkets with distance_km

**R2: Product Search** - Users can search products by name, category, brand, or barcode.
- Check: `curl -s "http://localhost:8000/api/v1/products/search?q=lait&lat=48.8566&lon=2.3522&radius=10"` -> Returns paginated products with current prices at nearby supermarkets

**R3: Price Comparison** - For a given product, show prices across supermarkets with cheapest highlighted.
- Check: `curl -s http://localhost:8000/api/v1/products/1/comparison` -> Returns product with prices array, cheapest, most_expensive, average_price, price_spread

**R4: Price History** - Show price evolution over time for a product at a supermarket.
- Check: `curl -s http://localhost:8000/api/v1/products/1/history?supermarket_id=1&days=30` -> Returns history points with date, price, original_price, is_promotion, supermarket_name

**R5: Price Alerts** - Authenticated users can create alerts for price drops below target.
- Check: `curl -X POST -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d '{"product_id":1,"target_price":2.50}' http://localhost:8000/api/v1/alerts` -> Returns created alert with id

**R6: Alert Triggering** - Background job checks prices and triggers alerts when price <= target.
- Check: Run alert checker job manually -> Alerts with last_triggered_at updated, email notification queued

**R7: Legal Scraping** - Scrape supermarket websites respecting robots.txt, with delays, user-agent.
- Check: `curl -X POST -H "Authorization: Bearer <admin_token>" -H "Content-Type: application/json" -d '{"supermarket_id":1}' http://localhost:8000/api/v1/scraping/jobs` -> Returns job with status "running", then "completed" with products_scraped > 0

**R8: User Location** - Users can set their location for nearby supermarket search.
- Check: `curl -X PATCH -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d '{"latitude":48.8566,"longitude":2.3522}' http://localhost:8000/api/v1/users/me` -> Returns updated user with location

**R9: Favorites** - Users can favorite products and supermarkets for quick access.
- Check: `curl -X POST -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d '{"product_id":1}' http://localhost:8000/api/v1/favorites/products` -> Returns favorite entry

**R10: Categories** - Hierarchical category tree for product organization.
- Check: `curl -s http://localhost:8000/api/v1/categories/tree` -> Returns nested category tree

### Edge Cases

**E1: Empty Search** - Search with no results returns empty paginated response, not error.
- Check: `curl -s "http://localhost:8000/api/v1/products/search?q=xyznonexistent"` -> Returns `{items:[],total:0,page:1,page_size:20,total_pages:0}`

**E2: Invalid Coordinates** - Latitude/longitude outside valid ranges rejected with 422.
- Check: `curl -s "http://localhost:8000/api/v1/supermarkets/nearby?lat=91&lon=2.3522"` -> Returns 422 validation error

**E3: Duplicate Alert** - User cannot create two alerts for same product+supermarket+target.
- Check: Create alert twice -> Second request returns 409 Conflict

**E4: Alert for Inactive Product** - Creating alert for inactive product returns 404.
- Check: Create alert for product with is_active=false -> Returns 404

**E5: Scraping Respects Robots.txt** - Scraping job fails gracefully if robots.txt disallows.
- Check: Configure supermarket with disallowed path -> Job status becomes "failed" with error message

**E6: Price Precision** - Prices stored and returned as Decimal with 2 places, no floating point errors.
- Check: Create price 2.675 -> Stored as 2.67, returned as "2.67"

**E7: Unauthorized Access** - Protected endpoints return 401 without valid token.
- Check: `curl -s http://localhost:8000/api/v1/alerts` -> Returns 401

**E8: Expired Token** - Token past expiry returns 401.
- Check: Use token expired >30 min ago -> Returns 401

**E9: Self-Alert Limit** - User cannot exceed max_alerts_per_user (default 50).
- Check: Create 51st alert -> Returns 400 with limit message

**E10: Concurrent Scraping** - Only one scraping job per supermarket at a time.
- Check: Start second job for same supermarket -> Returns 409 Conflict

**E11: Price History Retention** - Price history kept for at least 1 year.
- Check: Query history with days=365 -> Returns data

**E12: Promotion Expiry** - Expired promotions not shown as current promotions.
- Check: Query prices where promotion_end_date < now -> is_promotion=false in response

### Questions

1. **Which supermarkets to support initially?** -> Start with 3 major French chains (Carrefour, Leclerc, Auchan) with mock data, scraping selectors configurable per supermarket.

2. **Frontend framework?** -> React with TypeScript, Vite, Tailwind CSS for rapid development.

3. **Deployment target?** -> Docker Compose for local dev (PostgreSQL, Redis, backend, frontend, Celery worker, Celery beat).

4. **Real scraping vs mock?** -> Implement scraping framework with Playwright, but use mock scrapers for demo (real scraping requires handling CAPTCHAs, dynamic content, legal review).

5. **Notifications?** -> Email via SMTP (configured in .env), push notifications out of scope for MVP.

6. **Authentication?** -> JWT with bcrypt password hashing, refresh tokens out of scope.

7. **Admin interface?** -> API-only for MVP, admin endpoints protected by role.

### Out of Scope

- Mobile app (PWA is sufficient)
- Real-time price updates (WebSockets)
- Multi-language support (French only for MVP)
- Price prediction/ML
- Shopping list / cart functionality
- User reviews/ratings
- Barcode scanning from camera
- Loyalty card integration
- Price comparison across countries
- Affiliate links / monetization