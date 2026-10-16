# Budget Manager - Decisions

- Language: Python 3.12 with Flask - simple, no build step, good standard library support for Decimal and SQLite
- Web framework: Flask - lightweight, built-in dev server, Jinja2 templates for server-side rendering
- Storage: SQLite (file `budget.db`) - zero-config, persists between runs, ACID transactions
- Decimal handling: `decimal.Decimal` with `quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)` for all monetary calculations - avoids floating-point errors
- Date handling: `datetime.date` - ISO format (YYYY-MM-DD) in forms and URLs, French display format (DD/MM/YYYY)
- Input parsing: Accept both comma and dot as decimal separator via `str.replace(",", ".")` before Decimal construction
- Frontend: Server-rendered HTML with minimal vanilla JS for form validation and confirmation dialogs - no npm, no build step
- Templates: Jinja2 with template inheritance (base.html) - DRY, maintainable
- CSS: Embedded in base.html for simplicity - single file deploy
- Testing: pytest with Flask test client - unit tests for models, integration tests for routes
- Project structure:
  ```
  app.py              # Flask app, routes
  models.py           # Database models, Decimal helpers
  schema.sql          # SQLite schema
  requirements.txt    # Dependencies
  templates/
    base.html         # Base template with CSS
    index.html        # Main budget view
  tests/
    test_m1.py        # M1 tests
    test_m2.py        # M2 tests
    test_m3.py        # M3 tests
  ```
- Month navigation: URL parameter `?month=YYYY-MM` defaults to current month
- CSRF protection: Flask-WTF not used (overhead for this scope); same-origin POST forms with simple token in session