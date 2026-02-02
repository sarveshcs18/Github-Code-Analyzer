from fastapi import FastAPI
from app.core.config import settings
from app.api.api_v1.api import api_router
from loguru import logger
import sys

# Setup logging
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add("logs/app.log", rotation="10 MB", retention="5 days", level="DEBUG")

app = FastAPI(
    title="GitHub Repo Analyzer",
    description="Analyze GitHub repositories using Gemini",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app.include_router(api_router, prefix="/api/v1")

# Mount static files if they exist (Production/Docker)
static_dir = "/app/static"
if os.path.exists(static_dir):
    app.mount("/assets", StaticFiles(directory=f"{static_dir}/assets"), name="assets")

    @app.get("/")
    async def read_index():
        return FileResponse(f"{static_dir}/index.html")

    # Catch-all for React Router (if we used client-side routing, needed here too)
    @app.exception_handler(404)
    async def custom_404_handler(_, __):
        return FileResponse(f"{static_dir}/index.html")

@app.get("/health")
def health_check():
    return {"status": "ok", "app_name": "GitHub Repo Analyzer"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
