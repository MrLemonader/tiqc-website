# TIQC Internal Member Profile System

Flask API + MySQL backend with a Vue 3, Vite, and Naive UI single-page frontend for TIQC internal member profiles.

## Local Development

1. Create and activate a Python virtual environment.
2. Install backend dependencies:

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

5. Initialize tables and seed demo data:

```bash
flask --app app.py init-db
flask --app app.py seed-db
```

6. Run the Flask API:

```bash
flask --app app.py run
```

7. In another terminal, start the frontend dev server:

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL, usually `http://127.0.0.1:5173`. Vite proxies `/api`, `/uploads`, `/static`, `/dev-login`, and `/dev-logout` to Flask on port `5000`.

## Production Build

Build the Vue frontend before using Flask as the production page entry:

```bash
cd frontend
npm install
npm run build
```

The build output is written to `frontend/dist`. After that, Flask serves the SPA entry for `/`, `/login`, `/members`, `/members/<slug>`, and `/profile`, while API, upload, static image, and development login routes keep their existing behavior.

Run Flask directly for a local production-entry check:

```bash
flask --app app.py run
```

For Linux deployment, run the app with gunicorn behind Nginx:

```bash
gunicorn -w 2 -b 127.0.0.1:5000 app:app
```

The included Nginx example proxies normal traffic to Flask and serves uploaded files from `/uploads/` directly. It also keeps `client_max_body_size 20m`, matching Flask's avatar upload limit.

An alternative deployment is to let Nginx serve `frontend/dist` directly and proxy only `/api`, `/uploads`, `/static`, `/dev-login`, and `/dev-logout`; this repository's default first-stage setup keeps Flask as the SPA entry.

## Login and Visitor Mode

Visitors can browse the homepage, member list, and member detail pages without logging in. Editing `/profile` requires a member login.

Use `/login` and enter a seeded campus ID, such as:

- `20240001`
- `20240002`

The login form calls `/api/login`, sets a secure HTTP-only `campus_id` cookie, and redirects to `/profile`. Use the header logout button or `/api/logout` to clear the login cookie.

Development shortcuts are still available after seeding demo data:

- `/dev-login/20240001`
- `/dev-login/20240002`

`/dev-login/<campus_id>` redirects to `/profile`. `/dev-logout` clears the same cookie.

## Admin Data Maintenance

The MVP uses Flask CLI commands for basic admin data maintenance instead of a browser admin dashboard.

Create a user:

```bash
flask --app app.py create-user --campus-id 20240003 --name "Carol Wang" --email carol@example.edu --role member
```

Create a member profile and bind it to that user:

```bash
flask --app app.py create-member --user-campus-id 20240003 --slug carol-wang --role phd --title "PhD Student" --display-order 30 --active true
```

Update admin-maintained member fields:

```bash
flask --app app.py update-member --slug carol-wang --title "Senior PhD Student" --display-order 25
flask --app app.py update-member --slug carol-wang --new-slug carol-q-wang --active false
```

Inspect existing data:

```bash
flask --app app.py list-users
flask --app app.py list-members
```

Supported user roles are `member` and `admin`. Supported member roles are `pi`, `postdoc`, `phd`, `master`, `undergrad`, and `alumni`. Publication links are still maintained by each member from `/profile`.

## Core API Routes

- `/api/login`
- `/api/logout`
- `/api/me`
- `/api/members`
- `/api/members/<slug>`
- `/api/profile`
- `/api/profile/avatar`

## Acceptance Checks

- Development frontend: open `http://127.0.0.1:5173`.
- Production entry: build `frontend/dist`, then open `http://127.0.0.1:5000`.
- Refresh `/login`, `/members`, `/members/alice-chen`, and `/profile`; each should load the Vue app.
- `/api/members` should still return JSON.
- Without login, `/api/profile` should return `login_required`.
- After login, `/profile` should show only the current member's editable profile.
