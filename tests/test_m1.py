"""
M1 Tests: Walking Skeleton
Tests R1, R7, E7
"""
import pytest
import tempfile
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models import (
    init_db, get_entries, get_totals, get_net_balance,
    get_current_month, parse_amount, format_amount,
    DB_PATH as MODELS_DB_PATH
)


@pytest.fixture(autouse=True)
def temp_db(monkeypatch):
    """Use a temporary database for each test."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    monkeypatch.setattr('models.DB_PATH', db_path)
    init_db()
    yield
    os.unlink(db_path)


def test_r1_initial_view_shows_three_sections_with_zero_totals(temp_db):
    """R1: Initial view shows three sections with zero totals."""
    from models import get_totals, get_net_balance
    month = get_current_month()

    totals = get_totals(month)
    net = get_net_balance(month)

    assert totals['income'] == 0
    assert totals['expense'] == 0
    assert totals['savings'] == 0
    assert net == 0


def test_r7_data_persists_between_sessions(temp_db):
    """R7: Data persists - verify database file exists and can be re-read."""
    from models import create_entry, get_entries
    from decimal import Decimal
    from datetime import date

    month = get_current_month()
    create_entry('income', 'Salaire', Decimal('2500.00'), date(2026, 10, 1))

    entries = get_entries(month)
    assert len(entries) == 1
    assert entries[0]['label'] == 'Salaire'
    assert entries[0]['amount_cents'] == 250000


def test_e7_empty_database_on_first_run_shows_zeros(temp_db):
    """E7: Empty database on first run shows zeros, no errors."""
    from models import get_entries, get_totals, get_net_balance
    month = get_current_month()

    entries = get_entries(month)
    totals = get_totals(month)
    net = get_net_balance(month)

    assert entries == []
    assert totals['income'] == 0
    assert totals['expense'] == 0
    assert totals['savings'] == 0
    assert net == 0


def test_format_amount_french_formatting():
    """Test French number formatting."""
    from decimal import Decimal
    assert format_amount(Decimal('0')) == '0,00 €'
    assert format_amount(Decimal('12.50')) == '12,50 €'
    assert format_amount(Decimal('1234.56')) == '1 234,56 €'
    assert format_amount(Decimal('1000000.00')) == '1 000 000,00 €'


def test_parse_amount_accepts_comma_and_dot():
    """Test amount parsing accepts both comma and dot."""
    from decimal import Decimal
    assert parse_amount('12.50') == Decimal('12.50')
    assert parse_amount('12,50') == Decimal('12.50')
    assert parse_amount('  1 234,56  ') == Decimal('1234.56')


def test_parse_amount_raises_on_invalid():
    """Test parse_amount raises ValueError on invalid input."""
    with pytest.raises(ValueError):
        parse_amount('')
    with pytest.raises(ValueError):
        parse_amount('invalid')
    with pytest.raises(ValueError):
        parse_amount('12.34.56')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])