from datetime import datetime
import random
from copy import deepcopy

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/bins", tags=["Bins"])

BINS = []


def now_str():
    return datetime.utcnow().isoformat()


def get_status(fill_level: int) -> str:
    if fill_level >= 80:
        return "Full"
    if fill_level >= 40:
        return "Half Full"
    return "Empty"


def generate_demo_bins():
    global BINS

    cities = ["Aschaffenburg", "Frankfurt", "Dietzenbach", "Offenbach", "Darmstadt"]

    city_locations = {
        "Aschaffenburg": [
            ("City Center", "Mitte"),
            ("TH Aschaffenburg", "Campus"),
            ("Train Station", "Bahnhof"),
            ("Shopping Street", "Innenstadt"),
            ("City Park", "Park"),
            ("Hospital Area", "Klinik"),
            ("Bus Station", "Transport"),
            ("Residential Block A", "Wohngebiet"),
            ("Marketplace", "Center"),
            ("Library Area", "Education"),
        ],
        "Frankfurt": [
            ("Hauptbahnhof", "Bahnhof"),
            ("Zeil", "Shopping"),
            ("Main Tower", "Innenstadt"),
            ("Messe", "Business"),
            ("Römer", "Altstadt"),
            ("Westbahnhof", "Transport"),
            ("Uni Campus", "Education"),
            ("Riverside", "Tourism"),
            ("Residential Block B", "Wohngebiet"),
            ("Airport Zone", "Transit"),
        ],
        "Dietzenbach": [
            ("Marketplace", "Center"),
            ("Bus Stop West", "Transport"),
            ("City Park", "Park"),
            ("Residential Area A", "Wohngebiet"),
            ("Shopping Corner", "Commercial"),
            ("School Zone", "Education"),
            ("Station Area", "Bahnhof"),
            ("Sports Hall", "Recreation"),
            ("Town Hall", "Admin"),
            ("Medical Center", "Health"),
        ],
        "Offenbach": [
            ("Marktplatz", "Center"),
            ("Station Area", "Bahnhof"),
            ("Mall Entrance", "Shopping"),
            ("Riverside Walk", "Tourism"),
            ("Residential Area B", "Wohngebiet"),
            ("School Street", "Education"),
            ("Business Hub", "Commercial"),
            ("Park South", "Park"),
            ("Hospital Front", "Health"),
            ("Bus Terminal", "Transport"),
        ],
        "Darmstadt": [
            ("Luisenplatz", "Center"),
            ("TU Darmstadt", "Campus"),
            ("Main Station", "Bahnhof"),
            ("Residential Quarter", "Wohngebiet"),
            ("City Mall", "Shopping"),
            ("Science Park", "Business"),
            ("Clinic Area", "Health"),
            ("Museum Street", "Tourism"),
            ("Bus Depot", "Transport"),
            ("Library Plaza", "Education"),
        ],
    }

    bins = []
    counter = 1

    for city in cities:
        locations = city_locations[city]

        for idx, (location, area) in enumerate(locations, start=1):
            fill_level = random.randint(5, 100)

            bins.append(
                {
                    "id": counter,
                    "bin_name": f"{city[:3].upper()}-{idx:02}",
                    "city": city,
                    "location": location,
                    "area": area,
                    "fill_level": fill_level,
                    "status": get_status(fill_level),
                    "last_updated": now_str(),
                }
            )
            counter += 1

    BINS = bins


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
    global BINS

    new_id = max((b["id"] for b in BINS), default=0) + 1
    fill_level = int(bin_data.get("fill_level", 0))

    new_bin = {
        "id": new_id,
        "bin_name": bin_data.get("bin_name", f"BIN-{new_id:02}"),
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