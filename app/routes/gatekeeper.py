from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List

from .. import schemas, tSchemas, models, utils, oauth2, config
from ..database import get_db

router = APIRouter(prefix='/gkeep', tags=["Gate Keeper"])


@router.get("/",
            status_code=status.HTTP_200_OK)
def get_all_orders(db: Session = Depends(get_db)):
    
    purch_data_query = db.query(models.Purchases, models.Employees).join(
        models.Employees, models.Employees.id == models.Purchases.pur_by).all()

    return {
        'status': "200",
        'msg': "successfully fetched material orders",
        'data': [{
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
        } for slot_data in purch_data_query
        ]
    }

@router.post("/orders/check",
             status_code=status.HTTP_200_OK)
def check_orders(checks: tSchemas.CheckOrders,
                       db: Session = Depends(get_db)):
    
    for rec_order in checks.orders:
        order_qry = db.query(models.Orders).filter(models.Orders.ord_id == rec_order.order_id).first()
        if order_qry:
            order_qry.recieved_qty = rec_order.qty_recieved
            db.commit()
            db.refresh(order_qry)

            invent_item = db.query(models.RawMaterialInventory).filter(models.RawMaterialInventory.m_id == order_qry.m_id).first()
            if invent_item:
                invent_item.avail_qty += order_qry.recieved_qty
            else:
                new_inv_item = models.RawMaterialInventory(m_id=order_qry.m_id, avail_qty=order_qry.recieved_qty)
                db.add(new_inv_item)
            db.commit()

        else:
            continue

    slot_data = db.query(models.Purchases).filter(models.Purchases.pur_id == checks.pur_id).first()
    slot_data.recieved = True
        
    db.commit()
    db.refresh(slot_data)

    # updating inventory
    

    emp = db.query(models.Employees).filter(models.Employees.id == checks.recieved_by).first()

    return {
        'status': "200",
        'msg': "successfully updated recieved orders",
        'data': {
            'pur_id': slot_data.pur_id,
            'pur_time': slot_data.pur_time,
            'remarks': slot_data.remarks,
            'recieved': slot_data.recieved,
            'invoice': slot_data.invoice,
            'vehicle': slot_data.vehicle,
            'exp_date': slot_data.exp_date,

            'rec_by': {
                "id": emp.id,
                "name": emp.name,
                "email": emp.email,
                "role": emp.role,
                "phone": emp.phone,
                "created_at": emp.created_at,
                "is_active": emp.is_active,
            },

            'orders': [
                {
                    'order_id': ord.ord_id,
                    'qty_req': ord.ord_qty,
                    'qty_rec': ord.recieved_qty,
                    'mat_details': ord.materials,
                } for ord in slot_data.orders
            ]
        }
    }

    