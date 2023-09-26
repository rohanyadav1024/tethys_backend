from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import schemas,tSchemas, models, utils, oauth2, config
from ..database import get_db

router = APIRouter(prefix='/pmanager', tags=["ProductionManager"])

# materials = {
# 1 : Raw Material
# 2 : PACKING MATERIAL
# 3 : CHEMICAL
# 4 : BELT
# 5 : LUBRICANT
# 6 : PU FITTINGS
# 7 : BOLT & NUT
# 8 : BOND
# 9 : WATER
# 10 :  BLOW MOULDING
# 11 :  ELECTRICAL
# 12 :  BEARING
# 13 :  WATBEARING 2RS1
# 14 :  BEARING BT1-0525
# 15 :  PADISOR BEARING 
# }

@router.get("/" ,
             response_model=tSchemas.MaterialListOut,
            status_code=status.HTTP_200_OK)
def get_materials_list(db: Session = Depends(get_db)):

    materials = db.query(models.Material).all()

    return {
            "status" : "200",
            "data" : materials
        }


@router.post("/create", 
            #  response_model=tSchemas.RequisitionOut,
             status_code=status.HTTP_200_OK)
def create_employee(reqs:tSchemas.RequisitionIn ,db: Session = Depends(get_db)):
    emp_query = db.query(models.Requisition).filter(models.Employees.id == reqs.req_by).first()

    if not emp_query:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="cannot send request")

    for item in reqs.items:
        req_query = db.query(models.Requisition).filter(models.Requisition.m_id == item.id).first()

        if req_query:
            req_query.qty_req += item.qty_req
            print(req_query)

        else:
            new_req = models.Requisition(m_id = item.id,
                                         qty_req = item.qty_req,
                                         remarks = item.remarks,
                                         req_by = reqs.req_by)

            db.add(new_req)
            db.commit()
            db.refresh(new_req)

    requisitions = db.query(models.Requisition).all()
    return {
        'status' :"200",
        'data' : requisitions
    }


    # emp_query = db.query(models.Requisition).filter(models.Employees.email == emp.email).first()

    # if emp_query:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    
    # if emp.phone:
    #     emp_with_num = db.query(models.Employees).filter(models.Employees.phone == emp.phone).first()
    #     if emp_with_num:
    #         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="phone number already exists")

    # db.add(db_emp)
    # db.commit()
    # db.refresh(db_emp)
    # # employee = db_emp
    # db_request = models.Emp_requests(emp_id = db_emp.id)
    # db.add(db_request)
    # db.commit()
    # db.refresh(db_emp)

    # return {
    #         "status" : "200",
    #         "data" : db_emp
    #     }
