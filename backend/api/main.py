from fastapi import FastAPI

try:
    from backend.db.db import get_database_path
except ModuleNotFoundError:  # Supports the documented `cd backend` launch.
    from db.db import get_database_path

try:
    from backend.api.routes.analysis import router as analysis_router
    from backend.api.routes.reports import router as reports_router
    from backend.api.routes.sessions import router as sessions_router
except ModuleNotFoundError:  # Supports the documented `cd backend` launch.
    from api.routes.analysis import router as analysis_router
    from api.routes.reports import router as reports_router
    from api.routes.sessions import router as sessions_router

app = FastAPI(title="Agentic Workflow Diagnostic & Redesign Platform")
app.include_router(analysis_router)
app.include_router(reports_router)
app.include_router(sessions_router)


@app.on_event("startup")
def log_database_path() -> None:
    print(f"[startup] Database path: {get_database_path()}", flush=True)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
