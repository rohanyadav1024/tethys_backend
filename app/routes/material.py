from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List

from .. import schemas, tSchemas, models, utils, oauth2, config
from ..database import get_db

router = APIRouter(prefix='/material', tags=["Materials Available"])

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
            response_model=tSchemas.MaterialListOut,
            status_code=status.HTTP_200_OK)
def get_materials_list(db: Session = Depends(get_db)):

    materials = db.query(models.Material).all()

    return {
        "status": "200",
        'msg' : "successfully fetched data",
        "data": materials
    }

@router.post('/create')
def add_material(mats: List[tSchemas.MaterialIn], db: Session = Depends(get_db)):

    materials = []
    for mat in mats:
        new_mat = models.Material(material=mat.material, umo=mat.umo, g_no=mat.g_no)

        materials.append(new_mat)
        db.add(new_mat)
        db.commit()

    for material in materials:
        db.refresh(material)

    return{
        'status' : '200',
        'msg': f'{len(materials)} records added successfully!',
        'data' : materials
    }


@router.delete('/delete')
def add_material(mat :tSchemas.MaterialId, db: Session = Depends(get_db)):

    db_mat = db.query(models.Material).filter(models.Material.id == mat.id)

    if db_mat.first() is None:
        return {'status':'400','msg':f"No record found with id '{mat}'"}
    
    db_mat.delete(synchronize_session = False)
    db.commit()

    return{
        'status' : '200',
        'msg' : 'deleted successfully',
    }
    