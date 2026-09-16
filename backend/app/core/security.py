import os

import jwt
from pwdlib import PasswordHash

JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
JWT_ALGORITHM = os.environ["JWT_ALGORITHM"]
password_hash = PasswordHash.recommended()

def encode_jwt_token(payload: dict):
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def decode_jwt_token(token: str):
    return jwt.decode(token, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_password(plain_password, hashed_password: str | None = None) -> bool:
    # Calling verify with not hash_password allows burning the same time when no user is found
    # Makes the response timing indistinguishable for an attacker
    if not hashed_password:
        hashed_password = password_hash.hash("dummypassword")
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password):
    return password_hash.hash(password)
