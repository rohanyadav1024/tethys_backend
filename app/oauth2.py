from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import jwt, JWTError
from typing_extensions import Annotated

from . import schemas, database, models
from .config import settings

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
EXPIRE_MINUTES = settings.expiry_time_taken

class JSONOAuth2PasswordBearer(OAuth2PasswordBearer):
    def __init__(self, tokenUrl: str):
        super().__init__(tokenUrl)
    
    async def __call__(self, request: Request) -> str:
        body = await request.json()
        token = body.get("access_token")
        if token:
            return token
        else:
            return await super().__call__(request)

json_oauth2_scheme = JSONOAuth2PasswordBearer(tokenUrl='login')


def create_access_token(data : dict):
    to_encode = data.copy()
    exp_time = int((datetime.now() + timedelta(minutes=EXPIRE_MINUTES)).timestamp())

    to_encode.update({'expiry' : exp_time})
    encoded_jwt = jwt.encode(claims=to_encode, algorithm=ALGORITHM, key=SECRET_KEY)
    return encoded_jwt



def verify_access_token(token: str, credential_exception):
    try:
        payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        id : str = payload.get("user_id")
        is_owner : bool = payload.get("is_owner")

        if id is None:
            raise credential_exception

        token_data = schemas.TokenData(id=id, isowner = is_owner)
        return token_data
    
    except JWTError:
        raise credential_exception
    

    
def get_current_user_key(
        token : str = Depends(json_oauth2_scheme),
        db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials for getting user")

    user_token = verify_access_token(
        token=token,
        credential_exception=credentials_exception)
    
    
    if user_token.isowner :
        owner = db.query(models.Owners).filter(
        models.Owners.id == user_token.id).first()
        return owner

    employee = db.query(models.Employees).filter(
    models.Employees.id == user_token.id).first()
    return employee