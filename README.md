# clinic-demo

Run the app with Docker Compose:

```sh
cp .env.example .env
# Set the DB_* values and JWT_SECRET in .env.
docker compose up --build
```

Open http://localhost:3000. The backend API is at http://localhost:8000.
On first startup, Compose creates the database and applies migrations. To load
the diagnosis directory, run `docker compose exec backend python scripts/import_icd10cm_data.py`.
