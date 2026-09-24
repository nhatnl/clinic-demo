# ClinicCare frontend

An English-only Nuxt 3 application for the ClinicCare assignment: consultation history and details, patient details, new consultation, consultation and diagnosis search, sign-in, and administrator account creation. Responsive layouts include loading, empty, validation, permission, and backend error states.

The app uses **Nuxt 3**, matching the assignment. Application files use the standard Nuxt 3 root layout.

## Run

Use Node.js 22.19+, 24.11+, or 26+ as supported by the installed Nuxt release.

```sh
cd frontend
npm ci
cp .env.example .env
npm run dev
```

Open http://localhost:3000. Set `NUXT_API_BASE` to the FastAPI origin (default `http://127.0.0.1:8000`). This address is server-only. Run FastAPI separately and sign in with an existing database account; the frontend does not seed users or offer self-registration.

```sh
npm run typecheck
npm test
```

`npm test` builds production and runs a dependency-free Node integration check against a temporary, test-only upstream. It covers authentication, cookies, protected pages, request forwarding, query parameters, validation errors, malformed responses, expiration, and logout. Run the backend tests separately to check FastAPI and database logic.

Production requires the Nuxt server; static generation cannot provide the API bridge:

```sh
npm run build
NUXT_API_BASE=http://127.0.0.1:8000 node .output/server/index.mjs
```

Use HTTPS when deploying. Nuxt stores the backend JWT in an HttpOnly, SameSite=Strict cookie, with Secure enabled for HTTPS requests. The browser receives no bearer token. The server forwards it to FastAPI, allows only the listed routes, disables mutation retries, rejects cross-origin mutations, and returns only a success flag after account creation. JWT claims control UI visibility only: FastAPI must verify signatures and enforce authorization on every data endpoint.

## Backend status and API contract

The frontend uses real API requests only. It never silently substitutes sample records or stores patient notes in local storage.

| Nuxt endpoint | FastAPI endpoint | Current backend status |
| --- | --- | --- |
| `POST /api/sign-in` | `POST /auth/sign-in` | Implemented; requires an existing user |
| `POST /api/admin/create-user` | `POST /admin/create-user` | Implemented; returns 201 |
| `GET /api/diagnosis?search=...` | `GET /diagnosis/?search=...` | Implemented |
| `GET /api/consultation?patient=...&diagnosis_code=...` | Same path without `/api` | Implemented |
| `GET /api/consultation?patient_id=...` | `GET /consultation?patient_id=...` | Implemented |
| `GET /api/consultation/:id` | `GET /consultation/:id` | Implemented |
| `GET /api/patients/:id` | `GET /patients/:id` | Implemented |
| `GET /api/patients` | `GET /patients/` | Implemented; used by the patient selector |
| `POST /api/patients` | `POST /patients/` | Implemented; returns 201 |
| `POST /api/consultation` | `POST /consultation` | Implemented; returns 201 |

`GET /api/session` and `POST /api/sign-out` are local Nuxt session endpoints. Administrators see the account-creation page; other roles are redirected away from it. The backend remains responsible for actual permissions.

The frontend never retries POST requests automatically.

### Diagnosis lookup

Return an array, including an empty array for no matches:

```json
[
  {
    "code": "A00.0",
    "name": "Cholera due to Vibrio cholerae 01, biovar cholerae",
    "description": null,
    "is_valid_for_submission": true
  }
]
```

Category codes (`is_valid_for_submission: false`) appear in search but cannot be selected for a consultation. Codes are passed through exactly as returned by the directory.

### Create a consultation

The form sends the backend's existing contract:

```json
{
  "patient_id": 7,
  "diagnosis_codes": ["A00.0"],
  "note": "Assessment, treatment plan, and follow-up."
}
```

The form requires a selected patient, at least one selectable diagnosis, and nonblank notes. Typing a first or last name shows patient suggestions directly below the input. The backend validates the referenced records. Authorized clinical roles can create a patient from the sidebar or from the patient selector while recording a consultation; the new patient is selected automatically. Users can open a patient record from consultation history to see all visits and start a new consultation for that patient.

The backend returns the created consultation and lists these objects newest first:

```json
[
  {
    "id": 1,
    "patient": { "id": 7, "name": "Alex Smith", "age": 32 },
    "diagnoses": [
      { "code": "A00.0", "name": "Cholera", "description": null }
    ],
    "note": "Assessment, treatment plan, and follow-up.",
    "created_at": "2026-09-24T08:00:00Z",
    "updated_at": "2026-09-24T08:00:00Z"
  }
]
```

`patient` filters by patient name, `patient_id` filters by exact patient ID, and `diagnosis_code` filters by code; filters combine when provided. The frontend keeps search filters in the URL. The returned history list is paginated locally in groups of ten; introduce backend pagination when records become too large for a single response.

Missing endpoints and malformed responses show a service error. A failed save preserves the form. Leaving a modified consultation prompts before discarding it. There is no edit/delete consultation workflow because the current assignment and backend do not define one.
