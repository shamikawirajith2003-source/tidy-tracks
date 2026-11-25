# TidyTrack: smart garbage collection and recycling routes

A full-stack prototype.

- **frontend/**: React + Vite. Resident, driver and admin dashboards, Home / About / Contact, Sinhala / English / Tamil.
- **backend/**: Python (FastAPI) REST API with MongoDB (PyMongo) or embedded SQLite (runs out-of-the-box with zero database setup).
- **docker-compose.yml**: MongoDB and the API in containers (optional).

## Run it

You need Python 3.11+ and Node 18+. No MongoDB installation required (embedded SQLite is used automatically when MongoDB is not running).

**1. API Backend**
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
The API is then at http://localhost:8000 (interactive docs at http://localhost:8000/docs).

*(Optional: If you have Docker or MongoDB installed, you can run `docker compose up --build` or point `MONGO_URI` to your MongoDB instance).*

**2. Frontend**
```bash
cd frontend
npm install
npm run dev        # http://localhost:5173
```

On first start the API creates the stops, collection zones, an admin account and demo accounts in MongoDB.

| Role     | Email                  | Password | Log in at          |
|----------|------------------------|----------|--------------------|
| Admin    | admin@tidytrack.lk     | admin123 | "Admin login" page |
| Resident | a.perera@example.lk    | demo123  | "Log in" page      |
| Driver   | k.silva@example.lk     | demo123  | "Log in" page      |

Set `SEED_DEMO=false` to skip the demo accounts, and change `ADMIN_EMAIL` / `ADMIN_PASSWORD` / `JWT_SECRET`.

To see it working end to end, log in as the driver in one browser window (the demo truck starts driving),
and as a resident in another (the truck moves on their map and the ETA counts down).

## How it works

- **Accounts and roles:** passwords are hashed with bcrypt; login returns a JWT. Every protected endpoint checks the
  role on the server (`require_roles` in `backend/app/security.py`), so a resident cannot call driver or admin endpoints
  even by editing the frontend. Admin accounts cannot be self-registered.
- **Fleet:** stops, truck position and the traffic flag live in MongoDB. The driver's browser reports the truck position
  every second (in a real system: the phone's GPS); residents and admins poll `GET /api/fleet` every 2 seconds.
- **Route optimisation:** `backend/app/routing.py` orders the pending stops nearest-first, puts stops with a requested
  recycling pickup first, and penalises a stop under a traffic delay. ETAs and remaining kilometres are computed on the
  server. The "before optimizing" figure compares against visiting the streets in alphabetical order (a stand-in for an
  unplanned route sheet). It is a simple heuristic: use OR-Tools, OSRM or a maps API for production.
- **Photos:** complaint photos are uploaded to `backend/uploads/` (a Docker volume). The server checks that the file really
  is a JPG, PNG, GIF or WebP under 5 MB and gives it a random name.

## API summary

| Method and path | Who | What |
|---|---|---|
| `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me` | public / signed in | accounts (login has `admin: true` for the admin page) |
| `GET /api/fleet` | public | stops, truck, optimised order, ETAs, route metrics |
| `POST /api/fleet/truck` | driver | report truck position |
| `POST /api/fleet/stops/{id}/collect` | driver, admin | mark a stop collected |
| `POST /api/fleet/stops/{id}/issue` | driver | log blocked access / overloaded bin (also files a complaint) |
| `POST /api/fleet/traffic` | driver, admin | set or clear the traffic delay |
| `POST /api/fleet/reset` | admin | start a new day |
| `POST /api/pickups`, `GET /api/me/pickups` | resident | recycling pickup requests |
| `POST /api/reports` (multipart), `GET /api/me/reports` | resident | geotagged problem reports with a photo |
| `POST /api/messages` | public | contact form |
| `GET /api/admin/overview`, `/users`, `/pickups`, `/reports`, `/messages`, `/zones` | admin | the database view |
| `PATCH /api/admin/users/{id}`, `PATCH /api/admin/reports/{id}/resolve`, `PUT /api/admin/zones/{id}` | admin | manage accounts, complaints, schedule |

MongoDB collections: `users`, `stops`, `fleet`, `pickups`, `reports`, `messages`, `zones`.

## Tests

```bash
cd backend
python -m unittest discover -s tests     # route optimisation tests, no database needed
```

## Before a real deployment

- Put the API and the site behind HTTPS (for example nginx or Caddy) and set `CORS_ORIGINS` to your site's address.
- Replace the default `JWT_SECRET` and admin password. Do not publish MongoDB's port.
- The login and contact rate limits are kept in memory, so they only work with a single API process; use Redis or the proxy for several.
- Replace the drawn map with a real map and real GPS, and the nearest-stop heuristic with a routing service.
- Add backups for MongoDB and the `uploads` folder, and a password reset flow.
- Have a Sinhala and Tamil speaker review `frontend/src/translations.json`.
