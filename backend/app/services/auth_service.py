"""用户认证服务"""

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import RegisterRequest, UserResponse
from app.core.security import hash_password, verify_password, create_access_token
from app.core.exceptions import InvalidCredentialsException, EmailAlreadyExistsException


class AuthService:

    @staticmethod
    def register(db: Session, req: RegisterRequest) -> tuple[User, str]:
        existing = db.query(User).filter(User.email == req.email).first()
        if existing:
            raise EmailAlreadyExistsException()
        user = User(
            email=req.email,
            username=req.username,
            password_hash=hash_password(req.password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        token = create_access_token(user)
        return user, token

    @staticmethod
    def login(db: Session, email: str, password: str) -> tuple[User, str]:
        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.password_hash):
            raise InvalidCredentialsException()
        token = create_access_token(user)
        return user, token

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User | None:
        return db.query(User).filter(User.id == user_id).first()
