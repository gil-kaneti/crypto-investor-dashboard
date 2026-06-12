# Crypto Investor Dashboard

Backend foundation for the crypto investor dashboard assignment.

## Backend Setup

On Windows, use the Python launcher (`py`) so you do not accidentally hit the Microsoft Store `python` alias.

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Environment

Copy the example environment file and update values for your local PostgreSQL database:

```powershell
Copy-Item ..\.env.example .env
```

Required variables:

- `DATABASE_URL`: PostgreSQL SQLAlchemy URL, for example `postgresql+psycopg://postgres:postgres@localhost:5432/crypto_dashboard`
- `APP_NAME`: FastAPI application title
- `ENVIRONMENT`: Local environment label
- `DEBUG`: FastAPI debug flag
- `JWT_SECRET_KEY`: Long random secret used to sign JWT access tokens
- `JWT_ALGORITHM`: JWT signing algorithm, for example `HS256`
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`: Access token lifetime in minutes

## Run The Backend

From the `backend` directory:

```powershell
uvicorn app.main:app --reload
```

The API will be available at:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

## Database Migrations

Make sure PostgreSQL is running and the database named in `DATABASE_URL` exists.
The example credentials in `.env.example` are placeholders; replace them with your local PostgreSQL username, password, host, port, and database name.

From the `backend` directory:

```powershell
alembic upgrade head
```

To create future migrations after model changes:

```powershell
alembic revision --autogenerate -m "describe change"
```

## Authentication

This backend uses simple bearer JWT authentication for the assignment. It does not use OAuth, third-party login, session cookies, refresh tokens, email verification, or password reset flows.

Passwords are hashed with bcrypt before storage. JWT access tokens are signed with the `JWT_SECRET_KEY` value from your environment.

Auth endpoints:

- `POST /auth/register`: Creates a user with `name`, `email`, and `password`
- `POST /auth/login`: Accepts JSON `email` and `password`, returns a bearer access token
- `GET /auth/me`: Returns the current authenticated user

Preference endpoints:

- `GET /preferences`: Returns the current user's onboarding preferences
- `PUT /preferences`: Creates or updates onboarding preferences

Example request bodies:

```json
{
  "name": "Ada Lovelace",
  "email": "ada@example.com",
  "password": "strong-password"
}
```

```json
{
  "email": "ada@example.com",
  "password": "strong-password"
}
```

```json
{
  "crypto_assets": ["BTC", "ETH", "SOL"],
  "investor_type": "HODLer",
  "content_preferences": ["Market News", "Charts", "Fun"]
}
```

Use the login response token as:

```text
Authorization: Bearer <access_token>
```

## Manual Test Checklist

From the `backend` directory:

```powershell
python -m pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Then verify:

- `GET http://127.0.0.1:8000/health` returns `{"status":"ok"}`
- `http://127.0.0.1:8000/docs` loads
- `POST /auth/register` creates a new user
- Registering the same email again returns a clean duplicate-email error
- `POST /auth/login` returns an `access_token`
- Logging in with an invalid password returns `401`
- `GET /auth/me` without a token returns `401`
- `GET /auth/me` with `Authorization: Bearer <token>` returns the user profile
- `GET /preferences` with a token returns empty/default onboarding preferences before setup
- `PUT /preferences` with a token saves assets, investor type, and content preferences
- `GET /preferences` returns the saved values

## Database Verification

Open PostgreSQL with your local credentials:

```powershell
psql -d crypto_dashboard
```

Inspect the stored rows:

```sql
SELECT id, email, display_name, hashed_password FROM users;
SELECT user_id, risk_profile, preferred_coins, settings FROM user_preferences;
```

Confirm `hashed_password` starts with a bcrypt prefix such as `$2b$` and does not contain the plaintext password.

Confirm ignored local environment files are not tracked:

```powershell
git status --short
```
