# Vercel deployment

AgriAI deploys as two Vercel Services in one project: a FastAPI backend and a
Vite static frontend. The frontend and `/api/v1` API share a domain; client-side
routes are rewritten to the frontend entry page.

## Before deploying

1. Create a managed PostgreSQL database (Neon or another PostgreSQL provider).
   Vercel's filesystem and SQLite databases are not persistent across function
   invocations.
2. In the Vercel project settings, add `DATABASE_URL` for Production, Preview,
   and Development as appropriate. For Neon, use the pooled `DATABASE_URL` for
   the application runtime. The API supports `postgres://` and `postgresql://`
   URLs.
3. Apply the schema to each database from a machine with network access to it:

   ```powershell
   # Use Neon's direct (unpooled) URL for migrations.
   $env:DATABASE_URL = "<Neon direct DATABASE_URL_UNPOOLED>"
   python -m alembic upgrade head
   Remove-Item Env:DATABASE_URL
   ```

   Neon CLI provides this direct URL as `DATABASE_URL_UNPOOLED`; temporarily use
   it as `DATABASE_URL` when running Alembic. Keep connection URLs out of source
   control. Repeat the migration for each environment's database before
   sending traffic to that deployment.
4. Import the repository into Vercel with the repository root (`.`) as the
   project root. Keep the default framework/build detection; `vercel.json`
   defines the FastAPI and Vite services and their routing.
5. Deploy and verify `/api/v1/health`, then open `/dashboard` directly to
   verify the API and frontend routes.

The frontend uses same-origin `/api/v1` requests by default. If you instead
configure `VITE_API_URL` to use a separate API origin, set the backend's
`CORS_ORIGINS` environment variable to a JSON array containing the exact
frontend origins. Do not use `*` with credentialed CORS.

## Machine-learning artifacts

The repository includes `models/yield_model.pkl`, a model trained on synthetic
data for development and demonstration. It is not validated for real farming
decisions; replace it with an independently validated artifact before
production use. Other trained model files, including the market price model,
remain excluded by `.gitignore`. Without the price model artifact, the API
starts but price forecasts are unavailable. Keep the scikit-learn runtime
version aligned with the version used to train and validate the committed model
artifact; the current artifact is pinned to scikit-learn 1.6.0. Do not commit
artifacts containing private training data or credentials.

## Runtime notes

- SQLite remains the local-development default; use PostgreSQL for Vercel.
- Migrations are a deployment step and are deliberately not run automatically
  by serverless function startup.
- Market and crop reference tables must be populated with verified data after
  schema migration. Development seed data is not production data.
