from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import Base, engine, SessionLocal
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


def seed_demo_data():
    db: Session = SessionLocal()

    try:
        existing_bins = db.query(models.Bin).count()

        if existing_bins == 0:
            demo_bins = [
                models.Bin(
                    load_status="empty",
                    gas_status={
                        "status": "safe",
                        "message": "No harmful gases detected",
                        "concentration": "0 ppm",
                        "last_checked": "2024-11-24T12:00:00",
                    },
                    weight=0.0,
                    alert=False,
                    light_indicator=False,
                    buzzer=False,
                    last_updated="2024-11-24T12:00:00",
                ),
                models.Bin(
                    load_status="full",
                    gas_status={
                        "status": "safe",
                        "message": "No harmful gases detected",
                        "concentration": "0 ppm",
                        "last_checked": "2024-11-24T12:00:00",
                    },
                    weight=48.0,
                    alert=False,
                    light_indicator=True,
                    buzzer=True,
                    last_updated="2024-11-24T12:00:00",
                ),
                models.Bin(
                    load_status="full",
                    gas_status={
                        "status": "methane_detected",
                        "message": "Methane gas detected",
                        "concentration": "150 ppm",
                        "last_checked": "2024-11-24T12:10:00",
                    },
                    weight=50.0,
                    alert=True,
                    light_indicator=True,
                    buzzer=True,
                    last_updated="2024-11-24T12:10:00",
                ),
            ]

            db.add_all(demo_bins)
            db.commit()
    finally:
        db.close()


seed_demo_data()

app.include_router(bins.router)


@app.get("/")
def root():
    return {"message": "Smart Waste Management API is running"}