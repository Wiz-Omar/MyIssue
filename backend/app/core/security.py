import hashlib
import os
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
JWT_ALGORITHM = os.environ["JWT_ALGORITHM"]
password_hash = PasswordHash.recommended()

def encode_jwt_token(payload: dict):
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def decode_jwt_token(token: str):
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])

def verify_password(plain_password, hashed_password: str | None = None) -> bool:
    #calling verify with not hash_password allows burning the same time when no user is found
    #makes the response timing indistinguishable for an attacker
    if not hashed_password:
        hashed_password = password_hash.hash("dummypassword")
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password):
    return password_hash.hash(password)

def hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode()).hexdigest()

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return encode_jwt_token(to_encode)
