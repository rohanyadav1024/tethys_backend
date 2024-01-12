from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import schemas, models, utils, oauth2, database

router = APIRouter(tags=["Authentication"])


@router.post('/login', response_model=schemas.LoginResponse)
def user_login(user_credential: schemas.OAuth2PasswordRequestFormJSON,
               db: Session = Depends(database.get_db)):

    db_user = db.query(models.Owners).filter(
        models.Owners.email == user_credential.username).first()
    is_owner = True

    if not db_user:
        is_owner = False
        db_user = db.query(models.Employees).filter(
            models.Employees.email == user_credential.username).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials")

    if not utils.verify(plain_password=user_credential.password,
                        hashed_password=db_user.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials")

    token = oauth2.create_access_token(
        data={"user_id": db_user.id, "is_owner": is_owner})
    
    user_detials = {"id": db_user.id,
                    "name": db_user.name,
                    "email": db_user.email,
                    "phone": db_user.phone,
                    "created_at": db_user.created_at,
                    "is_active": db_user.is_active,
                    "role" : db_user.role if hasattr(db_user, "role") else 0
                    }

    # if not is_owner:
    #     user_detials["role"] = db_user.role
    #     return schemas.LoginResponseEmployee(access_token=token, token_type="bearer", employee=user_detials)

    return schemas.LoginResponse(status='200',
        access_token=token, token_type="bearer", user=user_detials)
    # return schemas.Token(access_token=token, token_type="bearer")
