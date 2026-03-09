from copy import deepcopy
from datetime import datetime
import random

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/bins", tags=["Bins"])


def now_str():
    return datetime.utcnow().isoformat()


def get_status(fill_level: int) -> str:
    if fill_level >= 80:
        return "Full"
    if fill_level >= 40:
        return "Half Full"
    return "Empty"


DEMO_BINS = [
    {
        "id": 1,
        "bin_name": "AB-01",
        "city": "Aschaffenburg",
        "location": "City Center",
        "area": "Mitte",
        "fill_level": 25,
        "status": "Empty",
        "last_updated": now_str(),
    },
    {
        "id": 2,
        "bin_name": "FFM-01",
        "city": "Frankfurt",
        "location": "Hauptbahnhof",
        "area": "Bahnhof",
        "fill_level": 84,
        "status": "Full",
        "last_updated": now_str(),
    },
    {
        "id": 3,
        "bin_name": "DTZ-01",
        "city": "Dietzenbach",
        "location": "Marketplace",
        "area": "Center",
        "fill_level": 67,
        "status": "Half Full",
        "last_updated": now_str(),
    },
]

BINS = deepcopy(DEMO_BINS)


@router.get("/")
def get_bins():
    return BINS


@router.get("/{bin_id}")
def get_bin(bin_id: int):
    for bin_obj in BINS:
        if bin_obj["id"] == bin_id:
            return bin_obj
    raise HTTPException(status_code=404, detail="Bin not found")


@router.post("/")
def create_bin(bin_data: dict):
    new_id = max((b["id"] for b in BINS), default=0) + 1
    fill_level = int(bin_data.get("fill_level", 0))

    new_bin = {
        "id": new_id,
        "bin_name": bin_data.get("bin_name", f"Bin {new_id}"),
        "city": bin_data.get("city", "Aschaffenburg"),
        "location": bin_data.get("location", "Unknown"),
        "area": bin_data.get("area", "General"),
        "fill_level": fill_level,
        "status": get_status(fill_level),
        "last_updated": now_str(),
    }

    BINS.append(new_bin)
    return new_bin


@router.put("/{bin_id}")
def update_bin(bin_id: int, bin_data: dict):
    for bin_obj in BINS:
        if bin_obj["id"] == bin_id:
            fill_level = int(bin_data.get("fill_level", bin_obj["fill_level"]))

            bin_obj["bin_name"] = bin_data.get("bin_name", bin_obj["bin_name"])
            bin_obj["city"] = bin_data.get("city", bin_obj["city"])
            bin_obj["location"] = bin_data.get("location", bin_obj["location"])
            bin_obj["area"] = bin_data.get("area", bin_obj["area"])
            bin_obj["fill_level"] = fill_level
            bin_obj["status"] = get_status(fill_level)
            bin_obj["last_updated"] = now_str()

            return bin_obj

    raise HTTPException(status_code=404, detail="Bin not found")


@router.delete("/{bin_id}")
def delete_bin(bin_id: int):
    global BINS
    for bin_obj in BINS:
        if bin_obj["id"] == bin_id:
            BINS = [b for b in BINS if b["id"] != bin_id]
            return {"message": "Bin deleted successfully"}

    raise HTTPException(status_code=404, detail="Bin not found")


@router.post("/simulate")
def simulate_sensor_updates():
    updated_count = 0

    for bin_obj in BINS:
        action = random.choices(
            ["increase", "same", "decrease"],
            weights=[60, 25, 15],
            k=1,
        )[0]

        if action == "increase":
            increase = random.randint(5, 15)
            bin_obj["fill_level"] = min(bin_obj["fill_level"] + increase, 100)
        elif action == "decrease":
            decrease = random.randint(10, 40)
            bin_obj["fill_level"] = max(bin_obj["fill_level"] - decrease, 0)

        bin_obj["status"] = get_status(bin_obj["fill_level"])
        bin_obj["last_updated"] = now_str()
        updated_count += 1

    return {
        "message": "Sensor simulation completed",
        "updated_bins": updated_count,
    }