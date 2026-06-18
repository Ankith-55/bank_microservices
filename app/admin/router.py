from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.admin.service import AdminService
from app.core.dependencies import get_db, get_admin_user
from app.models.user import User
from app.celery_tasks.interest import calculate_interest_task

router = APIRouter()

@router.post("/interest/apply")
async def apply_interest(admin: User = Depends(get_admin_user)):
    # Trigger Celery task
    task = calculate_interest_task.delay()
    return {"message": "Interest calculation started", "task_id": task.id}

@router.get("/users", response_model=list[dict])
async def list_users(
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    service = AdminService(db)
    users = await service.get_all_users()
    return [
        {
            "id": str(u.id),
            "full_name": u.full_name,
            "email": u.email,
            "role": u.role,
            "is_active": u.is_active
        }
        for u in users
    ]

@router.get("/accounts", response_model=list[dict])
async def list_accounts(
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    service = AdminService(db)
    accounts = await service.get_all_accounts()
    return [
        {
            "account_number": a.account_number,
            "user_id": str(a.user_id),
            "balance": a.balance
        }
        for a in accounts
    ]