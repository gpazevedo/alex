#!/usr/bin/env python3
"""
Seed data for Alex Financial Planner - DynamoDB version
Loads 22 popular ETF instruments with allocation data
"""

import os
from decimal import Decimal
from datetime import datetime
from src import Database
from src.schemas import InstrumentCreate
from dotenv import load_dotenv

load_dotenv(override=True)

# Define popular ETF instruments with realistic allocation data
# All percentages should sum to 100 for each allocation type
INSTRUMENTS = [
    # Core US Equity
    {
        "symbol": "SPY",
        "name": "SPDR S&P 500 ETF Trust",
        "instrument_type": "etf",
        "current_price": Decimal("450.25"),
        "allocation_regions": {"north_america": 100},
        "allocation_sectors": {
            "technology": 28,
            "healthcare": 13,
            "financials": 13,
            "consumer_discretionary": 12,
            "industrials": 9,
            "communication": 9,
            "consumer_staples": 6,
            "energy": 4,
            "utilities": 3,
            "real_estate": 2,
            "materials": 1,
        },
        "allocation_asset_class": {"equity": 100},
    },
    {
        "symbol": "QQQ",
        "name": "Invesco QQQ Trust",
        "instrument_type": "etf",
        "current_price": Decimal("385.50"),
        "allocation_regions": {"north_america": 100},
        "allocation_sectors": {"technology": 50, "communication": 15, "consumer_discretionary": 15, "healthcare": 10, "industrials": 6, "other": 4},
        "allocation_asset_class": {"equity": 100},
    },
    {
        "symbol": "BND",
        "name": "Vanguard Total Bond Market ETF",
        "instrument_type": "etf",
        "current_price": Decimal("72.80"),
        "allocation_regions": {"north_america": 100},
        "allocation_sectors": {"treasury": 40, "corporate": 30, "mortgage": 25, "other": 5},
        "allocation_asset_class": {"fixed_income": 100},
    },
    {
        "symbol": "VTI",
        "name": "Vanguard Total Stock Market ETF",
        "instrument_type": "etf",
        "current_price": Decimal("235.60"),
        "allocation_regions": {"north_america": 100},
        "allocation_sectors": {
            "technology": 26,
            "financials": 14,
            "healthcare": 13,
            "consumer_discretionary": 11,
            "industrials": 10,
            "communication": 8,
            "consumer_staples": 6,
            "energy": 5,
            "real_estate": 4,
            "materials": 2,
            "utilities": 1
        },
        "allocation_asset_class": {"equity": 100},
    },
    {
        "symbol": "AGG",
        "name": "iShares Core US Aggregate Bond ETF",
        "instrument_type": "etf",
        "current_price": Decimal("98.50"),
        "allocation_regions": {"north_america": 100},
        "allocation_sectors": {"treasury": 42, "mortgage": 28, "corporate": 25, "other": 5},
        "allocation_asset_class": {"fixed_income": 100},
    },
    {
        "symbol": "VEA",
        "name": "Vanguard FTSE Developed Markets ETF",
        "instrument_type": "etf",
        "current_price": Decimal("47.20"),
        "allocation_regions": {"europe": 45, "asia": 30, "north_america": 15, "oceania": 8,"africa": 2},
        "allocation_sectors": {"financials": 18, "industrials": 14, "healthcare": 13, "consumer_discretionary": 12, "technology": 11, "materials": 9, "consumer_staples": 9, "energy": 7, "utilities": 4, "real_estate": 2, "communication": 1},
        "allocation_asset_class": {"equity": 100},
    },
    {
        "symbol": "VWO",
        "name": "Vanguard FTSE Emerging Markets ETF",
        "instrument_type": "etf",
        "current_price": Decimal("41.30"),
        "allocation_regions": {"asia": 75, "latin_america": 12, "africa": 8, "middle_east": 5},
        "allocation_sectors": {"technology": 22, "financials": 20, "consumer_discretionary": 15, "communication": 12, "materials": 10, "energy": 8, "industrials": 7, "consumer_staples": 4, "healthcare": 1, "other": 1},
        "allocation_asset_class": {"equity": 100},
    },
    {
        "symbol": "IWM",
        "name": "iShares Russell 2000 ETF",
        "instrument_type": "etf",
        "current_price": Decimal("199.40"),
        "allocation_regions": {"north_america": 100},
        "allocation_sectors": {"financials": 17, "healthcare": 16, "industrials": 15, "technology": 13, "consumer_discretionary": 11, "real_estate": 8, "materials": 6, "energy": 5, "consumer_staples": 4, "utilities": 3, "communication": 2},
        "allocation_asset_class": {"equity": 100},
    },
    {
        "symbol": "GLD",
        "name": "SPDR Gold Shares",
        "instrument_type": "etf",
        "current_price": Decimal("185.30"),
        "allocation_regions": {"global": 100},
        "allocation_sectors": {"commodities": 100},
        "allocation_asset_class": {"commodities": 100},
    },
    {
        "symbol": "TLT",
        "name": "iShares 20+ Year Treasury Bond ETF",
        "instrument_type": "etf",
        "current_price": Decimal("91.70"),
        "allocation_regions": {"north_america": 100},
        "allocation_sectors": {"treasury": 100},
        "allocation_asset_class": {"fixed_income": 100},
    },
    {
        "symbol": "VOO",
        "name": "Vanguard S&P 500 ETF",
        "instrument_type": "etf",
        "current_price": Decimal("412.80"),
        "allocation_regions": {"north_america": 100},
        "allocation_sectors": {
            "technology": 28,
            "healthcare": 13,
            "financials": 13,
            "consumer_discretionary": 12,
            "industrials": 9,
            "communication": 9,
            "consumer_staples": 6,
            "energy": 4,
            "utilities": 3,
            "real_estate": 2,
            "materials": 1
        },
        "allocation_asset_class": {"equity": 100},
    },
    {
        "symbol": "VCIT",
        "name": "Vanguard Intermediate-Term Corporate Bond ETF",
        "instrument_type": "etf",
        "current_price": Decimal("81.50"),
        "allocation_regions": {"north_america": 100},
        "allocation_sectors": {"corporate": 100},
        "allocation_asset_class": {"fixed_income": 100},
    },
    {
        "symbol": "VNQ",
        "name": "Vanguard Real Estate ETF",
        "instrument_type": "etf",
        "current_price": Decimal("88.20"),
        "allocation_regions": {"north_america": 100},
        "allocation_sectors": {"real_estate": 100},
        "allocation_asset_class": {"real_estate": 100},
    },
    {
        "symbol": "VTV",
        "name": "Vanguard Value ETF",
        "instrument_type": "etf",
        "current_price": Decimal("150.30"),
        "allocation_regions": {"north_america": 100},
        "allocation_sectors": {"financials": 21, "healthcare": 16, "industrials": 14, "consumer_staples": 10, "energy": 10, "utilities": 8, "consumer_discretionary": 7, "technology": 6, "materials": 5, "communication": 2, "real_estate": 1},
        "allocation_asset_class": {"equity": 100},
    },
    {
        "symbol": "VUG",
        "name": "Vanguard Growth ETF",
        "instrument_type": "etf",
        "current_price": Decimal("312.40"),
        "allocation_regions": {"north_america": 100},
        "allocation_sectors": {"technology": 48, "consumer_discretionary": 17, "communication": 12, "healthcare": 10, "industrials": 7, "financials": 4, "consumer_staples": 1, "other": 1},
        "allocation_asset_class": {"equity": 100},
    },
    {
        "symbol": "XLE",
        "name": "Energy Select Sector SPDR Fund",
        "instrument_type": "etf",
        "current_price": Decimal("88.50"),
        "allocation_regions": {"north_america": 100},
        "allocation_sectors": {"energy": 100},
        "allocation_asset_class": {"equity": 100},
    },
    {
        "symbol": "XLF",
        "name": "Financial Select Sector SPDR Fund",
        "instrument_type": "etf",
        "current_price": Decimal("39.20"),
        "allocation_regions": {"north_america": 100},
        "allocation_sectors": {"financials": 100},
        "allocation_asset_class": {"equity": 100},
    },
    {
        "symbol": "XLK",
        "name": "Technology Select Sector SPDR Fund",
        "instrument_type": "etf",
        "current_price": Decimal("198.60"),
        "allocation_regions": {"north_america": 100},
        "allocation_sectors": {"technology": 100},
        "allocation_asset_class": {"equity": 100},
    },
    {
        "symbol": "XLV",
        "name": "Health Care Select Sector SPDR Fund",
        "instrument_type": "etf",
        "current_price": Decimal("151.30"),
        "allocation_regions": {"north_america": 100},
        "allocation_sectors": {"healthcare": 100},
        "allocation_asset_class": {"equity": 100},
    },
    {
        "symbol": "LQD",
        "name": "iShares iBoxx $ Investment Grade Corporate Bond ETF",
        "instrument_type": "etf",
        "current_price": Decimal("108.40"),
        "allocation_regions": {"north_america": 80, "europe": 15, "africa": 5},
        "allocation_sectors": {"corporate": 100},
        "allocation_asset_class": {"fixed_income": 100},
    },
    {
        "symbol": "SCHD",
        "name": "Schwab US Dividend Equity ETF",
        "instrument_type": "etf",
        "current_price": Decimal("78.50"),
        "allocation_regions": {"north_america": 100},
        "allocation_sectors": {"financials": 18, "healthcare": 16, "consumer_staples": 14, "industrials": 13, "energy": 11, "technology": 10, "utilities": 8, "materials": 5, "consumer_discretionary": 4, "communication": 1},
        "allocation_asset_class": {"equity": 100},
    },
    {
        "symbol": "VXUS",
        "name": "Vanguard Total International Stock ETF",
        "instrument_type": "etf",
        "current_price": Decimal("59.80"),
        "allocation_regions": {"europe": 40, "asia": 35, "north_america": 12, "latin_america": 6, "oceania": 5, "africa": 2},
        "allocation_sectors": {"financials": 17, "industrials": 14, "technology": 12, "consumer_discretionary": 11, "healthcare": 10, "materials": 9, "consumer_staples": 9, "energy": 7, "communication": 6, "utilities": 3, "real_estate": 2},
        "allocation_asset_class": {"equity": 100},
    },
]


def seed_instruments():
    """Load instruments into DynamoDB"""
    db = Database()

    print(f"🚀 Seeding {len(INSTRUMENTS)} instruments...")
    print("=" * 60)

    success_count = 0
    for inst_data in INSTRUMENTS:
        try:
            instrument = InstrumentCreate(**inst_data)
            db.instruments.create_instrument(instrument)

            # Record initial price in history
            db.instruments.update_price(
                inst_data['symbol'],
                inst_data['current_price']
            )

            print(f"✅ {inst_data['symbol']:6s} - {inst_data['name']}")
            success_count += 1
        except Exception as e:
            print(f"❌ {inst_data['symbol']:6s} - Failed: {e}")

    print("=" * 60)
    print(f"✅ Successfully seeded {success_count}/{len(INSTRUMENTS)} instruments")

    # Verify
    instruments = db.instruments.find_all()
    print(f"\n📊 Total instruments in database: {len(instruments)}")


if __name__ == "__main__":
    seed_instruments()
