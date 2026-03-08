from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import Bin


def get_status(fill_level: int) -> str:
    if fill_level >= 80:
        return "Full"
    if fill_level >= 40:
        return "Half Full"
    return "Empty"


def seed_bins():
    # Create tables first
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()

    bins = [
        # Aschaffenburg
        {"bin_name": "AB-01", "city": "Aschaffenburg", "location": "City Center", "area": "Mitte", "fill_level": 25},
        {"bin_name": "AB-02", "city": "Aschaffenburg", "location": "City Center", "area": "Mitte", "fill_level": 75},
        {"bin_name": "AB-03", "city": "Aschaffenburg", "location": "TH Aschaffenburg", "area": "Campus", "fill_level": 45},
        {"bin_name": "AB-04", "city": "Aschaffenburg", "location": "TH Aschaffenburg", "area": "Campus", "fill_level": 90},
        {"bin_name": "AB-05", "city": "Aschaffenburg", "location": "Train Station", "area": "Bahnhof", "fill_level": 20},
        {"bin_name": "AB-06", "city": "Aschaffenburg", "location": "Train Station", "area": "Bahnhof", "fill_level": 62},
        {"bin_name": "AB-07", "city": "Aschaffenburg", "location": "Shopping Street", "area": "Innenstadt", "fill_level": 83},
        {"bin_name": "AB-08", "city": "Aschaffenburg", "location": "City Park", "area": "Park", "fill_level": 38},
        {"bin_name": "AB-09", "city": "Aschaffenburg", "location": "Hospital Area", "area": "Klinik", "fill_level": 56},
        {"bin_name": "AB-10", "city": "Aschaffenburg", "location": "Bus Station", "area": "Transport", "fill_level": 88},

        # Frankfurt
        {"bin_name": "FFM-01", "city": "Frankfurt", "location": "Hauptbahnhof", "area": "Bahnhof", "fill_level": 92},
        {"bin_name": "FFM-02", "city": "Frankfurt", "location": "Zeil", "area": "Shopping", "fill_level": 70},
        {"bin_name": "FFM-03", "city": "Frankfurt", "location": "Main Tower", "area": "Innenstadt", "fill_level": 33},
        {"bin_name": "FFM-04", "city": "Frankfurt", "location": "Messe", "area": "Business", "fill_level": 44},
        {"bin_name": "FFM-05", "city": "Frankfurt", "location": "Airport Terminal 1", "area": "Airport", "fill_level": 85},
        {"bin_name": "FFM-06", "city": "Frankfurt", "location": "Airport Terminal 2", "area": "Airport", "fill_level": 59},
        {"bin_name": "FFM-07", "city": "Frankfurt", "location": "Römer", "area": "Old Town", "fill_level": 28},
        {"bin_name": "FFM-08", "city": "Frankfurt", "location": "Westend", "area": "Residential", "fill_level": 67},
        {"bin_name": "FFM-09", "city": "Frankfurt", "location": "University Campus", "area": "Campus", "fill_level": 81},
        {"bin_name": "FFM-10", "city": "Frankfurt", "location": "Sachsenhausen", "area": "Residential", "fill_level": 49},

        # Dietzenbach
        {"bin_name": "DTZ-01", "city": "Dietzenbach", "location": "Town Center", "area": "Mitte", "fill_level": 22},
        {"bin_name": "DTZ-02", "city": "Dietzenbach", "location": "Train Station", "area": "Bahnhof", "fill_level": 76},
        {"bin_name": "DTZ-03", "city": "Dietzenbach", "location": "Shopping Area", "area": "Retail", "fill_level": 84},
        {"bin_name": "DTZ-04", "city": "Dietzenbach", "location": "School Area", "area": "Education", "fill_level": 41},
        {"bin_name": "DTZ-05", "city": "Dietzenbach", "location": "Residential Block A", "area": "Residential", "fill_level": 37},
        {"bin_name": "DTZ-06", "city": "Dietzenbach", "location": "Residential Block B", "area": "Residential", "fill_level": 63},
        {"bin_name": "DTZ-07", "city": "Dietzenbach", "location": "Sports Center", "area": "Leisure", "fill_level": 52},
        {"bin_name": "DTZ-08", "city": "Dietzenbach", "location": "Bus Stop West", "area": "Transport", "fill_level": 88},
        {"bin_name": "DTZ-09", "city": "Dietzenbach", "location": "City Park", "area": "Park", "fill_level": 26},
        {"bin_name": "DTZ-10", "city": "Dietzenbach", "location": "Marketplace", "area": "Center", "fill_level": 71},

        # Offenbach
        {"bin_name": "OFF-01", "city": "Offenbach", "location": "Marktplatz", "area": "Center", "fill_level": 57},
        {"bin_name": "OFF-02", "city": "Offenbach", "location": "Main Riverbank", "area": "Riverfront", "fill_level": 32},
        {"bin_name": "OFF-03", "city": "Offenbach", "location": "Station Area", "area": "Bahnhof", "fill_level": 87},
        {"bin_name": "OFF-04", "city": "Offenbach", "location": "Shopping Mall", "area": "Retail", "fill_level": 79},
        {"bin_name": "OFF-05", "city": "Offenbach", "location": "Business District", "area": "Commercial", "fill_level": 45},
        {"bin_name": "OFF-06", "city": "Offenbach", "location": "Residential East", "area": "Residential", "fill_level": 23},
        {"bin_name": "OFF-07", "city": "Offenbach", "location": "Residential West", "area": "Residential", "fill_level": 66},
        {"bin_name": "OFF-08", "city": "Offenbach", "location": "Park South", "area": "Park", "fill_level": 91},
        {"bin_name": "OFF-09", "city": "Offenbach", "location": "School Zone", "area": "Education", "fill_level": 48},
        {"bin_name": "OFF-10", "city": "Offenbach", "location": "Bus Terminal", "area": "Transport", "fill_level": 73},

        # Darmstadt
        {"bin_name": "DA-01", "city": "Darmstadt", "location": "Luisenplatz", "area": "Center", "fill_level": 89},
        {"bin_name": "DA-02", "city": "Darmstadt", "location": "University Campus", "area": "Campus", "fill_level": 53},
        {"bin_name": "DA-03", "city": "Darmstadt", "location": "Main Station", "area": "Bahnhof", "fill_level": 77},
        {"bin_name": "DA-04", "city": "Darmstadt", "location": "Residential North", "area": "Residential", "fill_level": 21},
        {"bin_name": "DA-05", "city": "Darmstadt", "location": "Residential South", "area": "Residential", "fill_level": 47},
        {"bin_name": "DA-06", "city": "Darmstadt", "location": "Science Park", "area": "Innovation", "fill_level": 82},
        {"bin_name": "DA-07", "city": "Darmstadt", "location": "Shopping Zone", "area": "Retail", "fill_level": 36},
        {"bin_name": "DA-08", "city": "Darmstadt", "location": "Museum Area", "area": "Culture", "fill_level": 68},
        {"bin_name": "DA-09", "city": "Darmstadt", "location": "City Park", "area": "Park", "fill_level": 29},
        {"bin_name": "DA-10", "city": "Darmstadt", "location": "Bus Interchange", "area": "Transport", "fill_level": 93},
    ]

    for b in bins:
        existing = db.query(Bin).filter(Bin.bin_name == b["bin_name"]).first()
        if not existing:
            bin_obj = Bin(
                bin_name=b["bin_name"],
                city=b["city"],
                location=b["location"],
                area=b["area"],
                fill_level=b["fill_level"],
                status=get_status(b["fill_level"]),
            )
            db.add(bin_obj)

    db.commit()
    db.close()

    print("Seed data inserted successfully!")


if __name__ == "__main__":
    seed_bins()