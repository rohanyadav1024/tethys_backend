from passlib.context import CryptContext

from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(plain_password: str):
    return pwd_context.hash(plain_password)


def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)




