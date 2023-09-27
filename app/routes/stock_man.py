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

    req_query = db.query(models.Requisition, models.Material).join(models.Material, models.Material.id == models.Requisition.m_id).all()

    request = [
        {
            "req_id" : req.req_id,
            "req_by" : req.req_by,
            "qty" : req.qty_req,
            "remarks" : req.remarks,
            "req_at" : req.req_time,
            "material" : {
                "id": mat.id,
                "name": mat.material,
                "group": mat.g_no,
                "umo": mat.umo,
            },
        }
        for req, mat in req_query
    ]

    return {
            "status" : "200",
            "data" : request
        }

# @router.get("/requisition" ,
#             #  response_model=tSchemas.RequisitionOut,
#             status_code=status.HTTP_200_OK)
# def get_requisition_requests(emp_id: int, db: Session = Depends(get_db)):

#     # filter(models.Requisition.req_by == emp_id)

#     return {
#             "status" : "200",
#             "data" : req
#         }