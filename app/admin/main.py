from fastapi import FastAPI
from app.admin.router import router as admin_router
from app.core.logger import setup_logging

setup_logging()
app = FastAPI(title="Admin Service")
app.include_router(admin_router)