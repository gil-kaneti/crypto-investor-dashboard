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
