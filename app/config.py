import os
import uuid

SECRET_KEY = os.getenv("SECRET_KEY", "your-very-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 48  # 48 часов

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

TOKEN_EXPIRE_HOURS = 48

# Для UUID токенов генерация
TOKEN_LENGTH = 36
