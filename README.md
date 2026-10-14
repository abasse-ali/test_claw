# Budget Manager

Gestionnaire de budget mensuel - Revenus, Dépenses, Épargne

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Lancement

```bash
python3 app.py
```

Puis ouvrez http://localhost:5000 dans votre navigateur.

## Test de démarrage (démo)

```bash
python3 demo.py
```

## Tests

```bash
python3 -m pytest tests/ -v
```

## Fonctionnalités

- **Revenus** : Ajout/suppression avec libellé, montant, date
- **Dépenses** : Ajout/suppression avec libellé, montant, date, catégorie optionnelle
- **Épargne** : Ajout/suppression avec libellé, montant, date
- **Solde net** : Calculé automatiquement (Revenus - Dépenses - Épargne)
- **Navigation mensuelle** : Mois précédent / suivant
- **Export CSV** : Téléchargement des données du mois
- **Persistance** : Base de données SQLite (budget.db)
- **Précision décimale** : Pas d'erreurs de virgule flottante (utilise Decimal)
- **Format français** : Affichage `1 234,56 €`
- **Validation** : Rejet montants ≤ 0, libellés vides, dates invalides