# Behavioral Monitor

Monorepo for a stack that monitors edit dynamics and editor activity, persists sessions on a remote server, and uses machine learning to estimate behavioral change (0–100 proxy), with peak strikes, code-at-peak context, timeline UI, and feedback hints.

## Structure

```
extension/          # Browser / editor extension (to be built)
backend/            # API and persistence service (to be built)
docker-compose.yml  # Local multi-service orchestration
.env.example        # Sample environment variables
```

## Getting started

1. Copy `.env.example` to `.env` and adjust values as needed.
2. Extension and backend packages will be added in later steps.
3. Use Docker Compose once the backend image is defined:

```bash
docker compose up
```

## Status

Monorepo scaffold only. Dependencies, backend, extension, and ML models are not included yet.
