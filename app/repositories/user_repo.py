from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import UserCreate


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def count(self) -> int:
        return self.db.query(User).count()

    def get_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).first()

    def list(self, limit: int = 50, offset: int = 0) -> list[User]:
        return self.db.query(User).order_by(User.id.asc()).offset(offset).limit(limit).all()

    def create(self, data: UserCreate, password_hash: str) -> User:
        user = User(username=data.username, password_hash=password_hash, role=data.role)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
