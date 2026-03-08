from datetime import datetime
import random
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Bin
from app.schemas import BinCreate, BinUpdate, BinResponse

router = APIRouter(prefix="/bins", tags=["Bins"])


def get_status_from_fill(fill_level: int) -> str:
    if fill_level >= 80:
        return "Full"
    if fill_level >= 40:
        return "Half Full"
    return "Empty"


@router.get("/", response_model=list[BinResponse])
def get_bins(
    city: str | None = Query(default=None),
    db: Session = Depends(get_db)
):
    query = db.query(Bin)

    if city:
        query = query.filter(Bin.city == city)

    return query.all()


@router.post("/", response_model=BinResponse)
def create_bin(bin_data: BinCreate, db: Session = Depends(get_db)):
    new_bin = Bin(
        bin_name=bin_data.bin_name,
        city=bin_data.city,
        location=bin_data.location,
        area=bin_data.area,
        fill_level=bin_data.fill_level,
        status=bin_data.status,
        last_updated=datetime.utcnow()
    )
    db.add(new_bin)
    db.commit()
    db.refresh(new_bin)
    return new_bin


@router.get("/{bin_id}", response_model=BinResponse)
def get_bin(bin_id: int, db: Session = Depends(get_db)):
    bin_obj = db.query(Bin).filter(Bin.id == bin_id).first()
    if not bin_obj:
        raise HTTPException(status_code=404, detail="Bin not found")
    return bin_obj


@router.put("/{bin_id}", response_model=BinResponse)
def update_bin(bin_id: int, bin_data: BinUpdate, db: Session = Depends(get_db)):
    bin_obj = db.query(Bin).filter(Bin.id == bin_id).first()
    if not bin_obj:
        raise HTTPException(status_code=404, detail="Bin not found")

    bin_obj.bin_name = bin_data.bin_name
    bin_obj.city = bin_data.city
    bin_obj.location = bin_data.location
    bin_obj.area = bin_data.area
    bin_obj.fill_level = bin_data.fill_level
    bin_obj.status = bin_data.status
    bin_obj.last_updated = datetime.utcnow()

    db.commit()
    db.refresh(bin_obj)
    return bin_obj


@router.delete("/{bin_id}")
def delete_bin(bin_id: int, db: Session = Depends(get_db)):
    bin_obj = db.query(Bin).filter(Bin.id == bin_id).first()
    if not bin_obj:
        raise HTTPException(status_code=404, detail="Bin not found")

    db.delete(bin_obj)
    db.commit()
    return {"message": "Bin deleted successfully"}


@router.post("/simulate")
def simulate_sensor_updates(db: Session = Depends(get_db)):
    bins = db.query(Bin).all()

    if not bins:
        return {"message": "No bins available for simulation"}

    updated_count = 0

    for bin_obj in bins:
        action = random.choices(
            ["increase", "same", "decrease"],
            weights=[60, 25, 15],
            k=1
        )[0]

        if action == "increase":
            increase = random.randint(2, 10)
            bin_obj.fill_level = min(bin_obj.fill_level + increase, 100)

        elif action == "decrease":
            decrease = random.randint(10, 40)
            bin_obj.fill_level = max(bin_obj.fill_level - decrease, 0)

        # "same" means no change

        bin_obj.status = get_status_from_fill(bin_obj.fill_level)
        bin_obj.last_updated = datetime.utcnow()
        updated_count += 1

    db.commit()

    return {
        "message": "Sensor simulation completed",
        "updated_bins": updated_count
    }