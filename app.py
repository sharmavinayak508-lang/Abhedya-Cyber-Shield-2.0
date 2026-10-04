
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from config import APP_NAME
from backend.database.db import get_db, Base, engine
from backend.api import auth, customers, admin

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title=APP_NAME)

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes - THIS IS WHAT YOU ARE MISSING
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(customers.router, prefix="/api/customers", tags=["Customers"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])

@app.get("/api/health")
def health():
    return {"status": "CyberShield Backend Running"}

# Serve frontend
# app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
