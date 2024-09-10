from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy import and_, desc
from sqlalchemy.orm import Session, joinedload, aliased
from typing import List

from .. import schemas, tSchemas, models, utils, oauth2, config
from ..database import get_db

router = APIRouter(prefix='/history',
                   tags=["Histories"])


@router.post("/reqs",
             status_code=status.HTTP_200_OK)
def get_all_history_requisition(request: tSchemas.GetHistoryReq, db: Session = Depends(get_db)):

    # Base query with join for owner and stock manager
    EmployeesAlias = aliased(models.Employees)

    query = db.query(
        models.HistoryReqSlot,
        models.Employees,
        EmployeesAlias  # Use the alias here
    ).join(
        models.Employees,
        models.Employees.id == models.HistoryReqSlot.req_by
    ).join(
        EmployeesAlias,  # And here for the second join
        models.HistoryReqSlot.issued_by == EmployeesAlias.id
    )

    emp_query = db.query(models.Employees).filter(
        models.Employees.id == request.emp_id).first()
    if not emp_query:
        return {
            'status': "400",
            'msg': "employee not found"
        }

    if emp_query.role == 2:
        query = query.filter(models.HistoryReqSlot.req_by == request.emp_id)

    # If both start_date and end_date are provided
    if request.start_date and request.end_date:
        query = query.filter(
            and_(
                models.HistoryReqSlot.comp_time >= request.start_date,
                models.HistoryReqSlot.comp_time <= request.end_date
            )
        )
        # Optionally apply ordering here if needed for this case

    # If start_date and end_date are not provided, apply default ordering
    else:
        query = query.order_by(desc(models.HistoryReqSlot.comp_time))

    # Finally, apply limit and offset
    query = query.limit(request.limit).offset(request.offset * request.limit)
    slot_data_query = query.all()

    return {
        'status': "200",
        'msg': "successfully fetched requisition requests",
        'data': [{
            'slot_id': slot_data[0].slot_id,
            'req_time': slot_data[0].req_time,
            'remarks': slot_data[0].remarks,
            'issue_status': slot_data[0].issue_status,
            'issue_time': slot_data[0].issue_time,
            'comp_time': slot_data[0].comp_time,
            'req_by': {
                "id": slot_data[1].id,
                "name": slot_data[1].name,
                "email": slot_data[1].email,
                "role": slot_data[1].role,
                "phone": slot_data[1].phone,
                "created_at": slot_data[1].created_at,
                "is_active": slot_data[1].is_active,
            },

            'issued_by': {
                "id": slot_data[2].id,
                "name": slot_data[2].name,
                "email": slot_data[2].email,
                "role": slot_data[2].role,
                "phone": slot_data[2].phone,
                "created_at": slot_data[2].created_at,
                "is_active": slot_data[2].is_active,
            },

            'requisitions': [
                {
                    'req_id': req.req_id,
                    'qty_req': req.qty_req,
                    'qty_issued': req.issue_qty,
                    'qty_consumed': req.consum_qty,
                    'mat_details': req.materials,
                } for req in slot_data[0].history_requisition
            ]
        } for slot_data in slot_data_query
        ]
    }

@router.post("/returns", status_code=status.HTTP_200_OK)
def get_all_history_return(request: tSchemas.GetHistoryReq, db: Session = Depends(get_db)):

    # Base query with join for owner and stock manager
    query = db.query(
        models.HistoryReturnSlot,
        models.Employees,
    ).join(
        models.Employees,
        models.Employees.id == models.HistoryReturnSlot.ret_by
    ).distinct(models.HistoryReturnSlot.slot_id)

    emp_query = db.query(models.Employees).filter(
        models.Employees.id == request.emp_id).first()
    if not emp_query:
        return {
            'status': "400",
            'msg': "employee not found"
        }

    if emp_query.role == 2:
        query = query.filter(models.HistoryReturnSlot.ret_by == request.emp_id)

    # If both start_date and end_date are provided
    if request.start_date and request.end_date:
        query = query.filter(
            and_(
                models.HistoryReturnSlot.ret_time >= request.start_date,
                models.HistoryReturnSlot.ret_time <= request.end_date
            )
        )

    # Modify order by to ensure DISTINCT ON works correctly
    query = query.order_by(models.HistoryReturnSlot.slot_id, desc(models.HistoryReturnSlot.ret_time))

    # Finally, apply limit and offset
    query = query.limit(request.limit).offset(request.offset * request.limit)
    slot_data_query = query.all()

    return {
        'status': "200",
        'msg': "successfully fetched requisition requests",
        'data': [{
            'ret_slot_id': slot_data[0].slot_id,
            'req_slot_id': slot_data[0].req_slot_id,
            'ret_time': slot_data[0].ret_time,
            'remarks': slot_data[0].remarks,
            'approved': slot_data[0].approved,
            'ret_by': {
                "id": slot_data[1].id,
                "name": slot_data[1].name,
                "email": slot_data[1].email,
                "role": slot_data[1].role,
                "phone": slot_data[1].phone,
                "created_at": slot_data[1].created_at,
                "is_active": slot_data[1].is_active,
            },

            'returns': [
                {
                    'ret_id': req.ret_id,
                    'qty_req': req.history_requisition.qty_req,
                    'qty_issued': req.history_requisition.issue_qty,
                    'qty_consumed': req.history_requisition.consum_qty,
                    'qty_ret': req.qty_ret,
                    'mat_details': req.materials,
                } for req in slot_data[0].history_mat_return
            ]
        } for slot_data in slot_data_query
        ]
    }