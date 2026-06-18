from fastapi import FastAPI
from app.account.router import router as account_router
from app.core.logger import setup_logging

setup_logging()
app = FastAPI(title="Account Service")
app.include_router(account_router)