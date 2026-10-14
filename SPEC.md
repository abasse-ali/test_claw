# Budget Manager - Specification

## Requirements

R1: The application displays a monthly budget view with income, expenses, and savings sections. Check: Open the web app -> shows three sections labeled "Revenus", "Dépenses", "Épargne" with empty lists and totals at 0.00 €

R2: User can add an income entry with a label, amount, and date. Check: Submit "Salaire", "2500.00", "2026-10-01" via the income form -> entry appears in Revenus list with label "Salaire", amount "2 500,00 €", date "2026-10-01", and total Revenus updates to "2 500,00 €"

R3: User can add an expense entry with a label, amount, date, and category. Check: Submit "Loyer", "800.00", "2026-10-01", "Logement" via the expense form -> entry appears in Dépenses list with label "Loyer", amount "800,00 €", date "2026-10-01", category "Logement", and total Dépenses updates to "800,00 €"

R4: User can add a savings entry with a label, amount, and date. Check: Submit "Livret A", "300.00", "2026-10-05" via the savings form -> entry appears in Épargne list with label "Livret A", amount "300,00 €", date "2026-10-05", and total Épargne updates to "300,00 €"

R5: The application calculates and displays the net balance (Income - Expenses - Savings). Check: After R2, R3, R4 -> Net balance shows "1 400,00 €" (2500 - 800 - 300)

R6: User can delete an entry from any section. Check: Delete the "Loyer" expense -> entry disappears from Dépenses list, total Dépenses returns to "0,00 €", net balance updates to "2 800,00 €"

R7: Data persists between browser sessions (page reload). Check: Reload the page after adding entries -> all entries and totals remain visible

R8: Amounts accept both comma and dot as decimal separators. Check: Submit "12,50" and "12.50" -> both stored as 12.50 € and displayed as "12,50 €"

R9: Amounts are computed using Decimal (no floating-point errors). Check: Add three entries of "0.10" -> total shows "0,30 €" exactly (not 0.30000000000000004)

R10: Amounts display with French formatting (space as thousand separator, comma as decimal). Check: Add "1234.56" -> displays as "1 234,56 €"

R11: The application validates input: rejects empty label, zero/negative amount, invalid date, future date beyond current month. Check: Submit empty label -> error "Le libellé est requis"; submit "0" or "-10" -> error "Le montant doit être positif"; submit "invalid-date" -> error "Date invalide"; submit next month date -> error "La date doit être dans le mois en cours"

## Edge Cases

E1: Adding 100 split in three entries (33.33, 33.33, 33.34) -> total shows exactly "100,00 €"
E2: Adding "2.665" -> displays as "2,67 €" (ROUND_HALF_UP)
E3: Adding zero amount -> rejected with "Le montant doit être positif"
E4: Adding negative amount -> rejected with "Le montant doit être positif"
E5: Duplicate submission (double-click submit) -> only one entry created
E6: JSON serialization of Decimal values works without TypeError
E7: Empty database on first run -> shows zeros, no errors
E8: Category field optional for expenses -> works without category
E9: Month navigation (previous/next month) -> loads entries for that month, URL updates with month parameter
E10: CSV export of current month data -> downloads file with all entries

## Questions

- Language: Python with Flask (simple, built-in dev server, good for this scope)
- Storage: SQLite (file-based, no separate server, persists between runs)
- Frontend: Server-rendered HTML with vanilla JS for interactions (no build step)
- Decimal handling: Python's `decimal.Decimal` with `quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`
- Date handling: Current month by default, user can navigate months

## Out of Scope

- User authentication / multi-user
- Recurring transactions
- Budget limits / alerts
- Charts / visualizations
- Import from bank files (OFX, CSV)
- Mobile app