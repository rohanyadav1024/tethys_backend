from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import schemas,tSchemas, models
from ..database import get_db

router = APIRouter(prefix='/smanager', tags=["Stock Manager"])

@router.get("/reqs" ,
            #  response_model=tSchemas.RequisitionOut,
            status_code=status.HTTP_200_OK)
def get_requisition_requests(db: Session = Depends(get_db)):

    slot_data_query = db.query(models.Slot, models.Employees).join(
        models.Employees, models.Employees.id == models.Slot.req_by).all()

    return {
        'status': "200",
        'msg' : "successfully posted requisition requests",
        'data': [{
            'slot_id': slot_data[0].slot_id,
            'req_time': slot_data[0].req_time,
            'remarks': slot_data[0].remarks,
            'req_by': {
                "id": slot_data[1].id,
                "name": slot_data[1].name,
                "email": slot_data[1].email,
                "role": slot_data[1].role,
                "phone": slot_data[1].phone,
                "created_at": slot_data[1].created_at,
                "is_active": slot_data[1].is_active,
            },
                                 
            
            'requisitions': [
                {
                    'req_id' : req.req_id,
                    'qty_req' : req.qty_req,
                    'issue_qty' : req.issue_qty,
                    'issue_by' : req.issued_by,
                    'mat_details': req.materials,
                } for req in slot_data[0].requisition
            ]
        } for slot_data in slot_data_query
        ]
    }



@router.post('/reqs/slot')
def single_slot_requisitions(slot : tSchemas.SlotData, db: Session = Depends(get_db)):
    
    reqs_data = db.query(models.Requisition, models.Employees).filter(models.Requisition.slot_id == slot.slot_id).join(
        models.Employees, models.Employees.id == models.Requisition.issued_by).all()
    
    if not reqs_data:
        return{
            'status': "400",
            'msg' : "slot not available",
        }
    
    slot_data = reqs_data[0][0].slots

    return {
        'status': "200",
        'msg' : "successfully fetched requisition",
        'data': {
            'slot_id': slot_data.slot_id,
            'req_time': slot_data.req_time,
            'remarks': slot_data.remarks,
            'issue_status' : slot_data.issue_status,
            
            'requisitions': [
                {
                    'req_id' : req.req_id,
                    'qty_req' : req.qty_req,
                    'qty_issued' : req.issue_qty,
                    'mat_details': req.materials,
                    'issued_by': {
                        "id": emp.id,
                        "name": emp.name,
                        "email": emp.email,
                        "role": emp.role,
                        "phone": emp.phone,
                        "created_at": emp.created_at,
                        "is_active": emp.is_active,
            },
                } for req, emp in reqs_data
            ]
        }
    }
    

@router.post("/reqs/issue/slot" ,
            status_code=status.HTTP_200_OK)
def issue_slot(slot : tSchemas.IssueSlot, db: Session = Depends(get_db)):

    slot_query = db.query(models.Slot).filter(models.Slot.slot_id == slot.slot_id).first()

    if not slot_query:
        return{
            'status': "400",
            'msg' : "no requests for this slot",
        }
    
    slot_query.issue_status = 2
    db.commit()
    db.refresh(slot_query)

    return {
        'status': "200",
        'msg' : "successfully approved requisition",
        'data' : slot_query
    }
    
@router.post("/reqs/issue/req" ,
            status_code=status.HTTP_200_OK)
def issue_requisitions(reqs : tSchemas.IssueReq, db: Session = Depends(get_db)):

    iscomplete = True

    for req in reqs.issue_materials:
        req_query = db.query(models.Requisition).filter(models.Requisition.req_id == req.id).first()

        if not req_query:
            return{
                'status': "400",
                'msg' : "requisitions with id {req.req_id} not available",
            }
        
        req_query.issue_qty = req.qty
        if req_query.slots.issue_status < 1:
            req_query.slots.issue_status = 1

        req_query.issued_by = reqs.issue_by
        db.commit()
        db.refresh(req_query)

        if req_query.qty_req != req.qty:
            iscomplete = False


    slot = req_query.slots

    if iscomplete:
        slot.issue_status = 2

    db.commit()
    db.refresh(slot)

    req_issue_data = db.query(models.Requisition, models.Employees).filter(models.Requisition.slot_id == slot.slot_id).join(
        models.Employees, models.Employees.id == models.Requisition.issued_by).all()

    return {
        'status': "200",
        'msg' : "successfully approved requisitions",
        'data': {
            'slot_id': slot.slot_id,
            'req_time': slot.req_time,
            'remarks': slot.remarks,
            'issue_status' : slot.issue_status,
            
            'requisitions': [
                {
                    'req_id' : req.req_id,
                    'qty_req' : req.qty_req,
                    'qty_issued' : req.issue_qty,
                    'mat_details': req.materials,
                    'issued_by': {
                        "id": emp.id,
                        "name": emp.name,
                        "email": emp.email,
                        "role": emp.role,
                        "phone": emp.phone,
                        "created_at": emp.created_at,
                        "is_active": emp.is_active,
            },
                } for req, emp in req_issue_data
            ]
        }
    }

