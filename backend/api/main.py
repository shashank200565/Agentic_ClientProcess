from fastapi import FastAPI

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


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
