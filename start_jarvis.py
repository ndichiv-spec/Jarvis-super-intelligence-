import sys
sys.path.insert(0, '.')
from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn
from core.api.main import create_application

@asynccontextmanager
async def noop_lifespan(app: FastAPI):
    yield

app = create_application()
app.router.lifespan_context = noop_lifespan

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
