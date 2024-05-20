from app.database import get_db
from app import schemas, models
from fastapi import APIRouter, Depends, status
from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from typing import List
from collections import defaultdict
from typing import Dict, List

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


router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
def get_products_list(db: Session = Depends(get_db)):

    # Fetch all products from the database
    products = db.query(models.Products).all()

    # Group products by g_no
    grouped_products: Dict[str, List[models.Products]] = defaultdict(list)
    for product in products:
        grouped_products[product.g_no].append(product)

    # Sort products within each group alphabetically by product name
    for product_list in grouped_products.values():
        product_list.sort(key=lambda x: x.product.lower()
                          )  # Sort ignoring case

    # Prepare response data
    categorized_products = []
    for g_no, product_list in grouped_products.items():
        categorized_products.append({
            "g_no": g_no,
            "products": [
                {
                    "id": product.id,
                    "product": product.product,
                    "g_no": product.g_no,
                } for product in product_list
            ]
        })

    return {
        "status": "200",
        'msg': "successfully fetched data",
        "data": categorized_products
    }


@router.post('/create')
def add_product(mats: List[tSchemas.ProductIn], db: Session = Depends(get_db)):

    materials = []
    for mat in mats:
        new_mat = models.Products(product=mat.product, g_no=mat.g_no)

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
