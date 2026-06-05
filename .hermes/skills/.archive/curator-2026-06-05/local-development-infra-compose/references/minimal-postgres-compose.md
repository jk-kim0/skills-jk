# Minimal PostgreSQL compose example

This example captures the minimal local PostgreSQL-only setup used for a repository that wanted start/stop support but no app services, migrations, seed jobs, Redis, or queues yet.

## compose.yml shape

```yaml
services:
  postgres:
    image: postgres:18
    container_name: outbound-agent-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: outbound_agent
      POSTGRES_USER: outbound_agent
      POSTGRES_PASSWORD: outbound_agent_dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U outbound_agent -d outbound_agent"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s

volumes:
  postgres-data:
```

## Documentation points that mattered

- State that the setup is local-only and not production deployment configuration.
- Explain that PostgreSQL Docker images do not have a dedicated `lts` tag; use the current stable supported major tag instead of `latest`.
- Include a connection URL using the local-only credentials.
- Document normal stop (`docker compose down`) separately from destructive reset (`docker compose down -v`).
- Explicitly list what is not included yet to avoid scope creep.

## Verification

Run:

```bash
docker compose config
git diff --check
```
