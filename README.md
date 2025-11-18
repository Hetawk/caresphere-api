# CareSphere API — short guide

CareSphere API is a FastAPI backend for member & messaging workflows. This README shows the quick start and CI commands; details live in the `Docs/` folder in other repositories.

## Quick start (local)

- Copy environment and adjust settings:

```bash
cp .env.example .env
# edit .env (DB_URL, JWT_SECRET, etc.)
```

- Create a Python 3.11 virtualenv and install deps:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

- Run migrations (safe):

```bash
python3 scripts/run_migrations.py   # stamps or upgrades safely
```

- Start local server:

```bash
uvicorn app.main:app --reload
```

Open API docs: http://localhost:8000/docs

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication:

1. **Register/Login** to receive access token
2. **Include token** in requests:
   ```
   Authorization: Bearer <your-token>
   ```

## ⚙️ Sender Settings

The API supports flexible sender configurations at multiple scopes:

### Scope Hierarchy

1. **User-level**: Personal sender overrides for individual users
2. **Organization-level**: Shared sender settings for organization members
3. **Global-level**: System-wide defaults (admin only)
4. **Environment-level**: Fallback from environment variables

Settings cascade from specific to general: user → organization → global → environment.

### API Endpoints

- `GET /settings/senders/resolved` - Get effective sender settings for current user
- `GET /settings/senders` - List sender settings (with scope filters)
- `PUT /settings/senders` - Create/update sender settings
- `DELETE /settings/senders` - Delete specific sender settings

### Permission Model

- **Super Admin**: Can manage global settings
- **Admin**: Can manage organization settings
- **User**: Can manage personal settings only

### Example Usage

```bash
# Get resolved settings (cascaded)
curl -H "Authorization: Bearer <token>" \
  https://caresphere.ekddigital.com/settings/senders/resolved

# Set personal sender override
curl -X PUT -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"John Doe","email":"john@company.com","phone":"+1234567890"}' \
  https://caresphere.ekddigital.com/settings/senders?scope=USER
```

## 🚢 Deployment

### Production URL

```
https://caresphere.ekddigital.com
```

### Deployment Platforms

- Railway
- Heroku
- DigitalOcean
- AWS Elastic Beanstalk

## 📝 Environment Variables

All configuration is centralized in `app/config.py` and can be overridden through the following environment variables (see `.env.example`):

| Variable                                                  | Description                                                          |
| --------------------------------------------------------- | -------------------------------------------------------------------- |
| `DB_URL`                                                  | SQLAlchemy database URL (e.g., `mysql+pymysql://user:pass@host/db`). |
| `JWT_SECRET`                                              | Secret key for signing JWT access/refresh tokens.                    |
| `JWT_ALG`                                                 | JWT signing algorithm (default `HS256`).                             |
| `JWT_EXP` / `JWT_REFRESH_EXP`                             | Access and refresh token lifetimes in seconds.                       |
| `HASH_ROUNDS`                                             | Bcrypt cost factor for password hashing.                             |
| `API_HOST` / `API_PORT` / `API_RELOAD`                    | Uvicorn host, port, and auto-reload flag.                            |
| `CORS_ORIGINS`                                            | Comma-separated list of allowed origins.                             |
| `PAGE_DEF`, `PAGE_SIZE_DEF`, `PAGE_SIZE_MAX`              | Pagination defaults used across list endpoints.                      |
| `LOG_LIMIT_DEF`, `LOG_LIMIT_MAX`                          | Automation log list defaults/limits.                                 |
| `MSG_NAME`, `MSG_EMAIL`, `MSG_PHONE`                      | Default sender identity for outbound messaging.                      |
| `FEATURE_ANALYTICS`, `FEATURE_AUTOMATION`, `FEATURE_DEMO` | Feature toggles to enable/disable modules.                           |
| `LOG_LEVEL`                                               | Python logging level (e.g., `info`, `debug`).                        |

Any field not provided in `.env` falls back to the defaults declared in `app/config.py`.

## Tests

Run unit tests with pytest (local SQLite memory engine is used):

```bash
source .venv/bin/activate
pytest
```

### What we added

- Unit tests for the FastAPI health endpoints (`tests/test_app.py`) using FastAPI's TestClient.
- A database smoke test (`tests/test_database.py`) to verify that SQLAlchemy settings create an engine and tables can be created using an in-memory SQLite database.

### Next testing goals (recommended)

1. Add unit tests for critical services (auth, members, messages).
2. Add integration tests that run against a test MySQL instance (Docker) to validate migrations and driver-specific behavior (ssl, enum conversions).
3. Add CI pipeline step to run tests and run Alembic autogenerate check (no unexpected schema changes).
4. Add test coverage reporting (pytest-cov) and caching of DB containers for faster CI runs.

Run the tests locally:

```bash
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

CI: we added a GitHub Actions workflow (`.github/workflows/python-app.yml`) that runs tests and migrations. See workflow for details.

## Migrations

Use Alembic (via `app/config` which reads `DB_URL`) or the provided helper to safely stamp or upgrade:

```bash
source .venv/bin/activate
python3 scripts/run_migrations.py
```

The script will `stamp head` if it finds app tables but no alembic history; otherwise it will run `alembic upgrade head`.

## 📄 License

Private - All rights reserved

## 👥 Team

- **Developer:** EKD Digital
- **Repository:** https://github.com/Hetawk/caresphere-api
