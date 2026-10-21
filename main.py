"""
main.py - Root ASGI entrypoint for Render and cloud hosting platforms.
Forwards to the primary FastAPI application defined in api.main:app.
"""
from api.main import app

__all__ = ["app"]

if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
