# Vercel deployment

AgriAI deploys as two Vercel Services in one project: a FastAPI backend and a
Vite static frontend. The frontend and `/api/v1` API share a domain; client-side
routes are rewritten to the frontend entry page.

## Before deploying

1. Create a managed PostgreSQL database (Neon or another PostgreSQL provider).
   Vercel's filesystem and SQLite databases are not persistent across function
   invocations.
2. In the Vercel project settings, add `DATABASE_URL` for Production, Preview,
   and Development as appropriate. Use the provider's pooled connection URL
   when available. The API supports `postgres://` and `postgresql://` URLs.
3. Apply the schema to each database from a machine with network access to it:

   ```powershell
   $env:DATABASE_URL = "postgresql://USER:PASSWORD@HOST/DATABASE?sslmode=require"
   python -m alembic upgrade head
   ```

   Keep the database URL out of source control. Repeat the migration for each
   environment's database before sending traffic to that deployment.
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
starts but price forecasts are unavailable. Do not commit artifacts containing
private training data or credentials.

## Runtime notes

- SQLite remains the local-development default; use PostgreSQL for Vercel.
- Migrations are a deployment step and are deliberately not run automatically
  by serverless function startup.
- Market and crop reference tables must be populated with verified data after
  schema migration. Development seed data is not production data.
