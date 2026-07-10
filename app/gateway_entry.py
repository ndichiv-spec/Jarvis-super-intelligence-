"""Gateway subprocess entry point — serves the FastAPI app via uvicorn."""

from __future__ import annotations

import sys

import uvicorn
from jarvis_api.gateway.app import create_gateway_app

host = sys.argv[1] if len(sys.argv) > 1 else "0.0.0.0"
port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000

app = create_gateway_app()

uvicorn.run(app, host=host, port=port, log_level="info")
