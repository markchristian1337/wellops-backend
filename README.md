# WellOps Console — Backend

A FastAPI backend for an internal "Well Operations Console" modeled on oil & gas field operations. Supervisors view wells and ranked equipment alerts, acknowledge or close them, and see live sensor temperature readings. Built as a personal project to demonstrate production-grade engineering across the full stack: API design, validation, deployment to Azure Kubernetes Service, secret management via Key Vault, and time-series sensor data in PostgreSQL.

## Live Demo

[▶ WellOps — Live Azure Deployment Demo](https://www.loom.com/share/11a94f1bc0aa4cc39a60dee1ba846b50)

Demonstrates: AKS deployment, RabbitMQ pipeline (simulator → worker → Postgres), rolling average pre-computation, Grafana live dashboard, public API endpoint.

> **Note:** The AKS cluster, Azure Postgres, and ACR have been scaled down to avoid charges during my job search. The deployment is fully reproducible from the manifests in [wellops-infra](https://github.com/markchristian1337/wellops-infra). Happy to redeploy on request — typically takes 15 minutes.

## Stack

- Python 3.11
- FastAPI + uvicorn
- SQLAlchemy ORM
- Pydantic v2 schemas
- PostgreSQL (Azure Database for PostgreSQL Flexible Server in production, SQLite for local dev)
- Docker

## Architecture

```
Browser
   |
   v
AKS LoadBalancer Service
   |
   v
FastAPI pod (uvicorn)  <----- secrets injected at startup
   |                          via CSI driver from Azure Key Vault
   v
Azure PostgreSQL Flexible Server (SSL required)

Azure Container Registry stores the FastAPI image.
Grafana dashboard reads directly from the Postgres instance.
```

## Project layout

```
backend/
  app/
    main.py                  FastAPI app, CORS, route registration
    api/routes/              health, wells, alerts, sensors
    core/
      config.py              Pydantic Settings
      db.py                  SQLAlchemy engine, SSL auto-detection for Azure
      deps.py                get_db dependency
    models/                  SQLAlchemy models (Well, Alert, Temperature)
    schemas/                 Pydantic request/response schemas with enums
    services/                Business logic (kept thin while routes are simple)
    scripts/
      simulate_sensors.py    HTTP-based sensor reading simulator
  requirements.txt
```

Routes are intentionally thin. Business logic moves into `services/` once a route needs more than request/response shaping.

## API surface

All routes prefixed `/api`:

- `GET /api/health`
- `GET /api/wells`, `POST /api/wells`
- `GET /api/alerts`, `POST /api/alerts`, `PATCH /api/alerts/{id}`
- `GET /api/sensors/temperatures`, `POST /api/sensors/temperatures`

Auto-generated Swagger docs at `/docs` when the server is running.

## Local development

```bash
git clone https://github.com/markchristian1337/wellops-backend.git
cd wellops-backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# defaults to SQLite locally
uvicorn app.main:app --reload
```

Open `http://localhost:8000/docs` to explore the API.

To point at a Postgres instance instead, set:

```
DB_HOST=...
DB_PORT=5432
DB_NAME=wellops
DB_USER=...
DB_PASSWORD=...
```

The `db.py` module auto-enables `sslmode=require` when `DB_HOST` contains `postgres.database.azure.com`.

## Design decisions worth calling out

**Alert lifecycle as a state machine at the API boundary.** Alerts move `open -> ack -> closed`, only in that order, closed is terminal. The PATCH endpoint enforces this with explicit transition checks. Invalid transitions return 422 with an error message that quotes the current state. The database isn't responsible for the lifecycle — the API is. Database constraints handle invariants; the application owns the state machine.

**Server-owned fields.** `status`, `created_at`, `ack_at`, and `close_at` are never trusted from the client. The client provides who acknowledged or closed (`ack_by`, `close_by`); the server provides when. The `AlertUpdate` schema simply doesn't accept the timestamp fields.

**Pydantic enums for status and severity.** `AlertStatus` and `AlertSeverity` inherit from `str, Enum` so they serialize as JSON strings and reject invalid values at the API boundary, before anything reaches the database.

**Indexes on the common query paths.** `well_id` and `status` on the `alerts` table — the most frequent queries are "alerts for a well" and "all open alerts." The `wells.api_number` natural key is unique-indexed.

**SSL auto-detection.** `db.py` checks the host string and applies `sslmode=require` when connecting to Azure Postgres, without needing a separate config flag.

**Secrets via Azure Key Vault, not env files in the repo.** A K8s SecretProviderClass references the Key Vault, the CSI driver mounts the secret at pod startup using the kubelet's managed identity, and a cached K8s Secret picks it up. Rotating a secret in Key Vault is a delete-and-restart on the cached Secret.

## What's not built yet

Listed honestly so the scope is clear:

- MQTT-based real-time ingestion (currently uses an HTTP simulator)
- Azure Event Hubs as the message queue between MQTT subscriber and worker pod
- Azure Cache for Redis for the latest-reading-per-sensor lookup
- WebSocket or SSE push for the frontend (currently polls)
- Authentication (planned: Keycloak OIDC, same pattern I used at Daikin across 8+ apps)
- GitHub Actions CI/CD (deployment is currently manual)
- AI integration: anomaly detection on temperature readings, predictive alerting, text-to-SQL via Azure OpenAI

Architecture for each is sketched but the code isn't written yet. I'd rather ship a small thing that's defensible at every layer than a big thing I can't explain.

## Related repos

- [wellops-frontend](https://github.com/markchristian1337/wellops-frontend) — React + TypeScript SPA
- [wellops-infra](https://github.com/markchristian1337/wellops-infra) — Kubernetes manifests and Azure resource notes

## License

MIT
