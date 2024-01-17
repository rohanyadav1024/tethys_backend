from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from typing import List

from .. import tSchemas, models
from ..database import get_db

router = APIRouter(prefix='/products', tags=["Products Available"])

# materials = {
# 1 : Raw Material
# 2 : PACKING MATERIAL
# 3 : CHEMICAL
# 4 : BELT
# 5 : LUBRICANT
# 6 : PU FITTINGS
# 7 : BOLT & NUT
# 8 : BOND
# 9 : WATER
# 10 :  BLOW MOULDING
# 11 :  ELECTRICAL
# 12 :  BEARING
# 13 :  WATBEARING 2RS1
# 14 :  BEARING BT1-0525
# 15 :  PADISOR BEARING
# }


@router.get("/",
            response_model=tSchemas.ProductListOut,
            status_code=status.HTTP_200_OK)
def get_products_list(db: Session = Depends(get_db)):

    materials = db.query(models.Products).all()

    return {
        "status": "200",
        'msg': "successfully fetched data",
        "data": materials
    }


@router.post('/create')
def add_product(mats: List[tSchemas.ProductIn], db: Session = Depends(get_db)):

    materials = []
    for mat in mats:
        new_mat = models.Material(product=mat.product)

        materials.append(new_mat)
        db.add(new_mat)
        db.commit()

    for material in materials:
        db.refresh(material)

    return {
        'status': '200',
        'msg': f'{len(materials)} records added successfully!',
        'data': materials
    }


@router.delete('/delete')
def remove_product(mat: tSchemas.ProductId, db: Session = Depends(get_db)):

    db_mat = db.query(models.Products).filter(models.Products.id == mat.id)

    if db_mat.first() is None:
        return {'status': '400', 'msg': f"No record found with id '{mat}'"}

    db_mat.delete(synchronize_session=False)
    db.commit()

    return {
        'status': '200',
        'msg': 'deleted successfully',
    }
