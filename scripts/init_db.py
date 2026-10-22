#!/usr/bin/env python3
"""
Initialize the AgriAI database by creating tables and running migrations.
"""
import os
import sys

# Add the project root to the path BEFORE importing backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import ALL models BEFORE creating tables
from backend.models import (
    User, Farm, SoilTest, Crop, FarmCycle,
    YieldPrediction, MspPrice, MarketPrice,
    MarketRecommendation, ModelRegistry
)

from sqlalchemy import create_engine, text
from backend.database import Base, engine

def main():
    """Initialize the database using SQLite."""
    print("Initializing AgriAI database...")
    
    # Create all tables (models must be imported first!)
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully")
    
    # Seed the crops table
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    crops = [
        {"name": "wheat", "season": "rabi", "unit": "quintal"},
        {"name": "rice", "season": "kharif", "unit": "quintal"},
        {"name": "maize", "season": "kharif", "unit": "quintal"},
        {"name": "sugarcane", "season": "kharif", "unit": "tonne"},
        {"name": "cotton", "season": "kharif", "unit": "quintal"},
        {"name": "pulses", "season": "rabi", "unit": "quintal"},
        {"name": "groundnut", "season": "kharif", "unit": "quintal"},
        {"name": "mustard", "season": "rabi", "unit": "quintal"},
        {"name": "potato", "season": "rabi", "unit": "quintal"},
        {"name": "tomato", "season": "kharif", "unit": "quintal"},
    ]
    
    for crop_data in crops:
        existing = session.query(Crop).filter_by(name=crop_data["name"]).first()
        if not existing:
            crop = Crop(**crop_data)
            session.add(crop)
    
    session.commit()
    session.close()
    
    print("✅ Crops seeded successfully")
    print("✅ Database initialization complete!")

if __name__ == "__main__":
    main()