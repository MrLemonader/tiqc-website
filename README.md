# TIQC Internal Member Profile System

Flask API + MySQL backend skeleton for the TIQC internal member profile system. The frontend is planned as a Vue 3 + Vite + Naive UI SPA.

## Local setup

1. Create and activate a Python virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy environment settings:

```bash
cp .env.example .env
```

4. Start MySQL, or use Docker Compose:

```bash
docker compose up -d mysql
```

1. Initialize tables and seed demo data:

```bash
flask --app app.py init-db
flask --app app.py seed-db
```

6. Run the app:

```bash
flask --app app.py run
```

Open `http://127.0.0.1:5000` for the backend API. Page routes return a small JSON placeholder while the Vue dev server handles the frontend.

## Frontend setup

The frontend lives in `frontend/` and uses Vue 3, Vite, Naive UI, and npm.

Install or repair Node.js first. Both commands should work before installing frontend dependencies:

```bash
node --version
npm --version
```

Then run:

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL, usually `http://127.0.0.1:5173`. Vite proxies `/api`, `/uploads`, `/static`, `/dev-login`, and `/dev-logout` to Flask on port `5000`.

## Development login

The app simulates campus login by reading a `campus_id` cookie. Use `/dev-login/20240001` or `/dev-login/20240002` after seeding demo data. Login redirects to `/profile`, which will be handled by Vue Router once the SPA is added.

## Core API routes

- `/api/me`
- `/api/members`
- `/api/members/<slug>`
- `/api/profile`
- `/api/profile/avatar`

## Frontend status

Jinja templates have been removed. The Flask app no longer renders HTML pages directly; it exposes JSON APIs and upload file access for the Vue SPA.
