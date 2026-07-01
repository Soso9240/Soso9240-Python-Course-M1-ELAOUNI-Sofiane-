# DevOps Monitoring Dashboard

Système de monitoring temps réel construit en Python : une API FastAPI qui expose des métriques
système et gère une liste de serveurs surveillés, et un dashboard Streamlit qui les affiche en direct.

## Architecture

- **`devops-monitor-api`** (FastAPI, port 8000) — `/health`, `/metrics`, WebSocket `/ws/metrics`,
  CRUD `/servers` protégé par clé API.
- **`devops-monitor-dashboard`** (Streamlit, port 8501) — onglet Métriques (KPIs + graphique live)
  et onglet Serveurs (tableau coloré par statut + formulaire d'enregistrement).

Les deux services communiquent via Docker Compose, jamais par `localhost`.

## Prérequis

- Python 3.11
- Docker + Docker Compose
- `make`

## Lancement local

```bash
cp .env.example .env   # remplir API_KEY avec une valeur de ton choix
make up                # démarre la stack (API + dashboard)
make test               # lance les tests avec couverture
```

- API : http://localhost:8000/docs
- Dashboard : http://localhost:8501

Pour arrêter : `make down`

## Variables d'environnement

| Variable | Description |
|---|---|
| `API_KEY` | Clé requise dans le header `X-API-Key` pour créer/supprimer un serveur |
| `API_BASE_URL` | URL utilisée par le dashboard pour joindre l'API (`http://api:8000` dans Docker) |

## Développement sans Docker

```bash
pip install -r requirements.txt
make dev   # lance l'API et le dashboard en local
```

## Tests

```bash
make test    # pytest + couverture (seuil 75%)
make lint    # flake8
```

## Déploiement Azure

Le pipeline `.github/workflows/ci-cd.yml` est prêt (test → build → deploy vers Azure Container Apps)
mais nécessite la configuration des GitHub Secrets suivants pour fonctionner :
`AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `ACR_NAME`, `API_KEY`.

> URLs live à ajouter ici une fois déployé :
> - API : `https://<api>.<env>.azurecontainerapps.io/docs`
> - Dashboard : `https://<dashboard>.<env>.azurecontainerapps.io`

## Structure du dépôt

```
devops-monitor/
├── api/               # Backend FastAPI
├── dashboard/          # Frontend Streamlit
├── tests/              # Tests pytest
├── .github/workflows/  # Pipeline CI/CD
├── docker-compose.yml
├── Makefile
├── requirements.txt
└── .env.example
```
