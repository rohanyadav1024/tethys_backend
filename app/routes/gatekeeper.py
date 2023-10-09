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