from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime


from .. import schemas, tSchemas, models
from ..database import get_db

router = APIRouter(prefix='/smanager', tags=["Stock Manager"])


@router.get("/reqs",
            #  response_model=tSchemas.RequisitionOut,
            status_code=status.HTTP_200_OK)
def get_all_requisition(db: Session = Depends(get_db)):

    slot_data_query = db.query(models.Slot, models.Employees).join(
        models.Employees, models.Employees.id == models.Slot.req_by).all()

    return {
        'status': "200",
        'msg': "successfully fetched requisition requests",
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
                    'req_id': req.req_id,
                    'qty_req': req.qty_req,
                    'mat_details': req.materials,
                } for req in slot_data[0].requisition
            ]
        } for slot_data in slot_data_query
        ]
    }


# to get requisition by slot id: prod manager will see a slot data
@router.post('/reqs/slot')
def get_requisitions_by_slot(slot: tSchemas.SlotData, db: Session = Depends(get_db)):

    slot_data = db.query(models.Slot).filter(
        models.Slot.slot_id == slot.slot_id).first()
    if not slot_data:
        return {
            'status': "400",
            'msg': "slot not available",
        }

    reqs_data = db.query(models.Requisition).filter(models.Requisition.slot_id == slot.slot_id).all()
    emp = db.query(models.Employees).filter(models.Employees.id == slot_data.req_by).first()

    return {
        'status': "200",
        'msg': "successfully fetched requisition",
        'data': {
            'slot_id': slot_data.slot_id,
            'req_time': slot_data.req_time,
            'remarks': slot_data.remarks,
            'issue_status': slot_data.issue_status,

            'req_by': {
                "id": emp.id,
                "name": emp.name,
                "email": emp.email,
                "role": emp.role,
                "phone": emp.phone,
                "created_at": emp.created_at,
                "is_active": emp.is_active,
            },

            'requisitions': [
                {
                    'req_id': req.req_id,
                    'qty_req': req.qty_req,
                    'mat_details': req.materials,
                } for req in reqs_data
            ]
        }
    }


@router.post("/reqs/issue/slot",
            #  status_code=status.HTTP_200_OK
            )
def issue_slot(slot: tSchemas.IssueSlot, db: Session = Depends(get_db)):

    slot_query = db.query(models.Slot).filter(
        models.Slot.slot_id == slot.slot_id).first()

    if not slot_query :
        return {
            'status': "400",
            'msg': "no requests for this slot",
        }
    if slot_query.issue_status :
        return {
            'status': "400",
            'msg': "this slot has been already issued",
        }

    slot_query.issue_status = True
    slot_query.issued_by = slot.issue_by
    slot_query.issue_time = datetime.now()
    
    db.commit()
    db.refresh(slot_query)

    return {
        'status': "200",
        'msg': "successfully approved requisition",
        'data': slot_query
    }


# @router.post("/reqs/issue/req",
#              status_code=status.HTTP_200_OK)
# def issue_requisitions(reqs: tSchemas.IssueReq, db: Session = Depends(get_db)):

#     iscomplete = True

#     for req in reqs.issue_materials:
#         req_query = db.query(models.Requisition).filter(
#             models.Requisition.req_id == req.id).first()

#         if not req_query:
#             return {
#                 'status': "400",
#                 'msg': "requisitions with id {req.req_id} not available",
#             }

#         req_query.issue_qty = req.qty
#         if req_query.slots.issue_status < 1:
#             req_query.slots.issue_status = 1

#         req_query.issued_by = reqs.issue_by
#         db.commit()
#         db.refresh(req_query)

#         if req_query.qty_req != req.qty:
#             iscomplete = False

#     slot = req_query.slots

#     if iscomplete:
#         slot.issue_status = 2

#     db.commit()
#     db.refresh(slot)

#     req_issue_data = db.query(models.Requisition, models.Employees).filter(models.Requisition.slot_id == slot.slot_id).join(
#         models.Employees, models.Employees.id == models.Requisition.issued_by).all()

#     return {
#         'status': "200",
#         'msg': "successfully approved requisitions",
#         'data': {
#             'slot_id': slot.slot_id,
#             'req_time': slot.req_time,
#             'remarks': slot.remarks,
#             'issue_status': slot.issue_status,

#             'requisitions': [
#                 {
#                     'req_id': req.req_id,
#                     'qty_req': req.qty_req,
#                     'qty_issued': req.issue_qty,
#                     'mat_details': req.materials,
#                     'issued_by': {
#                         "id": emp.id,
#                         "name": emp.name,
#                         "email": emp.email,
#                         "role": emp.role,
#                         "phone": emp.phone,
#                         "created_at": emp.created_at,
#                         "is_active": emp.is_active,
#                     },
#                 } for req, emp in req_issue_data
#             ]
#         }
#     }

@router.get("/return/reqs",
            #  response_model=tSchemas.RequisitionOut,
            status_code=status.HTTP_200_OK)
def get_all_return_request(db: Session = Depends(get_db)):

    slot_data_query = db.query(models.ReturnSlot, models.Employees).join(
        models.Employees, models.Employees.id == models.ReturnSlot.ret_by).all()

    return {
        'status': "200",
        'msg': "successfully fetched return requests",
        'data': [{
            'slot_id': slot_data[0].slot_id,
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


            'materials_return': [
                {
                    'ret_id': req.ret_id,
                    'qty_ret': req.qty_ret,
                    'mat_details': req.materials,
                } for req in slot_data[0].mat_return
            ]
        } for slot_data in slot_data_query
        ]
    }


@router.post('/return/reqs/slot')
def get_return_request_bySlot(slot: tSchemas.SlotData, db: Session = Depends(get_db)):

    slot_data = db.query(models.ReturnSlot).filter(
        models.ReturnSlot.slot_id == slot.slot_id).first()
    if not slot_data:
        return {
            'status': "400",
            'msg': "slot not available",
        }

    reqs_data = db.query(models.MaterialReturn).filter(models.MaterialReturn.slot_id == slot.slot_id).all()
    emp = db.query(models.Employees).filter(models.Employees.id == slot_data.ret_by).first()

    return {
        'status': "200",
        'msg': "successfully fetched requisition",
        'data': {
            'slot_id': slot_data.slot_id,
            'ret_time': slot_data.ret_time,
            'remarks': slot_data.remarks,
            'approved': slot_data.approved,

            'ret_by': {
                "id": emp.id,
                "name": emp.name,
                "email": emp.email,
                "role": emp.role,
                "phone": emp.phone,
                "created_at": emp.created_at,
                "is_active": emp.is_active,
            },

            'requisitions': [
                {
                    'ret_id': req.ret_id,
                    'qty_ret': req.qty_ret,
                    'mat_details': req.materials,
                } for req in reqs_data
            ]
        }
    }




# post orders for gate keeper
@router.post("/orders/create",
             #  response_model=tSchemas.RequisitionOut,
             status_code=status.HTTP_200_OK)
def create_purchase_orders(puchs: tSchemas.Purchases, db: Session = Depends(get_db)):
    emp_query = db.query(models.Employees).filter(
        models.Employees.id == puchs.pur_by).first()

    if not emp_query:
        return {
            'status': "400",
            'msg': 'employee cannot purchase'
        }

    purchase = puchs.model_dump(exclude={"orders"})
    new_purchase = models.Purchases(**purchase)
    db.add(new_purchase)
    db.commit()
    db.refresh(new_purchase)


    for item in puchs.orders:
        new_order = models.Orders(
            m_id=item.m_id, ord_qty=item.ord_qty, pur_id=new_purchase.pur_id)

        db.add(new_order)
        db.commit()
        db.refresh(new_order)

    slot_data = db.query(models.Purchases, models.Employees).filter(models.Purchases.pur_id == new_purchase.pur_id).join(
        models.Employees, models.Employees.id == models.Purchases.pur_by).first()
    
    return {
        'status': "200",
        'msg': "successfully posted material orders",
        'data': {
            'pur_id': slot_data[0].pur_id,
            'pur_time': slot_data[0].pur_time,
            'remarks': slot_data[0].remarks,
            'recieved': slot_data[0].recieved,
            'invoice': slot_data[0].invoice,
            'vehicle': slot_data[0].vehicle,
            'exp_date': slot_data[0].exp_date,

            'pur_by': {
                "id": slot_data[1].id,
                "name": slot_data[1].name,
                "email": slot_data[1].email,
                "role": slot_data[1].role,
                "phone": slot_data[1].phone,
                "created_at": slot_data[1].created_at,
                "is_active": slot_data[1].is_active,
            },

            'orders': [
                {
                    'order_id': ord.ord_id,
                    'qty_req': ord.ord_qty,
                    'mat_details': ord.materials,
                } for ord in slot_data[0].orders
            ]
        }
    }

