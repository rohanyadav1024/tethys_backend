from fastapi import APIRouter, status, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List

from .. import schemas, models, oauth2
from ..database import get_db


router = APIRouter(prefix='/requests', tags=["Request"])

@router.get("/",
            # response_model=schemas.RequestsData,
            status_code=status.HTTP_200_OK)
def get_owners_list(db: Session = Depends(get_db)):

    req_query = db.query(models.Emp_requests, models.Employees).join(models.Employees, models.Employees.id == models.Emp_requests.emp_id, isouter=True).all()

    request = [
        {
            "req_id" : req.req_id,
            "employee" : {
                "id": emp.id,
                "name": emp.name,
                "email": emp.email,
                "role": emp.role,
                "phone": emp.phone,
                "created_at": emp.created_at,
                "is_active": emp.is_active,
            },
        }
        for req, emp in req_query
    ]
    return {
        "status" : "200",
        "data" : request
    }


@router.post("/permit",
             response_model=schemas.EmployeeOut,
             status_code=status.HTTP_200_OK)
def grant_permission(
        req: schemas.Requests,
        db: Session = Depends(get_db),
        # current_owner : models.Owners = Depends(oauth2.get_current_user_key)
        ):

    # if current_owner is None:
    #     raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,detail="you are not an owner")

    db_request = db.query(models.Emp_requests).filter(models.Emp_requests.req_id == req.req_id).first()
    if not db_request :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No request available with this id")
    
    emp = db.query(models.Employees).filter(db_request.emp_id == models.Employees.id).first()
    if not emp :
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    
    emp.is_active = True;
    db.delete(db_request)
    db.commit()
    db.refresh(emp)

    return emp

@router.delete("/delete", status_code=status.HTTP_200_OK)
def delete_request(
        req: schemas.Requests,
        db: Session = Depends(get_db),
                ):
    request = db.query(models.Emp_requests).filter(models.Emp_requests.req_id == req.req_id)
    if request.first() == None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"User with request id {req.req_id} not found")


    request.delete(synchronize_session = False)
    db.commit()

    return {
         "status" : "200",
         "message" : "successfully deleted employee data"
         }