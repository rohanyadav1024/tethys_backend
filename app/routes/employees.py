from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import schemas, models, utils, oauth2, config
from ..database import get_db

router = APIRouter(prefix='/employees', tags=["employee"])

#roles = {
#   stockmanger = 1
#   production manager = 2
#   gate keeper = 3
# }

@router.get("/" , response_model=List[schemas.EmployeeOut],
            status_code=status.HTTP_200_OK)
def get_employees(db: Session = Depends(get_db)):

    emp_query = db.query(models.Employees).all()

    return emp_query


@router.post("/create", 
             response_model=schemas.EmployeeOut,
             status_code=status.HTTP_201_CREATED)
def create_employee(emp:schemas.CreateEmployee ,db: Session = Depends(get_db)):
    emp_query = db.query(models.Employees).filter(models.Employees.email == emp.email).first()

    if emp_query:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    new_emp = emp.model_dump(exclude={"password"})
    hashed_pass = utils.hash(emp.password)
    db_emp = models.Employees(**new_emp,
                          password = hashed_pass)
    db.add(db_emp)
    db.commit()
    db.refresh(db_emp)
    # employee = db_emp
    db_request = models.Emp_requests(emp_id = db_emp.id)
    db.add(db_request)
    db.commit()
    db.refresh(db_emp)

    return db_emp


@router.get("/user", response_model=schemas.EmployeeOut, status_code=status.HTTP_302_FOUND)
def get_single_user(user_input : schemas.UserId,
                    db: Session = Depends(get_db),
                    current_user = Depends(oauth2.get_current_user_key)):
    
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,detail="Invalid Credentials, Please Login again")
    
    #check login id is owner or employee
    if hasattr(current_user, 'role') and current_user.id != user_input.user_id:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,detail="Invalid Credentials")
    
    user = db.query(models.Employees).filter(models.Employees.id == user_input.user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Credentials, can not access")
    else:
        return user
    

@router.delete("/delete")
def delete_user(user_input : schemas.UserId,
                db: Session = Depends(get_db),
                current_user = Depends(oauth2.get_current_user_key)):
    
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,detail="Invalid Credentials, login again")
    
    if hasattr(current_user, 'role') and current_user.id != user_input.user_id:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,detail="Invalid Credentials")

    user = db.query(models.Employees).filter(models.Employees.id == user_input.user_id)
    if user.first() == None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"User with id {user_input.user_id} not found")


    user.delete(synchronize_session = False)
    db.commit()

    return {"status" : "successfully deleted employee"}