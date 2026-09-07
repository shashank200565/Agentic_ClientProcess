from fastapi import FastAPI

app = FastAPI(title="Agentic Workflow Diagnostic & Redesign Platform")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
