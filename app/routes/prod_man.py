from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List

from .. import schemas, tSchemas, models, utils, oauth2, config
from ..database import get_db

router = APIRouter(prefix='/pmanager', tags=["ProductionManager"])



@router.post("/create",
             #  response_model=tSchemas.RequisitionOut,
             status_code=status.HTTP_200_OK)
def material_requisition(reqs: tSchemas.RequisitionIn, db: Session = Depends(get_db)):
    emp_query = db.query(models.Employees).filter(
        models.Employees.id == reqs.req_by).first()

    if not emp_query:
        return {
            'status': "400",
            'msg': 'employee cannot send request'
        }

    new_slot = models.Slot(remarks=reqs.remarks, req_by=reqs.req_by)
    db.add(new_slot)
    db.commit()
    db.refresh(new_slot)

    for item in reqs.items:
        new_req = models.Requisition(m_id=item.id, qty_req=item.qty, slot_id=new_slot.slot_id)

        db.add(new_req)
        db.commit()
        db.refresh(new_req)

    slot_data = db.query(models.Slot, models.Employees).filter(models.Slot.slot_id == new_slot.slot_id).join(
        models.Employees, models.Employees.id == models.Slot.req_by).first()

    return {
        'status': "200",
        'msg' : "successfully posted requisition requests",
        'data': {
            'slot_id': slot_data[0].slot_id,
            'req_time': slot_data[0].req_time,
            'remarks': slot_data[0].remarks,
            'issue_status' : slot_data[0].issue_status,
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
                    'mat_details': req.materials,
                } for req in slot_data[0].requisition
            ]
        }
    }
