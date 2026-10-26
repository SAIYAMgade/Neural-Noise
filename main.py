"""
main.py - Root ASGI entrypoint for Render and cloud hosting platforms.
Forwards to the primary FastAPI application defined in api.main:app.
"""
import sys

print("[Render Startup] Loading Neural Noise ASGI application...", flush=True)

from api.main import app

print("[Render Startup] Neural Noise ASGI application loaded successfully.", flush=True)

__all__ = ["app"]

if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
