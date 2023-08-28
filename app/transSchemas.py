# from pydantic import BaseModel, EmailStr
# from typing import Optional, List
# from datetime import datetime

# class Requisition(BaseModel):
#     material : str
#     qty_req : int
#     remarks : Optional[str] = None
#     req_by : Optional[int] = None

# class RequisitionOut(Requisition):
#     req_id : int
#     req_time : datetime
#     issue_details : Optional[int] = None


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


# class Purchases(BaseModel):
#     supp : str
#     material : str
#     amount : int
#     invoice : str
#     vehicle : str

# class PurchasesOut(Purchases):
#     pur_id : int
#     pur_time : datetime


# class Orders(BaseModel):
#     product : str
#     ord_qty : int
#     recieved_qty : Optional[int] = 0
#     remarks : Optional[str] = None
#     exp_date : Optional[datetime] = None

# class OrdersOut(Orders):
#     ord_id : int
#     pur_detials : PurchasesOut
#     gk_id : Optional[int] = None
#     recv_time : Optional[datetime] = None

