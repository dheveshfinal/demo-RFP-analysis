# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from model import BidCompany   
from components.RFP_document import router as RFP_router
from components.mycompanydata import router as mycompanydata_router

app = FastAPI()


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(RFP_router)
app.include_router(mycompanydata_router)


@app.get("/")
def root():
    return {"message": "RFP Analysis API is running", "status": "healthy"}

