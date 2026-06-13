# Personalized Crypto Investor Dashboard

A full-stack assignment project for a personalized crypto investor dashboard. Users can sign up, complete onboarding preferences, view a personalized dashboard, refresh live coin prices, and submit feedback on dashboard content.

## Features

- Email/password signup and login with JWT-protected routes
- Onboarding preferences for investor type, selected assets, and content interests
- Personalized dashboard with four sections: Market News, Coin Prices, AI Insight of the Day, and Fun Crypto Meme
- Live CoinGecko price data with a dedicated price-only refresh endpoint
- Optional CryptoPanic and OpenRouter integrations with safe static/fallback behavior
- Feedback voting stored in PostgreSQL for future personalization improvements
- React/Vite frontend with desktop-first plain CSS UI

## Tech Stack

- Backend: FastAPI, SQLAlchemy, Alembic, PostgreSQL, PyJWT
- Frontend: React, Vite, React Router, plain CSS
- External data: CoinGecko, optional CryptoPanic, optional OpenRouter
- Deployment target: Render backend, Render PostgreSQL, Vercel frontend

## Local Setup

### Backend

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item ..\.env.example .env
```

Update `backend/.env` with a local PostgreSQL `DATABASE_URL` and a long random `JWT_SECRET_KEY`, then run migrations and start the API:

```powershell
alembic upgrade head
uvicorn app.main:app --reload
```

Backend local URLs:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

### Frontend

```powershell
cd frontend
Copy-Item .env.example .env
npm install
npm run dev
```

Frontend local URL:

- `http://127.0.0.1:5173`

For production builds:

```powershell
npm run build
```

Vite outputs the production bundle to `frontend/dist`.

## Environment Variables

Backend variables:

- `DATABASE_URL`: SQLAlchemy PostgreSQL URL, for example `postgresql+psycopg://USER:PASSWORD@HOST:5432/DB_NAME`
- `APP_NAME`: FastAPI title
- `ENVIRONMENT`: environment label such as `local` or `production`
- `DEBUG`: `false` for production
- `JWT_SECRET_KEY`: long random JWT signing secret
- `JWT_ALGORITHM`: usually `HS256`
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`: token lifetime
- `CORS_ALLOWED_ORIGINS`: comma-separated frontend origins, for example `http://127.0.0.1:5173,https://your-app.vercel.app`
- `COINGECKO_API_KEY`: optional CoinGecko key
- `CRYPTOPANIC_API_KEY`: optional CryptoPanic key
- `OPENROUTER_API_KEY`: optional OpenRouter key
- `OPENROUTER_MODEL`: optional model name; defaults to `openai/gpt-4o-mini`

Frontend variable:

- `VITE_API_BASE_URL`: backend base URL, for example `http://127.0.0.1:8000` locally or `https://your-api.onrender.com` in Vercel

Do not commit `.env` files or real credentials.

## API and Data Behavior

- `GET /dashboard` returns the full normalized dashboard.
- `GET /dashboard/coin-prices` returns only the Coin Prices section so the frontend can refresh prices every 60 seconds without replacing news, AI insight, or meme content.
- `POST /feedback` stores thumbs up/down feedback by user, section, content ID, vote, and optional message.
- CoinGecko live prices are attempted by default and fall back to safe static rows if unavailable.
- CryptoPanic is optional. When no key is configured, or the provider fails, the app uses `backend/app/data/static_news.json`.
- OpenRouter is optional. It was designed for a free model path, and the app uses a safe educational fallback when no key is configured or the provider fails.
- Memes rotate from `backend/app/data/memes.json`; no scraping is used.

## Deployment

### Render PostgreSQL

1. Create a Render PostgreSQL database.
2. Keep the internal connection string/private database details in Render and private submission notes only.
3. Use a SQLAlchemy-compatible URL in the backend `DATABASE_URL`, for example `postgresql+psycopg://USER:PASSWORD@HOST:5432/DB_NAME`.
4. Do not commit the database URL.

### Render Backend

Create a Render Web Service from the repository:

- Root directory: `backend`
- Runtime: Python
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Set backend environment variables in Render:

- `DATABASE_URL`
- `APP_NAME=Crypto Investor Dashboard API`
- `ENVIRONMENT=production`
- `DEBUG=false`
- `JWT_SECRET_KEY`
- `JWT_ALGORITHM=HS256`
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60`
- `CORS_ALLOWED_ORIGINS=https://your-vercel-app.vercel.app`
- optional provider keys if used

Run production migrations after the database is attached:

```bash
cd backend
alembic upgrade head
```

If Render runs commands from the `backend` root, run only:

```bash
alembic upgrade head
```

### Vercel Frontend

Create a Vercel project from the repository:

- Root directory: `frontend`
- Framework preset: Vite
- Build command: `npm run build`
- Output directory: `dist`
- Environment variable: `VITE_API_BASE_URL=https://your-render-api.onrender.com`

After Vercel deployment, update Render `CORS_ALLOWED_ORIGINS` with the final Vercel URL and redeploy the backend if needed.

## Reviewer Demo and DB Access

After deployment, I will create a reviewer demo user through the normal signup/onboarding flow. The app URL, demo credentials, and full PostgreSQL DB access details will be shared privately in the assignment submission, not committed to GitHub.

Production DB access will be provided through Render PostgreSQL external connection details. Keep local test data separate from production data and never commit credentials.

Useful reviewer SQL:

```sql
SELECT id, email, display_name, created_at FROM users;
SELECT user_id, risk_profile, preferred_coins, settings FROM user_preferences;
SELECT user_id, section_id, content_id, vote, message, created_at
FROM feedback
ORDER BY created_at DESC;
```

The production database can be clean except for a demo user and a few feedback rows generated during QA.

## Final QA Checklist

- Backend starts locally with `uvicorn app.main:app --reload`
- Frontend starts locally with `npm run dev`
- Frontend build passes with `npm run build`
- Signup and login work
- Onboarding preferences save and load
- Dashboard loads Market News, Coin Prices, AI Insight of the Day, and Fun Crypto Meme
- Coin Prices refresh manually and every 60 seconds
- Feedback voting stores rows in PostgreSQL
- Edit Preferences returns to dashboard with updated data
- Logout and protected route behavior work
- Render backend health/docs URLs work after deployment
- Vercel frontend can call the deployed backend
- Render/Vercel environment variables are configured
- No secrets, API keys, or DB credentials are committed

## Secrets Audit

`.gitignore` excludes root `.env`, `backend/.env`, `frontend/.env`, `backend/.venv/`, `frontend/node_modules/`, and `frontend/dist/`. The committed env files are examples only and contain placeholders.

Before final submission, run:

```powershell
git status --short
git ls-files | Select-String "\.env$"
rg -n "sk-[A-Za-z0-9_-]{20,}|OPENROUTER_API_KEY=sk|CRYPTOPANIC_API_KEY=[A-Za-z0-9]{20,}|JWT_SECRET_KEY=[A-Za-z0-9_-]{32,}|DATABASE_URL=postgresql.*://[a-z0-9_]+:[^@]+@" --glob "!README.md"
```

The expected result is no committed real API keys, JWT secrets, or database credentials.

## Bonus: Future Model Improvement

The stored feedback can support future personalization without adding ML now. Each vote is tied to a user, section, content ID, investor type/preferences context, and selected assets available through joins with `user_preferences`.

Over time, thumbs up/down aggregates could improve ranking of news, AI insights, and memes. The same data could later tune AI prompts or train a lightweight recommendation model. This was intentionally left as future work to keep the assignment focused and avoid over-engineering.

## Known Limitations and Future Work

- CryptoPanic is documented as optional/static fallback behavior; real production news tuning is not expanded here.
- OpenRouter prompt optimization and model evaluation are future work.
- CoinGecko caching and rate-limit management are not implemented.
- No admin panel is included; DB access is handled through Render PostgreSQL.
- Authentication is assignment-grade JWT with `localStorage`; production apps should consider httpOnly secure cookies, refresh-token handling, email verification, and password reset flows.
