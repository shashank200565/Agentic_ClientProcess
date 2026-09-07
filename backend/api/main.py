from fastapi import FastAPI

try:
    from backend.api.routes.analysis import router as analysis_router
except ModuleNotFoundError:  # Supports the documented `cd backend` launch.
    from api.routes.analysis import router as analysis_router

app = FastAPI(title="Agentic Workflow Diagnostic & Redesign Platform")
app.include_router(analysis_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
