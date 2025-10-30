from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from database import get_db
from models import User
from typing import Optional

async def get_token_header(x_token: Optional[str] = Header(None)):
    if not x_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-Token header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return x_token

async def get_current_user(x_token: str = Depends(get_token_header), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.token == x_token).first()
    if not user or not user.verify_token(x_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
