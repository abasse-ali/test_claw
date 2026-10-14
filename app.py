"""
Flask application for budget manager.
"""
import os
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, flash, make_response
from models import (
    init_db, get_entries, create_entry, delete_entry,
    get_totals, get_net_balance, get_current_month,
    parse_amount, parse_date, validate_date_in_month,
    format_amount, format_date, export_csv, cents_to_amount
)
import models

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')


@app.before_request
def ensure_db():
    """Initialize database on first request."""
    if not os.path.exists(models.DB_PATH):
        init_db()


def get_month_param() -> str:
    """Get month from query param or default to current month."""
    month = request.args.get('month')
    if month:
        try:
            # Validate format
            parse_date(month + '-01')
            return month
        except ValueError:
            pass
    return get_current_month()


def get_prev_next_month(month_str: str) -> tuple[str, str]:
    """Get previous and next month strings from YYYY-MM."""
    year, month = map(int, month_str.split('-'))
    # Previous month
    if month == 1:
        prev = f"{year - 1}-12"
    else:
        prev = f"{year}-{month - 1:02d}"
    # Next month
    if month == 12:
        nxt = f"{year + 1}-01"
    else:
        nxt = f"{year}-{month + 1:02d}"
    return prev, nxt


@app.route('/')
def index():
    """Main budget view."""
    month = get_month_param()
    prev_month, next_month = get_prev_next_month(month)
    entries = get_entries(month)
    totals = get_totals(month)
    net = get_net_balance(month)

    # Group entries by type
    by_type = {'income': [], 'expense': [], 'savings': []}
    for e in entries:
        e['formatted_amount'] = format_amount(cents_to_amount(e['amount_cents']))
        e['formatted_date'] = format_date(parse_date(e['date']))
        by_type[e['type']].append(e)

    return render_template('index.html',
                           month=month,
                           prev_month=prev_month,
                           next_month=next_month,
                           entries_by_type=by_type,
                           totals=totals,
                           net_balance=net,
                           format_amount=format_amount)


@app.route('/add', methods=['POST'])
def add_entry():
    """Add a new entry."""
    month = get_month_param()
    entry_type = request.form.get('type')
    label = request.form.get('label', '').strip()
    amount_str = request.form.get('amount', '').strip()
    date_str = request.form.get('date', '').strip()
    category = request.form.get('category', '').strip() or None

    try:
        amount = parse_amount(amount_str)
        entry_date = validate_date_in_month(date_str, month)
        create_entry(entry_type, label, amount, entry_date, category)
        flash('Entrée ajoutée', 'success')
    except ValueError as e:
        flash(str(e), 'error')

    return redirect(url_for('index', month=month))


@app.route('/delete/<int:entry_id>', methods=['POST'])
def delete_entry_route(entry_id):
    """Delete an entry."""
    month = get_month_param()
    if delete_entry(entry_id):
        flash('Entrée supprimée', 'success')
    else:
        flash('Entrée introuvable', 'error')
    return redirect(url_for('index', month=month))


@app.route('/export')
def export_csv_route():
    """Export current month as CSV."""
    month = get_month_param()
    csv_data = export_csv(month)
    response = make_response(csv_data)
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename=budget-{month}.csv'
    return response


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)