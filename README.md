# ClinicCare Mini EMR

ClinicCare is a small EMR application for searching ICD-10-CM diagnoses and
recording patient consultation notes. It uses FastAPI, SQLModel, PostgreSQL,
Alembic, Nuxt 3, and a Nuxt server proxy that keeps the JWT in an HttpOnly
cookie.

## Features

- Search diagnoses by code or name.
- Create patients and consultation notes with one or more diagnoses, recording
  the authenticated creator automatically.
- List and search consultations by patient or diagnosis code.
- JWT authentication, role-based patient/admin operations, validation, and
  consistent API errors.
- PostgreSQL migrations and automatic import of 100 ICD-10-CM records on
  startup.

## Run with Docker

Requirements: Docker Desktop with Docker Compose.

```sh
cp .env.example .env
docker compose up --build
```

Before sharing or deploying the app, replace `JWT_SECRET` in `.env` with a
private random value of at least 32 characters.

Compose waits for PostgreSQL, applies all Alembic migrations, imports 100
diagnoses idempotently, and then starts both applications:

- Web app: http://localhost:3000
- FastAPI docs: http://localhost:8000/docs

The admin email is `admin@kyanon.digital`. Set `ADMIN_PASSWORD` in `.env` before
the first start, or read the generated password with `docker compose logs backend`.
A generated password is printed once when the admin is created or rotated by migration.

Stop the stack with `docker compose down`. Add `-v` only when you intentionally
want to delete the local PostgreSQL data.

## Main API

Except for sign-in, these routes require `Authorization: Bearer <token>`. The
Nuxt app handles this automatically through its HttpOnly session cookie.

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/auth/sign-in` | Sign in and receive a JWT |
| `GET` | `/diagnosis/?search=<term>` | Search diagnosis codes |
| `POST` | `/consultation` | Create a consultation |
| `GET` | `/consultation?patient=&diagnosis_code=` | List or search consultations |
| `GET` | `/consultation/{id}` | Read one consultation |
| `GET/POST` | `/patients/` | Search or create patients |
| `POST` | `/admin/create-user` | Create an account as an administrator |

List routes accept `page` (default 1) and `page_size` (default 10, maximum 100).
They return `{ "items": [...], "total": 0, "page": 1, "page_size": 10 }`.

## Diagnosis data

The included parser reads the official April 1, 2026 ICD-10-CM order and
tabular files. Startup imports 100 records; the upsert makes repeated starts
safe. To import the complete included dataset later, run:

```sh
docker compose exec backend python -m scripts.import_icd10cm_data
```

## Checks

```sh
cd backend
uv sync
uv run python -m unittest discover -s tests -p "test_*.py" -v

cd ../frontend
npm ci
npm run typecheck
npm test
```

Environment templates are available in `.env.example`, `backend/.env.example`,
and `frontend/.env.example`. The root template is sufficient for Docker.
