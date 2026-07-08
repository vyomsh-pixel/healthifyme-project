from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import dashboard

app = FastAPI(title="Health.io API")

# Allow the Vite dev server (and later, your deployed frontend) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])


@app.get("/api/health")
def health_check():
    return {"status": "ok"}