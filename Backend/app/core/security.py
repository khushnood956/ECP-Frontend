from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

SECRET_KEY = "lc3vAV68K8zii-d6aWr19q2oMXGszOuZk7RaPuJZ_9s"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def get_password_hash(password: str) -> str:
    # bcrypt has a 72-byte max password length limitation
    password_clean = password.encode("utf-8")[:72]
    return bcrypt.hashpw(password_clean, bcrypt.gensalt()).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_clean = plain_password.encode("utf-8")[:72]
    hashed_password_bytes = hashed_password.encode("utf-8")
    try:
        return bcrypt.checkpw(password_clean, hashed_password_bytes)
    except Exception:  # noqa: BLE001
        return False

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
