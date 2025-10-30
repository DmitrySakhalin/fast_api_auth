from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone, timedelta
from database import Base
from passlib.context import CryptContext
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(128), unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")

    token = Column(String(36), unique=True, index=True, nullable=True)  # UUID токен
    token_expire = Column(DateTime(timezone=True), nullable=True)

    advertisements = relationship("Advertisement", back_populates="owner")

    def set_password(self, password: str):
        self.hashed_password = pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.hashed_password)

    def set_token(self):
        self.token = str(uuid.uuid4())
        self.token_expire = datetime.now(timezone.utc) + timedelta(hours=48)

    def verify_token(self, token: str) -> bool:
        if self.token != token or not self.token_expire:
            return False
        expire = self.token_expire
        if expire.tzinfo is None:
            expire = expire.replace(tzinfo=timezone.utc)
        return expire > datetime.now(timezone.utc)


class Advertisement(Base):
    __tablename__ = "advertisements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="advertisements")
