"""Seed reference data for AgriAI.

Seeds:
  - Crops (with season and unit)
  - MSP prices for 2023-24 season (official govt data)
  - Synthetic market price data for multiple states/districts
"""
import sys
import os
from datetime import date, timedelta
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.database import SessionLocal, engine
from backend.models import Base, Crop, MspPrice, MarketPrice

# Ensure tables exist
Base.metadata.create_all(bind=engine)

# Official MSP for 2023-24 (Rs/quintal) - Govt of India data
CROPS = [
    {"name": "wheat",      "season": "rabi",   "unit": "tonne", "msp": 2275},
    {"name": "rice",       "season": "kharif", "unit": "tonne", "msp": 2183},
    {"name": "maize",      "season": "kharif", "unit": "tonne", "msp": 2090},
    {"name": "sugarcane",  "season": "kharif", "unit": "tonne", "msp": 315},
    {"name": "cotton",     "season": "kharif", "unit": "tonne", "msp": 6620},
    {"name": "pulses",     "season": "rabi",   "unit": "tonne", "msp": 5440},
    {"name": "groundnut",  "season": "kharif", "unit": "tonne", "msp": 6377},
    {"name": "mustard",    "season": "rabi",   "unit": "tonne", "msp": 5650},
    {"name": "potato",     "season": "rabi",   "unit": "tonne", "msp": 0},
    {"name": "tomato",     "season": "kharif", "unit": "tonne", "msp": 0},
    {"name": "soybean",    "season": "kharif", "unit": "tonne", "msp": 4600},
    {"name": "sunflower",  "season": "rabi",   "unit": "tonne", "msp": 6760},
    {"name": "jowar",      "season": "kharif", "unit": "tonne", "msp": 3180},
    {"name": "bajra",      "season": "kharif", "unit": "tonne", "msp": 2500},
]

MARKET_DATA = [
    {"state": "Maharashtra", "district": "Pune",       "market": "Pune Mandi"},
    {"state": "Maharashtra", "district": "Nashik",     "market": "Nashik Mandi"},
    {"state": "Maharashtra", "district": "Aurangabad", "market": "Aurangabad APMC"},
    {"state": "Maharashtra", "district": "Nagpur",     "market": "Nagpur Mandi"},
    {"state": "Maharashtra", "district": "Solapur",    "market": "Solapur APMC"},
    {"state": "Punjab",      "district": "Ludhiana",   "market": "Ludhiana Mandi"},
    {"state": "Punjab",      "district": "Amritsar",   "market": "Amritsar Grain Market"},
    {"state": "Punjab",      "district": "Jalandhar",  "market": "Jalandhar APMC"},
    {"state": "Punjab",      "district": "Patiala",    "market": "Patiala Mandi"},
    {"state": "Uttar Pradesh", "district": "Agra",     "market": "Agra Mandi"},
    {"state": "Uttar Pradesh", "district": "Meerut",   "market": "Meerut APMC"},
    {"state": "Uttar Pradesh", "district": "Kanpur",   "market": "Kanpur Mandi"},
    {"state": "Uttar Pradesh", "district": "Varanasi", "market": "Varanasi Mandi"},
    {"state": "Uttar Pradesh", "district": "Lucknow",  "market": "Lucknow APMC"},
    {"state": "Madhya Pradesh", "district": "Bhopal",  "market": "Bhopal Mandi"},
    {"state": "Madhya Pradesh", "district": "Indore",  "market": "Indore APMC"},
    {"state": "Madhya Pradesh", "district": "Jabalpur","market": "Jabalpur Mandi"},
    {"state": "Rajasthan",  "district": "Jaipur",      "market": "Jaipur Mandi"},
    {"state": "Rajasthan",  "district": "Jodhpur",     "market": "Jodhpur APMC"},
    {"state": "Rajasthan",  "district": "Udaipur",     "market": "Udaipur Mandi"},
    {"state": "Rajasthan",  "district": "Kota",        "market": "Kota APMC"},
    {"state": "Haryana",    "district": "Hisar",       "market": "Hisar Mandi"},
    {"state": "Haryana",    "district": "Karnal",      "market": "Karnal APMC"},
    {"state": "Haryana",    "district": "Gurugram",    "market": "Gurugram Mandi"},
    {"state": "Gujarat",    "district": "Ahmedabad",   "market": "Ahmedabad APMC"},
    {"state": "Gujarat",    "district": "Surat",       "market": "Surat Mandi"},
    {"state": "Gujarat",    "district": "Rajkot",      "market": "Rajkot Mandi"},
    {"state": "Karnataka",  "district": "Bengaluru",   "market": "Bengaluru APMC"},
    {"state": "Karnataka",  "district": "Mysuru",      "market": "Mysuru Mandi"},
    {"state": "West Bengal","district": "Kolkata",     "market": "Kolkata APMC"},
    {"state": "West Bengal","district": "Bardhaman",   "market": "Bardhaman Mandi"},
]

COMMODITY_PRICE_BASE = {
    "wheat":     {"min": 2000, "max": 2500},
    "rice":      {"min": 1800, "max": 2400},
    "maize":     {"min": 1600, "max": 2200},
    "sugarcane": {"min": 280,  "max": 360},
    "cotton":    {"min": 5800, "max": 7200},
    "pulses":    {"min": 4800, "max": 6200},
    "groundnut": {"min": 5500, "max": 7000},
    "mustard":   {"min": 5000, "max": 6500},
    "potato":    {"min": 800,  "max": 1500},
    "tomato":    {"min": 500,  "max": 2500},
    "soybean":   {"min": 4000, "max": 5200},
    "sunflower": {"min": 6000, "max": 7500},
    "jowar":     {"min": 2800, "max": 3500},
    "bajra":     {"min": 2100, "max": 2800},
}


def seed_crops(db):
    existing = {c.name for c in db.query(Crop).all()}
    added = 0
    for c in CROPS:
        if c["name"] not in existing:
            db.add(Crop(name=c["name"], season=c["season"], unit=c["unit"]))
            added += 1
    db.commit()
    print(f"  Added {added} crops (skipped {len(CROPS) - added} existing)")


def seed_msp(db):
    crops_map = {c.name: c.id for c in db.query(Crop).all()}
    added = 0
    skipped = 0
    for c in CROPS:
        if c["msp"] <= 0:
            continue
        crop_id = crops_map.get(c["name"])
        if not crop_id:
            continue
        exists = (
            db.query(MspPrice)
            .filter_by(crop_id=crop_id, marketing_season="2023-24", year=2023)
            .first()
        )
        if exists:
            skipped += 1
            continue
        db.add(MspPrice(
            crop_id=crop_id,
            marketing_season="2023-24",
            year=2023,
            msp_rs_per_quintal=float(c["msp"]),
            source="CACP/GoI 2023-24 official MSP",
        ))
        added += 1
    db.commit()
    print(f"  Added {added} MSP records (skipped {skipped} existing)")


def seed_market_prices(db, n_days=60):
    """Generate synthetic but realistic market price data."""
    today = date.today()
    added = 0
    skipped = 0

    for market_info in MARKET_DATA:
        for crop_name, price_range in COMMODITY_PRICE_BASE.items():
            base_price = random.uniform(price_range["min"], price_range["max"])
            for day_offset in range(n_days):
                obs_date = today - timedelta(days=day_offset)
                price = base_price * random.uniform(0.97, 1.03)
                modal = round(price, 2)
                min_p = round(modal * 0.93, 2)
                max_p = round(modal * 1.07, 2)

                exists = (
                    db.query(MarketPrice)
                    .filter_by(
                        source="synthetic-seed",
                        market=market_info["market"],
                        commodity=crop_name,
                        date=obs_date,
                        variety="",
                        grade="",
                    )
                    .first()
                )
                if exists:
                    skipped += 1
                    continue

                db.add(MarketPrice(
                    date=obs_date,
                    state=market_info["state"],
                    district=market_info["district"],
                    market=market_info["market"],
                    commodity=crop_name,
                    variety="",
                    grade="",
                    min_price=min_p,
                    max_price=max_p,
                    modal_price=modal,
                    arrivals=round(random.uniform(50, 5000), 1),
                    unit="quintal",
                    source="synthetic-seed",
                ))
                added += 1

                if added % 1000 == 0:
                    db.commit()
                    print(f"    ... committed {added} rows ...")

    db.commit()
    print(f"  Added {added} market price records (skipped {skipped} existing)")


def main():
    print("=" * 50)
    print("AgriAI: Seeding reference data")
    print("=" * 50)

    db = SessionLocal()
    try:
        print("\n[1/3] Seeding crops...")
        seed_crops(db)

        print("\n[2/3] Seeding MSP prices...")
        seed_msp(db)

        print("\n[3/3] Seeding market prices (60 days)...")
        seed_market_prices(db, n_days=60)

        print("\nSeeding complete!")
    except Exception as e:
        db.rollback()
        print(f"\nSeeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
