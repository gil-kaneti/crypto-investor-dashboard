# AI Usage

I used AI tools during this project as engineering support, but I kept the implementation decisions, testing, and final review under my control. The work was done in focused sessions so I could understand, verify, and approve each part before moving forward.

## Tools Used

* I used ChatGPT for planning the project, reviewing architecture decisions, improving prompts, debugging issues, and building manual QA checklists.
* I used OpenAI Codex to help implement focused parts of the backend, frontend, documentation, and deployment preparation.
* I tested the OpenRouter integration once with a free model to verify that the AI Insight section can receive an external model response.
* During most development and QA, I used the fallback AI insight path to avoid unnecessary paid API usage, free-tier quota usage, and dependency on an external provider.

## Development Sessions

* Session 1: Backend foundation with FastAPI, PostgreSQL, SQLAlchemy, Alembic, environment configuration, and health checks.
* Session 2: Authentication, signup/login, JWT handling, protected backend routes, and user preferences.
* Session 3: Dashboard backend, external data providers, fallback behavior, feedback storage, and API testing.
* Session 4: React/Vite frontend, onboarding flow, dashboard UI, price refresh behavior, feedback voting, and frontend QA.
* Session 5: Deployment preparation, README cleanup, DB access instructions, AI usage documentation, bonus future improvement notes, and final QA checklist.

## My Verification Work

I manually tested the main flows throughout the project: backend startup, frontend startup, signup, login, onboarding, dashboard loading, live coin prices, price refresh, feedback voting, edit preferences, logout, protected routes, database persistence, and production frontend build.

I also reviewed network requests in the browser, checked database rows directly during development, verified migrations, reviewed Git changes before commits, and made sure secrets and `.env` files were not committed.

## Key Decisions I Made

I chose a practical stack for the assignment: FastAPI, React/Vite, PostgreSQL, SQLAlchemy, Alembic, and JWT authentication. I kept the scope focused on the requested dashboard instead of adding unrelated features such as wallets, trading, portfolio tracking, admin panels, or actual ML training.

I also chose to implement safe fallback behavior for optional providers. CoinGecko is used for live prices, while CryptoPanic and OpenRouter can be configured later with API keys. When those providers are unavailable, the app still works with static/fallback content. This keeps the project reliable for review while still showing how external APIs and AI integration fit into the design.
