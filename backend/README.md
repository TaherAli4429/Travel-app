# Wanderly Travel App – Backend & Integration Guide

Welcome to the **Wanderly** backend service. This production-ready backend is built with **Python 3**, **FastAPI**, **PostgreSQL**, **SQLAlchemy 2.0**, **Alembic**, and **JWT Authentication**, fully integrated with the Flutter travel application frontend.

---

## 1. System Architecture

```
backend/
├── app/
│   ├── core/
│   │   ├── config.py           # Pydantic v2 BaseSettings & environment loader
│   │   ├── database.py         # SQLAlchemy engine, SessionLocal, declarative Base
│   │   └── security.py         # Passlib/bcrypt password hashing & PyJWT tokens
│   ├── dependencies/
│   │   └── auth.py             # Bearer token validation & current user injection
│   ├── models/                 # SQLAlchemy 2.0 ORM tables
│   │   ├── destination.py      # Destinations table
│   │   ├── favorite.py         # Favorites table (User + Destination FKs)
│   │   ├── notification.py     # Notifications table
│   │   ├── review.py           # Reviews table (with ratings recalculation)
│   │   └── user.py             # Users table (UUID PK, hashed password, roles)
│   ├── routers/                # FastAPI APIRouters under /api/v1
│   │   ├── auth.py             # Register, Login, Refresh, Logout, Password Reset
│   │   ├── destinations.py     # Listing, Search, Categories, Details, Featured
│   │   ├── favorites.py        # Toggle, Add, Remove, List user favorites
│   │   ├── notifications.py    # List, Unread count, Mark read, Delete
│   │   ├── reviews.py          # Create, List by destination, User reviews
│   │   └── users.py            # Get Profile, Update Profile, Change Password
│   ├── schemas/                # Pydantic validation & serialization models
│   ├── services/               # Modular business logic services
│   ├── seed/
│   │   └── seed_data.py        # Seed script for 9 initial travel destinations
│   ├── utils/
│   │   └── pagination.py       # Reusable pagination helper
│   └── main.py                 # FastAPI application, CORS, and health checks
├── alembic/                    # Database migration environment
│   └── versions/
│       └── 0001_initial_schema.py # Complete 5-table schema migration
├── tests/
│   ├── conftest.py             # Isolated SQLite in-memory test database fixture
│   └── test_all_requirements.py # 17 comprehensive automated tests
├── .env                        # Local environment configuration
├── .env.example                # Example template for environment configuration
├── alembic.ini                 # Alembic configuration
└── requirements.txt            # Python dependencies
```

---

## 2. Quick Start & Setup

### Step 1: PostgreSQL Setup
Ensure PostgreSQL is running locally on port `5432`.
In PowerShell, create the `wanderly_db` database:

```powershell
# Connect with psql and create the database
psql -U postgres -c "CREATE DATABASE wanderly_db;"
```

### Step 2: Environment Configuration
Check `backend/.env` and verify your PostgreSQL credentials:

```ini
DATABASE_URL=postgresql+psycopg://postgres:YOUR_POSTGRES_PASSWORD@localhost:5432/wanderly_db
SECRET_KEY=wanderly-secret-jwt-key-super-secure-production-ready-2026-v1
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=30
ENVIRONMENT=development
```

### Step 3: Run Alembic Database Migrations
Activate the virtual environment and apply the migration to create all tables:

```powershell
cd "d:\Travel app\backend"
.\.venv\Scripts\Activate.ps1
alembic upgrade head
```

### Step 4: Seed Initial Travel Destinations
Populate the 9 initial destinations (Bali, Swiss Alps, Santorini, Kyoto, Maldives, Dubai, Banff, Queenstown, Amalfi Coast):

```powershell
python -m app.seed.seed_data
```

### Step 5: Start the FastAPI Server

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

---

## 3. Interactive API Documentation

Once the server is running, visit:
- **Swagger UI:** [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs)
- **ReDoc:** [http://127.0.0.1:8001/redoc](http://127.0.0.1:8001/redoc)
- **Health Check:** [http://127.0.0.1:8001/api/v1/health](http://127.0.0.1:8001/api/v1/health)

---

## 4. API Endpoints Overview

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/v1/auth/register` | Register a new user | No |
| `POST` | `/api/v1/auth/login` | Login and receive JWT access token | No |
| `GET` | `/api/v1/auth/me` | Fetch currently logged in user profile | Bearer Token |
| `POST` | `/api/v1/auth/refresh` | Refresh access token | Bearer Token |
| `POST` | `/api/v1/auth/logout` | Revoke session and log out | Bearer Token |
| `GET` | `/api/v1/users/me` | Get current user's profile | Bearer Token |
| `PATCH` | `/api/v1/users/me` | Update full name, email, or avatar | Bearer Token |
| `POST` | `/api/v1/users/me/change-password` | Update user password | Bearer Token |
| `GET` | `/api/v1/destinations` | List all destinations with search & category filters | Optional |
| `GET` | `/api/v1/destinations/featured` | Get the featured destination of the week | Optional |
| `GET` | `/api/v1/destinations/categories` | List all destination categories | No |
| `GET` | `/api/v1/destinations/{id}` | Get single destination details | Optional |
| `GET` | `/api/v1/favorites` | List authenticated user's saved destinations | Bearer Token |
| `POST` | `/api/v1/favorites/{id}` | Add destination to saved bucket list | Bearer Token |
| `DELETE` | `/api/v1/favorites/{id}` | Remove destination from saved bucket list | Bearer Token |
| `GET` | `/api/v1/favorites/check/{id}` | Check if destination is saved | Bearer Token |
| `GET` | `/api/v1/reviews/destination/{id}` | List reviews for a destination | No |
| `POST` | `/api/v1/reviews` | Submit a review and recalculate rating | Bearer Token |
| `GET` | `/api/v1/notifications` | List user notifications | Bearer Token |
| `GET` | `/api/v1/notifications/unread-count` | Get count of unread notifications | Bearer Token |
| `PATCH` | `/api/v1/notifications/{id}/read` | Mark single notification as read | Bearer Token |
| `PATCH` | `/api/v1/notifications/read-all` | Mark all notifications as read | Bearer Token |

---

## 5. Flutter App Network Resolution

The Flutter app automatically adapts its base URL depending on the running platform:
- **Android Emulator:** `http://10.0.2.2:8001/api/v1`
- **Windows / Web / iOS Simulator:** `http://127.0.0.1:8001/api/v1`
- **Physical Device:** Set your machine's Wi-Fi LAN IP in `lib/core/network/api_endpoints.dart` (e.g. `http://192.168.1.100:8001/api/v1`).

---

## 6. Running Tests

### Backend Unit & Integration Tests (17 Tests)
```powershell
& "d:\Travel app\backend\.venv\Scripts\pytest.exe" -v "backend/tests"
```

### Flutter Frontend Tests (8 Tests)
```powershell
flutter test
```

### Flutter Static Analysis
```powershell
flutter analyze
```

---

## 7. Cloud Deployment & Production Release

### 1-Click Render Cloud Deployment
1. Push this repository to GitHub or GitLab.
2. In [Render Dashboard](https://dashboard.render.com), click **New +** -> **Blueprint**.
3. Connect your repository. Render automatically reads `backend/render.yaml` and provisions:
   - Managed **PostgreSQL Database** (`wanderly_db`) with automatic connection string generation.
   - Containerized **FastAPI Web Service** running `backend/Dockerfile` with health checks on `/api/v1/health`.
   - Automatic database migrations (`alembic upgrade head`) and destination seeding (`seed_data.py`) on boot.

### 1-Click Railway Deployment
1. Install Railway CLI or connect via [Railway.app](https://railway.app).
2. Add a PostgreSQL plugin service.
3. Link the backend repository. Railway automatically reads `railway.json` and executes `entrypoint.sh`.

### Production Android APK
The release APK is compiled and ready at:
`build\app\outputs\flutter-apk\app-release.apk`

To build the APK baked with your specific custom live cloud backend URL:
```powershell
flutter build apk --release --dart-define=API_URL=https://<YOUR-RENDER-OR-RAILWAY-DOMAIN>/api/v1
```

