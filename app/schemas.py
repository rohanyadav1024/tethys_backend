from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class OAuth2PasswordRequestFormJSON(BaseModel):
    username : str #phone number
    password : str

class StatusClass(BaseModel):
    status : str


#owners
class Owner(BaseModel):
    name:str
    phone:Optional[str] = None
    email:EmailStr

class CreateOwner(Owner):
    password : str
    secret_key:str

class OwnerOut(Owner):
    id : int
    created_at: datetime
    is_active:bool

    class Config():
        orm_mode=True

class OwnerData(StatusClass):
    data : OwnerOut
    class Config():
        orm_mode=True

class OwnerDataList(StatusClass):
    data : List[OwnerOut]
    class Config():
        orm_mode=True


#employees
class Employee(BaseModel):
    name:str
    email:EmailStr
    role:int
    phone:Optional[str] = None

class CreateEmployee(Employee):
    password : str

class EmployeeOut(Employee):
    id: int
    created_at: datetime
    is_active: bool

    class Config:
        orm_mode=True

class EmployeeData(StatusClass):
    data : EmployeeOut
    class Config():
        orm_mode=True

class EmployeeDataList(StatusClass):
    data : List[EmployeeOut]
    class Config():
        orm_mode=True



#permission schema
class Requests(BaseModel):
    req_id: int
    
class RequestsOut(Requests):
    employee: EmployeeOut
    
class RequestsData(StatusClass):
    data: List[RequestsOut]
    


#token schema
class TokenData(BaseModel):
    id : int
    isowner: bool

#to retrun to user(main token)
class Token(BaseModel): 
    access_token : str
    token_type : str = "Bearer"


#authentication response with token
class LoginResponse(Token):
    status : str
    user: EmployeeOut


#utilitis
#for otp sending through email
class EmailData(BaseModel):
    email: str

class UserId(BaseModel):
    user_id: int

class SecretKey(UserId):
    secret_key: str


####phase 2 schemas
# class Material(BaseModel):
#     m_id : int
#     qty_req : int
    

# class Requisition(BaseModel):
#     materials : List[Material]
#     remarks : Optional[str] = None
#     req_by : int = None

# class RequisitionOut(Requisition):
#     req_id : int
#     req_time : datetime
#     issue_details : Optional[int] = None