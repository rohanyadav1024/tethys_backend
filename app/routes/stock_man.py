from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime


from .. import schemas, tSchemas, models
from ..database import get_db

router = APIRouter(prefix='/smanager', tags=["Stock Manager"])


@router.get("/",
            #  response_model=tSchemas.RequisitionOut,
            status_code=status.HTTP_200_OK)
def rawmaterials_inventory(db: Session = Depends(get_db)):
    invent_query = db.query(models.RawMaterialInventory).all()

    return {
        'status': "200",
        'msg': "successfully fetched inventory data",
        'data': [{
            'material_id': invent_item.m_id,
            'available_qty': invent_item.avail_qty,
            'mat_details': invent_item.materials
        } for invent_item in invent_query
        ]
    }


@router.get("/reqs",
            #  response_model=tSchemas.RequisitionOut,
            status_code=status.HTTP_200_OK)
def get_all_requisition(db: Session = Depends(get_db)):

    slot_data_query = db.query(models.Slot, models.Employees).join(
        models.Employees, models.Employees.id == models.Slot.req_by).all()

    # req_with_issue = db.query(models.Requisition).all()

    return {
        'status': "200",
        'msg': "successfully fetched requisition requests",
        'data': [{
            'slot_id': slot_data[0].slot_id,
            'req_time': slot_data[0].req_time,
            'remarks': slot_data[0].remarks,
            'issue_status': slot_data[0].issue_status,
            'issue_time': slot_data[0].issue_time,
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
                    'qty_issued': req.issue_qty,
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

    reqs_data = db.query(models.Requisition).filter(
        models.Requisition.slot_id == slot.slot_id).all()
    emp = db.query(models.Employees).filter(
        models.Employees.id == slot_data.req_by).first()

    return {
        'status': "200",
        'msg': "successfully fetched requisition",
        'data': {
            'slot_id': slot_data.slot_id,
            'req_time': slot_data.req_time,
            'remarks': slot_data.remarks,
            'issue_status': slot_data.issue_status,
            'issue_time': slot_data[0].issue_time,
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
                    'qty_issued': req.issue_qty,
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

    if not slot_query:
        return {
            'status': "400",
            'msg': "no requests for this slot",
        }
    if slot_query.issue_status:
        return {
            'status': "400",
            'msg': "this slot has been already issued",
        }

    for req in slot_query.requisition:
        inventory = db.query(models.RawMaterialInventory).filter(
            models.RawMaterialInventory.m_id == req.m_id).first()
        if inventory is None or inventory.avail_qty < req.qty_req:
            return {
                'status': "200",
                'msg': "insufficient quantity in stocks",
                'data': {
                    'qty_req': req.qty_req,
                    'avail_qty': inventory.avail_qty if inventory else 0,
                    # 'm_id': req.m_id,
                    # 'mat_details' : req.materials
                }
            }

        # stock inventory
        inventory.avail_qty -= req.qty_req
        # database requisitions
        req.issue_qty = req.qty_req

    db.commit()

    for req in slot_query.requisition:
        # production inventory
        invent_item = db.query(models.PManagerMatInventory).filter(
            models.PManagerMatInventory.m_id == req.m_id).first()
        if invent_item:
            invent_item.avail_qty += req.qty_req
        else:
            new_inv_item = models.PManagerMatInventory(
                m_id=req.m_id, avail_qty=req.qty_req)
            db.add(new_inv_item)

        req.issue_qty = req.qty_req

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


@router.delete("/reqs/deny/slot",
               #  status_code=status.HTTP_200_OK
               )
def deny_slot(slot: tSchemas.SlotData, db: Session = Depends(get_db)):

    slot_query = db.query(models.Slot).filter(
        models.Slot.slot_id == slot.slot_id).first()

    if not slot_query:
        return {
            'status': "400",
            'msg': "no requests for this slot",
        }
    if slot_query.issue_status:
        return {
            'status': "400",
            'msg': "this slot has been already issued",
        }

    db.delete(slot_query)
    db.commit()

    return {
        'status': "200",
        'msg': "requisition slot deleted successfully",
    }


@router.post("/reqs/issue/req",
             status_code=status.HTTP_200_OK)
def issue_requisitions(reqs: tSchemas.IssueReq, db: Session = Depends(get_db)):

    iscomplete = True

    for req in reqs.issue_materials:
        req_query = db.query(models.Requisition).filter(
            models.Requisition.req_id == req.id).first()

        if not req_query:
            return {
                'status': "400",
                'msg': "requisitions with id {req.req_id} not available",
            }

        inventory = db.query(models.RawMaterialInventory).filter(
            models.RawMaterialInventory.m_id == req_query.m_id).first()
        if inventory is None or inventory.avail_qty < req.qty:
            return {
                'status': "200",
                'msg': "insufficient quantity in stocks",
                'data': {
                    'qty_req': req.qty,
                    'avail_qty': inventory.avail_qty if inventory else 0,
                }
            }

        # stock inventory
        inventory.avail_qty -= req.qty

        # db updations
        if req_query.qty_req - req_query.issue_qty > req.qty:  # remaining qty more than issue qty
            iscomplete = False
        req_query.issue_qty += req.qty

        # production inventory
        invent_item = db.query(models.PManagerMatInventory).filter(
            models.PManagerMatInventory.m_id == req_query.m_id).first()
        if invent_item:
            invent_item.avail_qty += req.qty
        else:
            new_inv_item = models.PManagerMatInventory(
                m_id=req_query.m_id, avail_qty=req.qty)
            db.add(new_inv_item)

    db.commit()

    slot = req_query.slots
    slot.issued_by = reqs.issue_by
    slot.issue_time = datetime.now()

    if iscomplete:
        slot.issue_status = True

    db.commit()
    db.refresh(slot)

    req_issue_data = db.query(models.Requisition).filter(
        models.Requisition.slot_id == slot.slot_id).all()
    emp = db.query(models.Employees).filter(
        models.Employees.id == reqs.issue_by).first()
    return {
        'status': "200",
        'msg': "successfully approved requisitions",
        'data': {
            'slot_id': slot.slot_id,
            'req_time': slot.req_time,
            'remarks': slot.remarks,
            'issue_status': slot.issue_status,
            'issued_by': {
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
                    'qty_issued': req.issue_qty,
                    'mat_details': req.materials,

                } for req in req_issue_data
            ]
        }
    }


@router.get("/return/reqs",
            #  response_model=tSchemas.RequisitionOut,
            status_code=status.HTTP_200_OK)
def get_all_return_request(db: Session = Depends(get_db)):

    slot_data_query = db.query(models.ReturnSlot, models.Employees).join(
        models.Employees, models.Employees.id == models.ReturnSlot.ret_by).all()

    # slot_data_query = db.query(models.ReturnSlot, models.Employees, models.Slot).join(
    #     models.Employees, models.Employees.id == models.ReturnSlot.ret_by).join(
    #     models.Slot, models.Slot.slot_id == models.ReturnSlot.req_slot_id).all()

    return {
        'status': "200",
        'msg': "successfully fetched return requests",
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


            'materials_return': [
                {
                    'ret_id': req.ret_id,
                    'qty_req': req.requisition.qty_req,
                    'qty_issued': req.requisition.issue_qty,
                    'qty_ret': req.qty_ret,
                    'mat_details': req.materials,
                } for req in slot_data[0].mat_return
            ]
        } for slot_data in slot_data_query
        ]
    }


@router.post('/return/reqs/allow')
def approve_returns(slot: tSchemas.IssueSlot, db: Session = Depends(get_db)):

    slot_data = db.query(models.ReturnSlot).filter(
        models.ReturnSlot.slot_id == slot.slot_id).first()
    if not slot_data:
        return {
            'status': "400",
            'msg': "slot not available",
        }

    if slot_data.approved:
        return {
            'status': "400",
            'msg': "slot already approved",
        }

    for ret_mat in slot_data.mat_return:
        # buffer inventory
        invent_item = db.query(models.BufferRawMaterialInventory).filter(
            models.BufferRawMaterialInventory.m_id == ret_mat.m_id).first()
        if invent_item and invent_item.avail_qty >= ret_mat.qty_ret:
            invent_item.avail_qty -= ret_mat.qty_ret

        else:
            return {
                'status': "400",
                'msg': "insuffiecient quantity in buffer",
            }

    db.commit()

    for ret_mat in slot_data.mat_return:
        # stock inventory
        invent_item = db.query(models.RawMaterialInventory).filter(
            models.RawMaterialInventory.m_id == ret_mat.m_id).first()
        if invent_item:
            invent_item.avail_qty += ret_mat.qty_ret
        else:
            new_inv_item = models.RawMaterialInventory(
                m_id=ret_mat.m_id, avail_qty=ret_mat.qty_ret)
            db.add(new_inv_item)

    slot_data.approved = True

    db.commit()

    return {
        'status': "200",
        'msg': "material recieved",
        'data': {
            'slot_id': slot.slot_id,
            'approved': slot_data.approved
        }
    }


@router.delete('/return/reqs/deny')
def deny_returns(slot: tSchemas.IssueSlot, db: Session = Depends(get_db)):

    slot_data = db.query(models.ReturnSlot).filter(
        models.ReturnSlot.slot_id == slot.slot_id).first()
    if not slot_data:
        return {
            'status': "400",
            'msg': "slot not available",
        }

    if slot_data.approved:
        return {
            'status': "400",
            'msg': "slot already approved",
        }

    for ret_mat in slot_data.mat_return:
        # buffer inventory
        invent_item = db.query(models.BufferRawMaterialInventory).filter(
            models.BufferRawMaterialInventory.m_id == ret_mat.m_id).first()
        if invent_item and invent_item.avail_qty >= ret_mat.qty_ret:
            invent_item.avail_qty -= ret_mat.qty_ret

        else:
            return {
                'status': "400",
                'msg': "insuffiecient quantity in buffer",
            }

    db.commit()

    for ret_mat in slot_data.mat_return:
        # stock inventory
        invent_item = db.query(models.PManagerMatInventory).filter(
            models.PManagerMatInventory.m_id == ret_mat.m_id).first()
        if invent_item:
            invent_item.avail_qty += ret_mat.qty_ret
        else:
            new_inv_item = models.PManagerMatInventory(
                m_id=ret_mat.m_id, avail_qty=ret_mat.qty_ret)
            db.add(new_inv_item)

    db.delete(slot_data)
    db.commit()

    return {
        'status': "200",
        'msg': "material denied",
        'data': {
            'slot_id': slot.slot_id,
        }
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

    reqs_data = db.query(models.MaterialReturn).filter(
        models.MaterialReturn.slot_id == slot.slot_id).all()
    emp = db.query(models.Employees).filter(
        models.Employees.id == slot_data.ret_by).first()

    return {
        'status': "200",
        'msg': "successfully fetched return requisition",
        'data': {
            'slot_id': slot_data.slot_id,
            'req_slot_id': slot_data.req_slot_id,
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
                    'qty_req': req.requisition.qty_req,
                    'qty_issued': req.requisition.issue_qty,
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


router2 = APIRouter(prefix='/smanager', tags=["Stock Manager (Products)"])


@router2.get("/handovers",
             #  response_model=tSchemas.RequisitionOut,
             status_code=status.HTTP_200_OK)
def get_all_handover_request(db: Session = Depends(get_db)):

    batch_data_query = db.query(models.Batches, models.Employees).join(
        models.Employees, models.Employees.id == models.Batches.handover_by).all()

    return {
        'status': "200",
        'msg': "successfully fetched handover requests",
        'data': [{
            'batch_id': batch_data[0].batch_id,
            'mfg': batch_data[0].mfg,
            'remarks': batch_data[0].remarks,
            'is_recieved': batch_data[0].is_recieved,
            'recieved_time': batch_data[0].recieved_time,
            'recieved_by': batch_data[0].recieved_by,

            'handover_by': {
                "id": batch_data[1].id,
                "name": batch_data[1].name,
                "email": batch_data[1].email,
                "role": batch_data[1].role,
                "phone": batch_data[1].phone,
                "created_at": batch_data[1].created_at,
                "is_active": batch_data[1].is_active,
            },

            'handovers': [
                {
                    'handover_id': handover.handover_id,
                    'product': handover.products,
                    'qty_req': handover.qty,
                } for handover in batch_data[0].prod_handover
            ]
        } for batch_data in batch_data_query
        ]
    }


@router2.post("/handovers/recieve/batch",
              #  status_code=status.HTTP_200_OK
              )
def accept_handover(batch: tSchemas.AcceptBatch, db: Session = Depends(get_db)):

    batch_data = db.query(models.Batches).filter(
        models.Batches.batch_id == batch.batch_id).first()

    if not batch_data:
        return {
            'status': "400",
            'msg': "no requests for this batch",
        }
    if batch_data.is_recieved:
        return {
            'status': "400",
            'msg': "this batch has been already accepted",
        }

    batch_data.is_recieved = True
    batch_data.recieved_by = batch.recieved_by
    batch_data.recieved_time = datetime.now()

    db.commit()
    db.refresh(batch_data)

    emp = db.query(models.Employees).filter(
        models.Employees.id == batch.recieved_by).first()

    return {
        'status': "200",
        'msg': "batch recieved successfully",
        'data': {
            'batch_id': batch_data.batch_id,
            'mfg': batch_data.mfg,
            'remarks': batch_data.remarks,
            'is_recieved': batch_data.is_recieved,
            'recieved_time': batch_data.recieved_time,
            # 'recieved_by': batch_data.recieved_by,

            'recieved_by': {
                "id": emp.id,
                "name": emp.name,
                "email": emp.email,
                "role": emp.role,
                "phone": emp.phone,
                "created_at": emp.created_at,
                "is_active": emp.is_active,
            },

            'handovers': [
                {
                    'handover_id': handover.handover_id,
                    'product': handover.products,
                    'qty_req': handover.qty,
                } for handover in batch_data.prod_handover
            ]
        }
    }


@router2.delete("/handovers/deny/batch",
                #  status_code=status.HTTP_200_OK
                )
def deny_handover(batch: tSchemas.BatchData, db: Session = Depends(get_db)):

    batch_query = db.query(models.Batches).filter(
        models.Batches.batch_id == batch.batch_id).first()

    if not batch_query:
        return {
            'status': "400",
            'msg': "no requests for this batch",
        }
    if batch_query.is_recieved:
        return {
            'status': "400",
            'msg': "this batch has been already accepted",
        }

    db.delete(batch_query)
    db.commit()

    return {
        'status': "200",
        'msg': "handover batch deleted successfully",
    }


# post consignments for gate keeper
@router2.post("/consignments/create",
              #  response_model=tSchemas.RequisitionOut,
              status_code=status.HTTP_200_OK)
def create_consignments(disp: tSchemas.Dispatches, db: Session = Depends(get_db)):
    emp_query = db.query(models.Employees).filter(
        models.Employees.id == disp.dis_by).first()

    if not emp_query:
        return {
            'status': "400",
            'msg': 'employee cannot dispatch'
        }

    # dispatch = puchs.model_dump(exclude={"orders"})
    new_dispatch = models.Dispatches(
        buyer=disp.buyer,
        invoice=disp.invoice,
        inv_value=disp.invoice_value,
        dis_by=disp.dis_by,
    )
    db.add(new_dispatch)
    db.commit()
    db.refresh(new_dispatch)

    for item in disp.consigns:
        new_consign = models.Consignments(
            prod_id=item.prod_id, qty=item.qty, dis_id=new_dispatch.dis_id)

        db.add(new_consign)
    db.commit()

    driver_query = db.query(models.Drivers).filter(
        models.Drivers.phone == disp.driv_phone).first()
    if not driver_query:
        driver_query = models.Drivers(
            name=disp.driv_name,
            phone=disp.driv_phone,
            license_no=disp.driv_license)
        db.add(driver_query)
        db.commit()
        db.refresh(driver_query)

    vehicle_number = disp.veh_no.strip().replace(" ", "").upper()

    trans_query = db.query(models.Transports).filter(
        models.Transports.veh_no == vehicle_number).first()
    if not trans_query:
        trans_query = models.Transports(
            veh_no=vehicle_number,
            name=disp.transport_name,)
        db.add(trans_query)
        db.commit()
        db.refresh(trans_query)

    new_dispatch.driv_id = driver_query.drv_id
    new_dispatch.trans_id = trans_query.tran_id
    db.commit()

    dis_data = db.query(models.Dispatches, models.Employees).filter(models.Dispatches.dis_id == new_dispatch.dis_id).join(
        models.Employees, models.Employees.id == models.Dispatches.dis_by).first()

    return {
        'status': "200",
        'msg': "successfully posted material orders",
        'data': {
            'dis_id': dis_data[0].dis_id,
            'buyer': dis_data[0].buyer,
            'invoice': dis_data[0].invoice,
            'inv_value': dis_data[0].inv_value,
            'recv_time': dis_data[0].recv_time,
            'checkout': dis_data[0].checkout,

            'dis_by': {
                "id": dis_data[1].id,
                "name": dis_data[1].name,
                "email": dis_data[1].email,
                "role": dis_data[1].role,
                "phone": dis_data[1].phone,
                "created_at": dis_data[1].created_at,
                "is_active": dis_data[1].is_active,
            },

            'driver_detials': dis_data[0].drivers,
            'vehicle': dis_data[0].transports,

            'consignments': [
                {
                    'consignment_id': consign.cg_id,
                    'qty': consign.qty,
                    'product': consign.products,
                    'checked_qty': consign.checked_qty,
                } for consign in dis_data[0].consignments
            ]
        }
    }
