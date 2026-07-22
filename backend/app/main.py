from fastapi import FastAPI

from backend.app.api.routes import comments

app = FastAPI(title="Clasificador de sentimiento — API")

app.include_router(comments.router, prefix="/api")


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
