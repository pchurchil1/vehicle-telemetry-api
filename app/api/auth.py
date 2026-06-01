from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import ROLE_ADMIN, require_roles
from app.schemas.auth import LoginRequest, TokenOut, UserCreate, UserOut
from app.services.auth_service import AuthService


router = APIRouter()


@router.post("/auth/bootstrap", response_model=UserOut, status_code=201)
def bootstrap_admin(payload: UserCreate, db: Session = Depends(get_db)):
    return AuthService(db).bootstrap_admin(payload)


@router.post("/auth/login", response_model=TokenOut)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    return AuthService(db).login(payload)


@router.post(
    "/users",
    response_model=UserOut,
    status_code=201,
    dependencies=[Depends(require_roles(ROLE_ADMIN))],
)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    return AuthService(db).create_user(payload)


@router.get(
    "/users",
    response_model=list[UserOut],
    dependencies=[Depends(require_roles(ROLE_ADMIN))],
)
def list_users(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return AuthService(db).list_users(limit=limit, offset=offset)
