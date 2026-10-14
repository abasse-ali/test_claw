"""
Database models and Decimal helpers for budget manager.
All monetary values stored as integer cents to avoid floating-point errors.
"""
import sqlite3
import os
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(__file__), 'budget.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')

# Decimal quantize for 2 decimal places (cents)
CENTS = Decimal('0.01')


def get_db() -> sqlite3.Connection:
    """Get a database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize the database with schema."""
    with get_db() as conn:
        with open(SCHEMA_PATH, 'r') as f:
            conn.executescript(f.read())
        conn.commit()


@contextmanager
def transaction():
    """Context manager for database transactions."""
    conn = get_db()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def parse_amount(amount_str: str) -> Decimal:
    """
    Parse amount string to Decimal, accepting both comma and dot as decimal separator.
    Raises ValueError if invalid, zero, or negative.
    """
    if not amount_str or not amount_str.strip():
        raise ValueError("Montant requis")
    # Replace comma with dot, remove spaces
    cleaned = amount_str.strip().replace(',', '.').replace(' ', '')
    try:
        amount = Decimal(cleaned).quantize(CENTS, rounding=ROUND_HALF_UP)
    except Exception:
        raise ValueError("Montant invalide")
    if amount <= 0:
        raise ValueError("Le montant doit être positif")
    return amount


def amount_to_cents(amount: Decimal) -> int:
    """Convert Decimal amount to integer cents."""
    return int((amount * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))


def cents_to_amount(cents: int) -> Decimal:
    """Convert integer cents to Decimal amount."""
    return Decimal(cents) / 100


def format_amount(amount: Decimal) -> str:
    """Format Decimal amount as French string: '1 234,56 €'."""
    # Ensure exactly 2 decimal places
    amount = amount.quantize(CENTS, rounding=ROUND_HALF_UP)
    # Format with space as thousand separator, comma as decimal
    s = f"{amount:,.2f}".replace(',', ' ').replace('.', ',')
    return f"{s} €"


def parse_date(date_str: str) -> date:
    """Parse ISO date string (YYYY-MM-DD) to date object."""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise ValueError("Date invalide (format attendu: YYYY-MM-DD)")


def format_date(d: date) -> str:
    """Format date as French string: DD/MM/YYYY."""
    return d.strftime('%d/%m/%Y')


def get_current_month() -> str:
    """Get current month as YYYY-MM string."""
    return date.today().strftime('%Y-%m')


def get_month_bounds(month_str: str) -> tuple[date, date]:
    """Get first and last day of month from YYYY-MM string."""
    year, month = map(int, month_str.split('-'))
    first = date(year, month, 1)
    if month == 12:
        last = date(year + 1, 1, 1)
    else:
        last = date(year, month + 1, 1)
    # Last day is day before first of next month
    from datetime import timedelta
    last = last - timedelta(days=1)
    return first, last


def validate_date_in_month(date_str: str, month_str: str) -> date:
    """Validate date is within the given month."""
    d = parse_date(date_str)
    first, last = get_month_bounds(month_str)
    if not (first <= d <= last):
        raise ValueError(f"La date doit être dans le mois {month_str}")
    return d


# --- Entry CRUD ---

def create_entry(
    entry_type: str,
    label: str,
    amount: Decimal,
    entry_date: date,
    category: Optional[str] = None
) -> int:
    """Create a new entry, return its ID."""
    if entry_type not in ('income', 'expense', 'savings'):
        raise ValueError("Type invalide")
    if not label or not label.strip():
        raise ValueError("Le libellé est requis")
    if amount <= 0:
        raise ValueError("Le montant doit être positif")

    with transaction() as conn:
        cursor = conn.execute(
            '''INSERT INTO entries (type, label, amount_cents, date, category)
               VALUES (?, ?, ?, ?, ?)''',
            (entry_type, label.strip(), amount_to_cents(amount), entry_date.isoformat(), category)
        )
        return cursor.lastrowid


def get_entries(month_str: str) -> List[Dict[str, Any]]:
    """Get all entries for a given month."""
    first, last = get_month_bounds(month_str)
    with get_db() as conn:
        rows = conn.execute(
            '''SELECT * FROM entries
               WHERE date >= ? AND date <= ?
               ORDER BY date, id''',
            (first.isoformat(), last.isoformat())
        ).fetchall()
    return [dict(row) for row in rows]


def get_entry(entry_id: int) -> Optional[Dict[str, Any]]:
    """Get a single entry by ID."""
    with get_db() as conn:
        row = conn.execute('SELECT * FROM entries WHERE id = ?', (entry_id,)).fetchone()
    return dict(row) if row else None


def delete_entry(entry_id: int) -> bool:
    """Delete an entry by ID. Returns True if deleted."""
    with transaction() as conn:
        cursor = conn.execute('DELETE FROM entries WHERE id = ?', (entry_id,))
    return cursor.rowcount > 0


def get_totals(month_str: str) -> Dict[str, Decimal]:
    """Get totals for income, expenses, savings for a month."""
    entries = get_entries(month_str)
    totals = {'income': Decimal('0'), 'expense': Decimal('0'), 'savings': Decimal('0')}
    for e in entries:
        amount = cents_to_amount(e['amount_cents'])
        totals[e['type']] += amount
    return totals


def get_net_balance(month_str: str) -> Decimal:
    """Calculate net balance: income - expenses - savings."""
    totals = get_totals(month_str)
    return totals['income'] - totals['expense'] - totals['savings']


def export_csv(month_str: str) -> str:
    """Export all entries for a month as CSV string."""
    import csv
    import io

    entries = get_entries(month_str)
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    # Header
    writer.writerow(['Type', 'Libellé', 'Montant (€)', 'Date', 'Catégorie'])
    for e in entries:
        amount = cents_to_amount(e['amount_cents'])
        writer.writerow([
            e['type'],
            e['label'],
            format_amount(amount).replace(' €', ''),
            format_date(parse_date(e['date'])),
            e['category'] or ''
        ])
    return output.getvalue()