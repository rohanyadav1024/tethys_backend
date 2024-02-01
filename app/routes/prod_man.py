from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List

from .. import schemas, tSchemas, models, utils, oauth2, config
from ..database import get_db

router = APIRouter(prefix='/pmanager',
                   tags=["ProductionManager (RawMaterial)"])


@router.get("/",
            #  response_model=tSchemas.RequisitionOut,
            status_code=status.HTTP_200_OK)
def production_manager_rawmaterials_inventory(db: Session = Depends(get_db)):
    invent_query = db.query(models.PManagerMatInventory).all()

    return {
        'status': "200",
        'msg': "successfully fetched production inventory data",
        'data': [{
            'material_id': invent_item.m_id,
            'available_qty': invent_item.avail_qty,
            'mat_details': invent_item.materials
        } for invent_item in invent_query
        ]
    }

# to see requisition data req_by prod manager


@router.post("/id",
             status_code=status.HTTP_200_OK)
def get_requisition_data_by_empID(emp: tSchemas.EmpID, db: Session = Depends(get_db)):

    emp_query = db.query(models.Employees).filter(
        models.Employees.id == emp.emp_id).first()

    if not emp_query:
        return {
            'status': "400",
            'msg': 'employee does not exist'
        }

    slot_data_query = db.query(models.Slot, models.Employees).filter(
        models.Slot.req_by == emp.emp_id).join(
        models.Employees, models.Employees.id == models.Slot.issued_by, isouter=True).all()

    if not slot_data_query:
        return {
            'status': "400",
            'msg': 'employee has not requested anything'
        }

    return {
        'status': "200",
        'msg': "successfully fetched requisition requests",
        'data': [
            {
                'slot_id': slot_data[0].slot_id,
                'req_time': slot_data[0].req_time,
                'remarks': slot_data[0].remarks,
                'issue_status': slot_data[0].issue_status,
                'issue_time': slot_data[0].issue_time,
                'issue_by': {
                    "id": slot_data[1].id,
                    "name": slot_data[1].name,
                    "email": slot_data[1].email,
                    "role": slot_data[1].role,
                    "phone": slot_data[1].phone,
                    "created_at": slot_data[1].created_at,
                    "is_active": slot_data[1].is_active,
                } if slot_data[0].issued_by is not None else None,

                'requisitions': [
                    {
                        'req_id': req.req_id,
                        'qty_req': req.qty_req,
                        'qty_issued': req.issue_qty,
                        'qty_consumed': req.consum_qty,

                        'mat_details': req.materials,
                    } for req in slot_data[0].requisition
                ]
            } for slot_data in slot_data_query
        ]
    }


@router.post("/create",
             #  response_model=tSchemas.RequisitionOut,
             status_code=status.HTTP_200_OK)
def create_requisition(reqs: tSchemas.RequisitionIn, db: Session = Depends(get_db)):
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
        new_req = models.Requisition(
            m_id=item.id, qty_req=item.qty, slot_id=new_slot.slot_id)

        db.add(new_req)
        db.commit()
        db.refresh(new_req)

    slot_data = db.query(models.Slot, models.Employees).filter(models.Slot.slot_id == new_slot.slot_id).join(
        models.Employees, models.Employees.id == models.Slot.req_by).first()

    return {
        'status': "200",
        'msg': "successfully posted requisition requests",
        'data': {
            'slot_id': slot_data[0].slot_id,
            'req_time': slot_data[0].req_time,
            'remarks': slot_data[0].remarks,
            'issue_status': slot_data[0].issue_status,
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
                    'qty_consumed': req.consum_qty,

                    'mat_details': req.materials,
                } for req in slot_data[0].requisition
            ]
        }
    }


# return materials
@router.post("/return/id",
             status_code=status.HTTP_200_OK)
def get_return_material_by_empID(emp: tSchemas.EmpID, db: Session = Depends(get_db)):

    emp_query = db.query(models.Employees).filter(
        models.Employees.id == emp.emp_id).first()

    if not emp_query:
        return {
            'status': "400",
            'msg': 'employee does not exist'
        }

    slot_data_query = db.query(models.ReturnSlot).filter(
        models.Slot.req_by == emp.emp_id).all()

    if not slot_data_query:
        return {
            'status': "400",
            'msg': 'employee has not return anything'
        }

    return {
        'status': "200",
        'msg': "successfully fetched return requests",
        'data': [
            {
                'slot_id': slot_data.slot_id,
                'req_slot_id': slot_data.req_slot_id,
                'ret_time': slot_data.ret_time,
                'remarks': slot_data.remarks,
                'approved': slot_data.approved,

                'materials_return': [
                    {
                        'ret_id': req.ret_id,
                        'qty_req': req.history_requisition.qty_req,
                        'qty_issued': req.history_requisition.issue_qty,
                        'qty_consumed': req.history_requisition.consum_qty,
                        'qty_ret': req.qty_ret,
                        'mat_details': req.materials,
                    } for req in slot_data.mat_return
                ]
            } for slot_data in slot_data_query
        ]
    }


@router.post("/return/create",
             #  response_model=tSchemas.RequisitionOut,
             status_code=status.HTTP_200_OK)
def create_return_request(reqs: tSchemas.ReturnIn, db: Session = Depends(get_db)):
    emp_query = db.query(models.Employees).filter(
        models.Employees.id == reqs.req_by).first()
    if not emp_query:
        return {
            'status': "400",
            'msg': 'employee cannot send return request'
        }

    old_req_slot_data = db.query(models.Slot).filter(
        models.Slot.slot_id == reqs.req_slot_id).first()
    if not old_req_slot_data:
        return {
            'status': "400",
            'msg': 'requisition slot not available'
        }

    # checking for integrity constraints
    for item in reqs.items:
        req_query = db.query(models.Requisition).filter(
            models.Requisition.req_id == item.req_id).first()

        # updating production inventory
        invent_item = db.query(models.PManagerMatInventory).filter(
            models.PManagerMatInventory.m_id == item.mat_id).first()

        if invent_item and invent_item.avail_qty >= req_query.issue_qty - req_query.consum_qty:
            # consumption will be reduced by mat remain for consumption
            invent_item.avail_qty -= (req_query.issue_qty -
                                      req_query.consum_qty)
            req_query.consum_qty = (req_query.issue_qty - item.qty)

        else:
            return {
                'status': "400",
                'msg': 'insufficient quantity'
            }
        

    # Step 1: create history requisition slot
    new_hist_req_slot = models.HistoryReqSlot(
        issued_by=old_req_slot_data.issued_by,
        req_by=old_req_slot_data.req_by,
        req_time=old_req_slot_data.req_time,
        issue_time=old_req_slot_data.issue_time,
        issue_status=old_req_slot_data.issue_status,
        remarks=old_req_slot_data.remarks)

    db.add(new_hist_req_slot)
    db.commit()
    db.refresh(new_hist_req_slot)

    # Step2: create history requisition
    for req in old_req_slot_data.requisition:
        # perform op to move from req to history_req
        new_hist_req = models.HistoryRequisition(
            m_id=req.m_id,
            qty_req=req.qty_req,
            issue_qty=req.issue_qty,
            consum_qty=req.consum_qty,
            slot_id=new_hist_req_slot.slot_id,
        )
        # remove the requisition list and add it to History Requisitions
        db.add(new_hist_req)
        # db.delete(req)
        db.commit()

    # Step 3: create history return slot
    # creating Return slot
    new_slot = models.ReturnSlot(
        remarks=reqs.remarks,req_slot_id = new_hist_req_slot.slot_id, ret_by=reqs.req_by)
    db.add(new_slot)
    db.commit()
    db.refresh(new_slot)

    # Step 4: create history mat return requisition
#    creating mat return requisition
    for item in reqs.items:
        # updating buffer inventory
        invent_item = db.query(models.BufferRawMaterialInventory).filter(
            models.BufferRawMaterialInventory.m_id == item.mat_id).first()
        if invent_item:
            invent_item.avail_qty += item.qty
        else:
            new_inv_item = models.BufferRawMaterialInventory(
                m_id=item.mat_id, avail_qty=item.qty)
            db.add(new_inv_item)

        # creating return requestion for each material
        hist_req_query = db.query(models.HistoryRequisition).filter(models.HistoryRequisition.slot_id == new_hist_req_slot.slot_id and models.HistoryRequisition.m_id == item.mat_id).first()
        new_return_req = models.MaterialReturn(
            m_id=item.mat_id, old_req_id=item.req_id, req_id=hist_req_query.req_id, qty_ret=item.qty, slot_id=new_slot.slot_id)
        # new_return_req = models.MaterialReturn(
        #     m_id=item.mat_id, req_id=item.req_id, qty_ret=item.qty, slot_id=new_slot.slot_id)

        db.add(new_return_req)
    db.commit()

    

    db.delete(old_req_slot_data)  # delete old data
    db.commit()

    slot_data = db.query(models.ReturnSlot, models.Employees).filter(models.ReturnSlot.slot_id == new_slot.slot_id).join(
        models.Employees, models.Employees.id == models.ReturnSlot.ret_by).first()

    return {
        'status': "200",
        'msg': "successfully posted return request",
        'data': {
            'slot_id': slot_data[0].slot_id,
            'req_slot_id': slot_data[0].req_slot_id,
            'ret_time': slot_data[0].ret_time,
            'remarks': slot_data[0].remarks,
            'recieved': slot_data[0].approved,
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
                    'qty_req': req.history_requisition.qty_req,
                    'qty_issued': req.history_requisition.issue_qty,
                    'qty_consumed': req.history_requisition.consum_qty,

                    'qty_ret': req.qty_ret,
                    'mat_details': req.materials,
                } for req in slot_data[0].mat_return
            ]
        }
    }


@router.post("/update",
             #  response_model=tSchemas.RequisitionOut,
             status_code=status.HTTP_200_OK)
def update_used_material(consump: tSchemas.UpdateMatIn, db: Session = Depends(get_db)):

    emp_query = db.query(models.Employees).filter(
        models.Employees.id == consump.upd_by).first()

    if not emp_query:
        return {
            'status': "400",
            'msg': 'employee cannot consume'
        }

    for item in consump.items:
        # update db entry of requisitions
        req = db.query(models.Requisition).filter(
            models.Requisition.req_id == item.req_id).first()
        if not req:
            return {
                'status': "400",
                'msg': f'requisition not available for id {item.req_id}'
            }

        if (req.issue_qty - req.consum_qty) < item.qty:
            return {
                'status': "400",
                'msg': f'Can not consume more than {req.issue_qty - req.consum_qty} quantity for id {item.req_id}'
            }

        else:
            # reduced from both to balance them
            req.consum_qty += item.qty

        # update inventory
        inventory = db.query(models.PManagerMatInventory).filter(
            models.PManagerMatInventory.m_id == req.m_id).first()
        if inventory:
            inventory.avail_qty -= item.qty

        else:
            return {
                'status': "400",
                'msg': 'insufficient quantity'
            }

    db.commit()

    return {
        'status': "200",
        'msg': 'material consumed successfully'
    }


@router.post("/complete/req")
def complete_req_by_slotId(slot: tSchemas.IssueSlot, db: Session = Depends(get_db)):

    # check for emp auth
    emp_query = db.query(models.Employees).filter(
        models.Employees.id == slot.issue_by).first()
    if not emp_query:
        return {
            'status': "400",
            'msg': 'employee can not complete requisition'
        }

    slot_data = db.query(models.Slot).filter(
        models.Slot.slot_id == slot.slot_id).first()
    if not slot_data:
        return {
            'status': "400",
            'msg': "slot not available",
        }

    # creation of new hist slot
    new_hist_slot = models.HistoryReqSlot(
        issued_by=slot_data.issued_by,
        req_by=slot_data.req_by,
        req_time=slot_data.req_time,
        issue_time=slot_data.issue_time,
        issue_status=slot_data.issue_status,
        remarks=slot_data.remarks)

    db.add(new_hist_slot)
    db.commit()
    db.refresh(new_hist_slot)

    for req in slot_data.requisition:
        # perform op to move from req to history_req
        new_hist_req = models.HistoryRequisition(
            m_id=req.m_id,
            qty_req=req.qty_req,
            issue_qty=req.issue_qty,
            consum_qty=req.consum_qty,
            slot_id=new_hist_slot.slot_id,
        )
        # update quantity consumed if not updated by prod manager
        # in case if prod manager has not returned total issue qty is used
        new_hist_req.consum_qty = req.issue_qty

        # remove the requisition list and add it to History Requisitions
        db.add(new_hist_req)
        db.delete(req)
        db.commit()

    db.delete(slot_data)  # delete old data
    db.commit()

    # his_slot_data = db.query(models.HistoryReqSlot, models.Employees).filter(models.HistoryReqSlot.slot_id == new_hist_slot.slot_id).join(
    #     models.Employees, models.Employees.id == models.HistoryReqSlot.req_by).first()

    return {
        'status': "200",
        'msg': "successfully completed requisitions",
        # 'data': {
        #     'slot_id': his_slot_data[0].slot_id,
        #     'req_time': his_slot_data[0].req_time,
        #     'complete_time': his_slot_data[0].comp_time,
        #     'remarks': his_slot_data[0].remarks,
        #     'issue_status': his_slot_data[0].issue_status,

        #     'req_by': {
        #         "id": his_slot_data[1].id,
        #         "name": his_slot_data[1].name,
        #         "email": his_slot_data[1].email,
        #         "role": his_slot_data[1].role,
        #         "phone": his_slot_data[1].phone,
        #         "created_at": his_slot_data[1].created_at,
        #         "is_active": his_slot_data[1].is_active,
        #     },


        #     'requisitions': [
        #         {
        #             'req_id': req.req_id,
        #             'qty_req': req.qty_req,
        #             'qty_issued': req.issue_qty,
        #             'qty_consumed': req.consum_qty,
        #             'mat_details': req.materials,
        #         } for req in his_slot_data[0].history_requisition
        #     ]
        # }
    }
    # except Exception as e:
    #     return {
    #         'status': "400",
    #         'msg': f"error occured {e}",
    #     }


router2 = APIRouter(prefix='/pmanager', tags=["ProductionManager (Product)"])


# for manufactured products
@router2.post("/handover/id",
              #  response_model=tSchemas.RequisitionOut,
              status_code=status.HTTP_200_OK)
def get_handover_req_by_empID(emp: tSchemas.EmpID, db: Session = Depends(get_db)):
    emp_query = db.query(models.Employees).filter(
        models.Employees.id == emp.emp_id).first()

    if not emp_query:
        return {
            'status': "400",
            'msg': 'employee does not exist'
        }

    batch_data_query = db.query(models.Batches, models.Employees).filter(models.Batches.handover_by == emp.emp_id).join(
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


@router2.post("/create/product",
              #  response_model=tSchemas.RequisitionOut,
              status_code=status.HTTP_200_OK)
def handover_batch(handovers: tSchemas.BatchesIn, db: Session = Depends(get_db)):
    emp_query = db.query(models.Employees).filter(
        models.Employees.id == handovers.hand_by).first()

    if not emp_query:
        return {
            'status': "400",
            'msg': 'employee cannot send request'
        }

    new_batch = models.Batches(
        remarks=handovers.remarks, handover_by=handovers.hand_by)
    db.add(new_batch)
    db.commit()
    db.refresh(new_batch)

    for prod in handovers.prods:
        new_handover = models.Prod_Handover(
            prod_id=prod.prod_id, qty=prod.qty, batch_id=new_batch.batch_id)

        db.add(new_handover)
        db.commit()
        db.refresh(new_handover)

    batch_data = db.query(models.Batches, models.Employees).filter(models.Batches.batch_id == new_batch.batch_id).join(
        models.Employees, models.Employees.id == models.Batches.handover_by).first()

    return {
        'status': "200",
        'msg': "successfully posted handover requests",
        'data': {
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
        }
    }
