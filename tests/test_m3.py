"""
M3 Tests: Month Navigation + Export
Tests E9, E10
"""
import pytest
import tempfile
import os
import sys
from decimal import Decimal
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models import (
    init_db, get_entries, create_entry, delete_entry,
    get_totals, get_net_balance, get_current_month,
    get_month_bounds, export_csv,
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


# --- E9: Month navigation ---
def test_e9_get_month_bounds_january(temp_db):
    """Test month bounds for January."""
    first, last = get_month_bounds('2026-01')
    assert first == date(2026, 1, 1)
    assert last == date(2026, 1, 31)


def test_e9_get_month_bounds_february_leap(temp_db):
    """Test month bounds for February in leap year."""
    first, last = get_month_bounds('2024-02')
    assert first == date(2024, 2, 1)
    assert last == date(2024, 2, 29)


def test_e9_get_month_bounds_february_non_leap(temp_db):
    """Test month bounds for February in non-leap year."""
    first, last = get_month_bounds('2026-02')
    assert first == date(2026, 2, 1)
    assert last == date(2026, 2, 28)


def test_e9_get_month_bounds_december(temp_db):
    """Test month bounds for December."""
    first, last = get_month_bounds('2026-12')
    assert first == date(2026, 12, 1)
    assert last == date(2026, 12, 31)


def test_e9_entries_filtered_by_month(temp_db):
    """E9: Entries are filtered by month parameter."""
    # Add entries in October
    create_entry('income', 'Salaire Oct', Decimal('2500.00'), date(2026, 10, 1))
    create_entry('expense', 'Loyer Oct', Decimal('800.00'), date(2026, 10, 15))

    # Add entries in November
    create_entry('income', 'Salaire Nov', Decimal('2500.00'), date(2026, 11, 1))
    create_entry('expense', 'Loyer Nov', Decimal('800.00'), date(2026, 11, 15))

    # Query October
    oct_entries = get_entries('2026-10')
    assert len(oct_entries) == 2
    assert all(e['date'].startswith('2026-10') for e in oct_entries)

    # Query November
    nov_entries = get_entries('2026-11')
    assert len(nov_entries) == 2
    assert all(e['date'].startswith('2026-11') for e in nov_entries)

    # Totals are per month
    oct_totals = get_totals('2026-10')
    assert oct_totals['income'] == Decimal('2500.00')
    assert oct_totals['expense'] == Decimal('800.00')

    nov_totals = get_totals('2026-11')
    assert nov_totals['income'] == Decimal('2500.00')
    assert nov_totals['expense'] == Decimal('800.00')


# --- E10: CSV Export ---
def test_e10_export_csv_format(temp_db):
    """E10: CSV export produces correct format."""
    create_entry('income', 'Salaire', Decimal('2500.00'), date(2026, 10, 1))
    create_entry('expense', 'Loyer', Decimal('800.00'), date(2026, 10, 15), 'Logement')
    create_entry('savings', 'Livret A', Decimal('300.00'), date(2026, 10, 5))

    csv_data = export_csv('2026-10')
    lines = csv_data.strip().splitlines()

    # Check header
    assert lines[0] == 'Type;Libellé;Montant (€);Date;Catégorie'

    # Check data rows (3 entries)
    assert len(lines) == 4

    # Check income row (2026-10-01)
    income_row = next(l for l in lines[1:] if 'income' in l)
    assert 'Salaire' in income_row
    assert '2 500,00' in income_row
    assert '01/10/2026' in income_row

    # Check expense row with category (2026-10-15)
    expense_row = next(l for l in lines[1:] if 'expense' in l)
    assert 'Loyer' in expense_row
    assert '800,00' in expense_row
    assert '15/10/2026' in expense_row
    assert 'Logement' in expense_row

    # Check savings row (2026-10-05)
    savings_row = next(l for l in lines[1:] if 'savings' in l)
    assert 'Livret A' in savings_row
    assert '300,00' in savings_row
    assert '05/10/2026' in savings_row


def test_e10_export_csv_empty_month(temp_db):
    """E10: CSV export for empty month returns only header."""
    csv_data = export_csv('2026-10')
    lines = csv_data.strip().split('\n')
    assert len(lines) == 1
    assert lines[0] == 'Type;Libellé;Montant (€);Date;Catégorie'


def test_e10_export_csv_special_characters(temp_db):
    """E10: CSV handles special characters in labels."""
    create_entry('income', 'Salaire "Prime"', Decimal('1000.00'), date(2026, 10, 1))
    create_entry('expense', 'Courses, Supermarché', Decimal('50.00'), date(2026, 10, 2), 'Alimentation')

    csv_data = export_csv('2026-10')
    # CSV should be valid (quotes escaped by csv module)
    assert 'Salaire' in csv_data
    assert 'Courses' in csv_data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])