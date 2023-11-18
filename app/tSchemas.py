from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

from sqlalchemy import Double

from . import schemas

class MaterialId(BaseModel):
    id : int

class MaterialIn(BaseModel):
    material : str
    umo : str
    g_no : int

class Material(MaterialIn):
    id : int

class MaterialListOut(BaseModel):
    status: str
    data : List[Material]
    

class ReqMat(BaseModel):
    id : int
    qty : int

class RequisitionIn(BaseModel):
    items : List[ReqMat]
    req_by : int
    remarks: Optional[str] = None

class Requisition(RequisitionIn):
    req_id : int
    req_time : datetime
    # issue_details : Optional[int] = None

class RequisitionOut(BaseModel):
    status: str
    data : List[Requisition]

class EmpID(BaseModel):
    emp_id : int
class SlotData(BaseModel):
    slot_id : int
class IssueSlot(SlotData):
    issue_by : int

class IssueReq(BaseModel):
    issue_materials : List[ReqMat]
    issue_by: int

class BatchData(BaseModel):
    batch_id : int

class AcceptBatch(BatchData):
    recieved_by : int

# class Issued(BaseModel):
#     material : str
#     qty_issued : int
#     remarks : Optional[str] = None
#     issued_by : Optional[int] = None

# class IssuedOut(Issued):
#     issue_id : int
#     issue_time : datetime


# class Returns(BaseModel):
#     material : str
#     qty_ret : int
#     remarks : Optional[str] = None
#     ret_by : Optional[int] = None

# class ReturnsOut(Returns):
#     ret_id : int
#     ret_time : datetime


# class Productions(BaseModel):
#     product : str
#     batch_no : int
#     qty : int
#     remarks : Optional[str] = None
#     prod_manager : Optional[int] = None

# class ProductionsOut(Productions):
#     prod_id : int
#     recieved_by : Optional[int] = None
#     mfg : datetime

class Orders(BaseModel):
    m_id : int
    ord_qty : int

    
class Purchases(BaseModel):
    supp_name : str
    t_amount : float
    invoice : str
    vehicle : str
    remarks : Optional[str] = None
    exp_date : Optional[datetime] = None
    pur_by : int
    orders : List[Orders]

# class PurchasesOut(Purchases):
#     pur_id : int
#     pur_time : datetime



    

# class OrdersOut(Orders):
#     ord_id : int
#     pur_detials : PurchasesOut
#     gk_id : Optional[int] = None
#     recv_time : Optional[datetime] = None

class ProdHandover(BaseModel):
    p_name: str
    qty: int

class BatchesIn(BaseModel):
    prods: List[ProdHandover]
    hand_by: int
    remarks: Optional[str] = None


class Consignments(BaseModel):
    product : str
    qty : int

class Dispatches(BaseModel):
    buyer : str
    invoice_value : float #total amount
    invoice : str
    veh_no: str
    transport_name: str
    driv_name: str
    driv_phone: str
    driv_license: str
    remarks : Optional[str] = None
    dis_by : int
    consigns : List[Consignments]

class GateOrders(BaseModel):
    order_id: int
    qty_recieved: int

class CheckOrders(BaseModel):
    pur_id : int
    recieved_by: int
    orders: List[GateOrders]

class GateConsignments(BaseModel):
    cons_id: int
    qty_checked: int

class CheckConsignments(BaseModel):
    dis_id : int
    checked_by: int
    consigns: List[GateConsignments]

