# Behavioral-Monitor-Extension
**Goal**
Ship a stack that monitors edit dynamics + editor activity, persists sessions on a remote server, and uses machine learning to estimate the extent of behavioral change (0–100 proxy), with peak strikes, code-at-peak context, timeline UI, and feedback hints.

**Defaults locked**
Backend: remote-capable FastAPI in Docker
Database: PostgreSQL 16
Auth: per-user Bearer API tokens (SHA-256 hash at rest)
Driver: SQLAlchemy async + asyncpg (Alembic uses sync URL variant)
Deploy: Docker Compose (api + db); 1 Uvicorn worker in v1 so model file loads stay simple
ML: EWMA baseline always; Isolation Forest when enough history; RandomForest only after labels
Transport: extension host calls the API; webview never fetches the remote server

**Final pre-coding review (fixes applied)**
No raw keystrokes — edit classification only; no type command wrapping; bulkInsert ≠ typing speed.

Webview networking — Webviews are browser-like (CORS). All HTTP goes through the extension host; UI gets data via postMessage.

Peak snippet handoff — Each event batch includes optional editor_context (uri, line range, snippet). When a peak is recorded, attach the latest context from that batch (no second round-trip required).

ML must not block/retrain on every request — Per-batch scoring is Model A (+ Model B inference from disk). Retrain Isolation Forest / RF only via POST /models/retrain (or startup job), never inline on POST /events.

Single worker — v1 Compose runs one Uvicorn worker to avoid multi-process stale in-memory models; models are loaded from artifacts/ by version from model_registry.

Timestamps — Store client ts for behavior ordering and server received_at for audit/clock skew.

GET /health — Unauthenticated liveness; all other routes require Bearer token.

Abuse guards — Max events per batch (e.g. 500), max snippet chars (e.g. 4k), basic rate limit per token.

Proxy honesty — Extent is behavioral change vs baseline, not physiological stress; README states this.

Secrets — Token in extension SecretStorage; DATABASE_URL / bootstrap token only in server env; never commit .env.


**Languages and stack**
TypeScript + HTML/CSS — VS Code/Cursor extension and webview UI
Python 3.11+ — FastAPI, feature pipeline, scikit-learn
PostgreSQL — durable sessions, events, scores, peaks, labels, model registry
Docker Compose — local and remote deploy of api + db


**Monorepo layout**
behavioral-monitor/
  extension/              # VS Code/Cursor extension
  backend/                # FastAPI + ML + Alembic
  docker-compose.yml
  .env.example
  README.md

Path: ~/Projects/behavioral-monitor (create, git init, then move agent to root before coding).


**Architecture**

flowchart LR
  subgraph client [User machine]
    Collectors[Collectors]
    HostApi[ExtensionHostApiClient]
    Ui[WebviewPanel]
  end
  subgraph remote [Remote server]
    Api[FastAPI]
    Db[(PostgreSQL)]
    Score[ScoreService]
    Artifacts[ModelArtifacts]
  end
  Collectors --> HostApi
  HostApi -->|"HTTPS Bearer"| Api
  Api --> Db
  Api --> Score
  Score --> Artifacts
  Score --> Db
  HostApi -->|"postMessage snapshot"| Ui


**Backend**

Auth and API

users, api_tokens (hash, label, revoked_at)

Bootstrap script prints one admin token once

Routes: POST /sessions, POST /sessions/{id}/stop, POST /sessions/{id}/events, GET /sessions/{id}/snapshot, POST /sessions/{id}/labels, POST /models/retrain

GET /health public

All data scoped to token’s user


Postgres schema (core)

sessions, behavior_events (client_ts, received_at, type, payload_json)

feature_windows, scores, peaks (optional snippet from editor_context)

labels, model_registry

Indexes on (session_id, client_ts); user-scoped cascades


Event batch payload

events[]: classified behavior events with client timestamps

editor_context?: { file_uri, line_start, line_end, snippet } for peak attachment / reveal


ML (extent 0–100)

Features (20s windows): typed_rate, iki_mean/std, deletion_ratio, pause_ratio, undo_rate, file_switch_rate, cursor_jump_rate, selection_thrash_rate, bulk_insert_rate, …

Model A (always): EWMA per-feature baseline → distance → logistic-scaled extent; states calm / elevated / peak-candidate

Model B: Isolation Forest trained offline on stored windows (min ~200 windows); inference only on request path

Model C (optional): RandomForest after enough user labels; explicit retrain only

Peaks: threshold + local max + refractory (45–60s); store snippet from batch editor_context

Hints: top contributing features → rule-based messages


Extension





Edit + editor collectors (classification rules as above)



Commands: Start/Stop session, Show Timeline, Set API Token, Clear Session, Trigger Retrain (calls API)



Settings: apiBaseUrl (dev http://127.0.0.1:8765 or remote HTTPS)



Status bar live extent; offline badge if health/snapshot fails



WebviewPanel: timeline chart, peak list with “Code at peak” + reveal in editor (host executes reveal)

Deploy





Compose: Postgres 16 + API (port 8765), volumes for DB + artifacts/



Dev: Compose on laptop



Remote: same Compose on VPS + TLS reverse proxy (Caddy/Nginx)



Env: DATABASE_URL, ARTIFACTS_DIR, BOOTSTRAP_ADMIN_TOKEN (optional)

Privacy





Remote = metrics + peak snippets leave the machine; document clearly



Exclude globs for secrets; cap snippet size



User data delete endpoint or documented SQL wipe



No medical claims

Deliverables





Runnable monorepo (Compose + F5 extension)



Authenticated Postgres-backed API



ML extent scoring with peaks and hints



Timeline webview



README: run locally, deploy remotely, tokens, privacy, model meaning

Out of scope





OAuth/SSO, team admin UI



Webcam / facial / pupil



Bitmap screenshots, OS keyloggers



Deep learning, multi-worker model serving

Implementation order





Scaffold monorepo + Compose + agent move to root



Alembic + auth + session/event/snapshot



Extension collectors + host API client + editor_context batches



Model A scoring + peaks; then Model B artifact load/retrain



Webview + hints + optional labels/Model C



TLS/deploy docs + privacy wipe + README


