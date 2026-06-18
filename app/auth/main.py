from fastapi import FastAPI
from app.auth.router import router as auth_router
from app.core.logger import setup_logging

setup_logging()
app = FastAPI(title="Auth Service")
app.include_router(auth_router)