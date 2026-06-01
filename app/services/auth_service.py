from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.user_repo import UserRepository
from app.schemas.auth import LoginRequest, TokenOut, UserCreate


class AuthService:
    def __init__(self, db: Session):
        self.users = UserRepository(db)

    def bootstrap_admin(self, data: UserCreate):
        if self.users.count() > 0:
            raise HTTPException(status_code=409, detail="Users already exist")
        if data.role != "admin":
            raise HTTPException(status_code=400, detail="Bootstrap user must be admin")
        return self.users.create(data, hash_password(data.password))

    def create_user(self, data: UserCreate):
        try:
            return self.users.create(data, hash_password(data.password))
        except IntegrityError:
            raise HTTPException(status_code=409, detail="Username already exists")

    def list_users(self, limit: int = 50, offset: int = 0):
        limit = min(max(limit, 1), 100)
        offset = max(offset, 0)
        return self.users.list(limit=limit, offset=offset)

    def login(self, data: LoginRequest) -> TokenOut:
        user = self.users.get_by_username(data.username)
        if not user or not user.is_active or not verify_password(data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return TokenOut(access_token=create_access_token(user.username, user.role))
