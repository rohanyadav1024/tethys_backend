from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import schemas,tSchemas, models, utils, oauth2, config
from ..database import get_db

router = APIRouter(prefix='/smanager', tags=["Stock Manager"])

@router.get("/all" ,
            #  response_model=tSchemas.RequisitionOut,
            status_code=status.HTTP_200_OK)
def get_requisition_requests(db: Session = Depends(get_db)):

    req = db.query(models.Requisition).all()

    return {
            "status" : "200",
            "data" : req
        }

@router.get("/requisition" ,
            #  response_model=tSchemas.RequisitionOut,
            status_code=status.HTTP_200_OK)
def get_requisition_requests(emp_id: int, db: Session = Depends(get_db)):

    req = db.query(models.Requisition).filter(models.Requisition.req_by == emp_id).all()

    return {
            "status" : "200",
            "data" : req
        }