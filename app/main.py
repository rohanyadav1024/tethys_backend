from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# import pandas as pd

from .database import engine
from . import models
from .routes import auth, employees, owner, otp, requests, prod_man, stock_man, material

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# file = 'file.xlsx'
# df = pd.read_excel(file)

# df.to_sql('materials', con=engine, if_exists='replace', index=False)
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Welcome to the API"}

app.include_router(employees.router)
app.include_router(owner.router)
app.include_router(auth.router)
app.include_router(otp.router)
app.include_router(requests.router)

app.include_router(material.router)
app.include_router(prod_man.router)
app.include_router(stock_man.router)


