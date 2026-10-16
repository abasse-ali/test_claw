# Budget Manager

Gestionnaire de budget mensuel - Revenus, Dépenses, Épargne

## Installation (version Flask / locale)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Lancement (version Flask / locale)

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

## Déploiement sur GitHub Pages (version statique)

Une version **100% statique** (HTML/CSS/JS, sans backend Python) est disponible dans le dossier `docs/` et utilise `localStorage` pour la persistance.

### Déploiement manuel

1. Poussez le dossier `docs/` sur la branche `gh-pages` ou activez GitHub Pages sur le dossier `docs/` de la branche `main` :
   - Settings → Pages → Source: "Deploy from a branch"
   - Branch: `main` / Folder: `/docs`
2. L'application sera accessible à `https://<votre-user>.github.io/<repo>/`

### Fonctionnalités de la version statique

Identiques à la version Flask, sauf :
- Pas de base de données SQLite (utilise `localStorage` du navigateur)
- Pas de flash messages côté serveur (notifications JS)
- Pas de CSRF (inutile sans backend)
- Calculs côté client avec `Math.round(value * 100) / 100` pour éviter les erreurs de virgule flottante

## Fonctionnalités

- **Revenus** : Ajout/suppression avec libellé, montant, date
- **Dépenses** : Ajout/suppression avec libellé, montant, date, catégorie optionnelle
- **Épargne** : Ajout/suppression avec libellé, montant, date
- **Solde net** : Calculé automatiquement (Revenus - Dépenses - Épargne)
- **Navigation mensuelle** : Mois précédent / suivant
- **Export CSV** : Téléchargement des données du mois
- **Persistance** : Base de données SQLite (budget.db) ou localStorage (version statique)
- **Précision décimale** : Pas d'erreurs de virgule flottante (utilise Decimal / Math.round)
- **Format français** : Affichage `1 234,56 €`
- **Validation** : Rejet montants ≤ 0, libellés vides, dates invalides