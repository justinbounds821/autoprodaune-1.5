# Sentry Monitoring Configuration

This directory documents how backend Sentry tracing is initialised inside the FastAPI application.

## Environment variables

| Variable | Description |
| --- | --- |
| `SENTRY_DSN` | Project DSN from Sentry. When set, the backend enables Sentry tracing automatically. |
| `SENTRY_TRACES_SAMPLE_RATE` | Optional float between 0 and 1 for performance tracing. Defaults to `0.2`. |
| `SENTRY_PROFILES_SAMPLE_RATE` | Optional profiling sample rate. Defaults to `0.0`. |
| `ENVIRONMENT` | Optional environment tag propagated to Sentry. |

## Frontend LogRocket

Frontend monitoring is initialised via `src/lib/monitoring.ts`. Set the following variables inside the `.env` file in `02_FRONTEND_UI_CLEAN/`:

- `VITE_ENABLE_ERROR_REPORTING=true`
- `VITE_LOGROCKET_APP_ID=<your-app-id>`
- `VITE_APP_VERSION=<version-label>`

Once configured, LogRocket sessions are started when the Health ping runs at boot.
