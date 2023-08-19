from fastapi import APIRouter, status, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List

from .. import schemas, models, utils, oauth2
from ..database import get_db
from ..config import settings


router = APIRouter(prefix='/owner', tags=["Owner"])

@router.get("/",
            response_model=List[schemas.OwnerOut],
            status_code=status.HTTP_200_OK)
def get_owners_list(db: Session = Depends(get_db)):

    own_query = db.query(models.Owners).all()
    return own_query


@router.post("/create", 
             response_model=schemas.OwnerOut,
             status_code=status.HTTP_201_CREATED)
def create_employee(own:schemas.CreateOwner ,db: Session = Depends(get_db)):
    own_query = db.query(models.Owners).filter(models.Owners.email == own.email).first()

    if own_query:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Owner already exists")

    if own.secret_key != settings.secret_owner_key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Secret key invalid")

    new_own = own.model_dump(exclude={"password", "secret_key"})
    hashed_pass = utils.hash(own.password)
    db_own = models.Owners(**new_own,
                          password = hashed_pass)
    db.add(db_own)
    db.commit()
    db.refresh(db_own)

    return db_own




@router.get("/user", response_model=schemas.OwnerOut, status_code=status.HTTP_302_FOUND)
def get_single_user(user_input : schemas.UserId,
                    db: Session = Depends(get_db),
                    current_owner : models.Owners = Depends(oauth2.get_current_user_key)):
    
    if current_owner is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,detail="Invalid Credentials, Please Login again")
    
    if current_owner.id != user_input.user_id:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,detail="Invalid Credentials, You're not user")
    
    user = db.query(models.Owners).filter(models.Owners.id == user_input.user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"You are not an owner")
    else:
        return user
    

@router.delete("/delete")
def delete_user(keydata: schemas.SecretKey,
                db: Session = Depends(get_db),
                current_owner : models.Owners = Depends(oauth2.get_current_user_key)):
    
    if keydata.secret_key != settings.secret_owner_key:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,detail="Entered Invalid Credentials")

    if current_owner is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,detail="Entered Invalid Credentials")

    user = db.query(models.Owners).filter(models.Owners.id == current_owner.id)
    if user.first() == None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"User with id {current_owner.id} not found")


    user.delete(synchronize_session = False)
    db.commit()

    return {"status" : "successfully deleted owner"}