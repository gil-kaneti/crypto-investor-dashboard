# Crypto Investor Dashboard

Full-stack foundation for the personalized crypto investor dashboard assignment.

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

Optional variables:

- `COINGECKO_API_KEY`: Optional CoinGecko demo/API key. Public CoinGecko requests are attempted without it.
- `CRYPTOPANIC_API_KEY`: Optional CryptoPanic key for live market news. Static local fallback news is used when missing or failing.
- `OPENROUTER_API_KEY`: Optional OpenRouter key for the AI insight. Safe fallback insight is used when missing, invalid, rate-limited, quota-limited, or failing.
- `OPENROUTER_MODEL`: Optional OpenRouter model name. Defaults to `openai/gpt-4o-mini`.

## Run The Backend

From the `backend` directory:

```powershell
uvicorn app.main:app --reload
```

The API will be available at:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

The backend allows local frontend requests from:

- `http://127.0.0.1:5173`
- `http://localhost:5173`

## Frontend Setup

The frontend lives in `frontend/` and uses React, Vite, and plain CSS.

Create a local frontend env file:

```powershell
cd frontend
Copy-Item .env.example .env
```

Expected frontend variable:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Install dependencies and run the Vite dev server:

```powershell
npm install
npm run dev
```

The frontend will be available at:

- `http://127.0.0.1:5173`

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

The frontend stores the JWT access token in `localStorage` for this demo and automatically sends it as `Authorization: Bearer <token>` on protected API requests. Production apps should consider stronger storage patterns such as httpOnly secure cookies.

Frontend auth flow:

- Signup calls `POST /auth/register`; because the backend returns a user instead of a token, the frontend redirects to login with a success message.
- Login calls `POST /auth/login`, stores the returned token, fetches `/auth/me`, then checks `/preferences`.
- If `/preferences` returns no saved preference row (`id: null`), the user is routed to onboarding.
- If preferences exist, the user is routed to the dashboard.
- Logout clears the local token and returns the user to login.

Auth endpoints:

- `POST /auth/register`: Creates a user with `name`, `email`, and `password`
- `POST /auth/login`: Accepts JSON `email` and `password`, returns a bearer access token
- `GET /auth/me`: Returns the current authenticated user

Preference endpoints:

- `GET /preferences`: Returns the current user's onboarding preferences
- `PUT /preferences`: Creates or updates onboarding preferences

Dashboard endpoints:

- `GET /dashboard`: Requires bearer auth and returns exactly four normalized sections: `market_news`, `coin_prices`, `ai_insight`, and `crypto_meme`
- `POST /feedback`: Requires bearer auth and stores thumbs up/down section feedback for future improvements

## Frontend Dashboard Behavior

The dashboard renders the normalized backend response only. It expects exactly four section IDs:

- `market_news`
- `coin_prices`
- `ai_insight`
- `crypto_meme`

The dashboard includes a manual `Refresh now` button and auto-refreshes every 60 seconds while the dashboard page is open. A countdown shows the next refresh time, and the current dashboard stays visible while fresh data is loading. The meme section is fetched again with each dashboard refresh, so it can change naturally whenever the backend returns a different static meme.

Each dashboard card supports thumbs up/down feedback through `POST /feedback`. The frontend sends `section_id`, the available `content_id`, and the selected vote.

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

Example dashboard response shape:

```json
{
  "user_id": 1,
  "generated_at": "2026-06-13T10:00:00Z",
  "preferences": {
    "crypto_assets": ["BTC", "ETH", "SOL"],
    "investor_type": "HODLer",
    "content_preferences": ["Market News", "Fun"]
  },
  "sections": [
    {
      "section_id": "market_news",
      "title": "Market News",
      "source": "static_fallback",
      "is_fallback": true,
      "generated_at": "2026-06-13T10:00:00Z",
      "items": []
    },
    {
      "section_id": "coin_prices",
      "title": "Coin Prices",
      "source": "coingecko",
      "is_fallback": false,
      "generated_at": "2026-06-13T10:00:00Z",
      "items": []
    },
    {
      "section_id": "ai_insight",
      "title": "AI Insight of the Day",
      "source": "safe_fallback",
      "is_fallback": true,
      "generated_at": "2026-06-13T10:00:00Z",
      "content_id": "ai-insight-fallback",
      "insight": "Educational crypto context...",
      "disclaimer": "Educational information only. Not financial advice."
    },
    {
      "section_id": "crypto_meme",
      "title": "Fun Crypto Meme",
      "source": "static_json",
      "is_fallback": false,
      "generated_at": "2026-06-13T10:00:00Z",
      "content_id": "meme-buy-high-sell-low",
      "caption": "When your strategy says DCA...",
      "image_url": "https://placehold.co/800x450/png?text=Crypto+Meme",
      "alt_text": "Crypto meme placeholder"
    }
  ]
}
```

Example feedback request:

```json
{
  "section_id": "market_news",
  "content_id": "fallback-news-bitcoin-etf-flows",
  "vote": "thumbs_up",
  "comment": "Useful summary"
}
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
- `GET /dashboard` without a token returns `401`
- `GET /dashboard` with `Authorization: Bearer <token>` returns four sections
- The dashboard still returns valid JSON when optional provider keys are omitted
- `POST /feedback` with `thumbs_up` or `thumbs_down` stores feedback for each dashboard section

Frontend manual verification:

- Start the backend at `http://127.0.0.1:8000`
- Start the frontend at `http://127.0.0.1:5173`
- Open the frontend and create a new account
- Confirm signup redirects to login with a clear success message
- Login and confirm the app routes to onboarding when preferences are missing
- Complete onboarding and save preferences
- Confirm the dashboard loads four sections: Market News, Coin Prices, AI Insight of the Day, and Fun Crypto Meme
- Click `Refresh now` and confirm the existing dashboard stays visible while refreshing
- Confirm the `Next refresh in 60s` countdown ticks down and resets after refresh
- Confirm the meme can change after dashboard refreshes
- Vote thumbs up/down on each dashboard card and confirm the thank-you state appears
- Use `Edit Preferences`, confirm existing preferences are prefilled, save changes, and return to the dashboard
- Logout and confirm the app returns to login

Example PowerShell flow:

```powershell
$token = "<access_token>"
Invoke-RestMethod http://127.0.0.1:8000/dashboard -Headers @{ Authorization = "Bearer $token" }
Invoke-RestMethod http://127.0.0.1:8000/feedback `
  -Method Post `
  -Headers @{ Authorization = "Bearer $token" } `
  -ContentType "application/json" `
  -Body '{"section_id":"market_news","content_id":"fallback-news-bitcoin-etf-flows","vote":"thumbs_up","comment":"Useful"}'
```

## Database Verification

Open PostgreSQL with your local credentials:

```powershell
psql -d crypto_dashboard
```

Inspect the stored rows:

```sql
SELECT id, email, display_name, hashed_password FROM users;
SELECT user_id, risk_profile, preferred_coins, settings FROM user_preferences;
SELECT id, user_id, section_id, content_id, vote, message, created_at FROM feedback ORDER BY id DESC;
```

Confirm `hashed_password` starts with a bcrypt prefix such as `$2b$` and does not contain the plaintext password.

Confirm ignored local environment files are not tracked:

```powershell
git status --short
```

## Provider Fallback Behavior

All provider responses are normalized before returning to the frontend. Raw CoinGecko, CryptoPanic, and OpenRouter payloads are not exposed.

- CoinGecko failures return a valid `coin_prices` section with fallback coin rows and `is_fallback: true`.
- Missing CryptoPanic key returns local static news from `backend/app/data/static_news.json`.
- CryptoPanic errors, rate limits, or quota issues also return static fallback news.
- Missing OpenRouter key returns a safe educational fallback insight.
- OpenRouter errors, invalid key, rate limits, or quota issues also return the safe fallback insight.
- AI insight text is educational only and includes a not-financial-advice disclaimer.
- Memes are selected from `backend/app/data/memes.json`; no scraping is used.
