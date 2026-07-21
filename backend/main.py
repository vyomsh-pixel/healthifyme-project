import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()  # picks up backend/.env (or root .env if run from root)

from backend.database import initialise_database
from backend.routes.api import router as api_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialise_database()
    yield

app = FastAPI(
    title="Health.io API",
    version="2.0.0",
    description="A privacy-aware wellness tracker. It provides general wellness information, not medical diagnosis.",
    lifespan=lifespan,
)

# Allow the Vite dev server (and later, your deployed frontend) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:8001",
        os.getenv("FRONTEND_URL", "https://healthio-coral.vercel.app")
    ],
    allow_origin_regex=r"https://healthio.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "healthio-api", "version": app.version}

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Health.io API is running!"}
