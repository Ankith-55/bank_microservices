from fastapi import FastAPI
from app.transaction.router import router as transaction_router
from app.core.logger import setup_logging

setup_logging()
app = FastAPI(title="Transaction Service")
app.include_router(transaction_router)