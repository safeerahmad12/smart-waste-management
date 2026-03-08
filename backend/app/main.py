from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routes import bins
from app import models

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Waste Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://smart-waste-management-ivory.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bins.router)


@app.get("/")
def root():
    return {"message": "Smart Waste Management API is running"}