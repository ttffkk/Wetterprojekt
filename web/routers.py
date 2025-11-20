from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Dict, Any
from datetime import date
import yaml

from backend.database import Database
from backend.analysis import Analysis
from web.models import (
    LiveWeather,
    ChartData,
)

router = APIRouter(prefix="/api")

# Dependency to get the database connection
async def get_db():
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    db_config = config['database']
    db = Database(db_config)
    await db.create_connection()
    try:
        yield db
    finally:
        await db.close_connection()

@router.get("/live_weather", response_model=LiveWeather)
async def get_live_weather_endpoint(lat: float, lon: float, db: Database = Depends(get_db)):
    analysis = Analysis(db)
    data = await analysis.get_live_weather(lat, lon)
    if data.get("error"):
        raise HTTPException(status_code=500, detail=data.get("message", "Failed to get live weather"))
    return data

@router.get("/all_stations", response_model=Dict[str, Any])
async def get_all_stations_endpoint(db: Database = Depends(get_db)):
    analysis = Analysis(db)
    stations = await analysis.get_all_stations()
    return {"status": "success", "stations": stations}

@router.get("/nearest_stations", response_model=Dict[str, Any])
async def get_nearest_stations_endpoint(lat: float, lon: float, db: Database = Depends(get_db)):
    analysis = Analysis(db)
    stations = await analysis.get_nearest_stations(lat, lon)
    return {"status": "success", "stations": stations}

@router.get("/historical_data", response_model=Dict[str, Any])
async def get_historical_data_endpoint(
    station_id: int,
    start_date: date,
    end_date: date,
    aggregation: str = Query("yearly", enum=["daily", "monthly", "yearly"]),
    db: Database = Depends(get_db)
):
    analysis = Analysis(db)
    data = await analysis.get_historical_data(station_id, start_date, end_date, aggregation)
    return {"aggregation": aggregation, "rows": data}

@router.get("/chart_data", response_model=ChartData)
async def get_chart_data_endpoint(
    station_id: int,
    start_date: date,
    end_date: date,
    metric: str = Query(..., enum=["tmk", "txk", "tnk", "rsk", "upm"]),
    aggregation: str = Query(..., enum=["daily", "monthly", "yearly"]),
    db: Database = Depends(get_db)
):
    analysis = Analysis(db)
    data = await analysis.get_chart_data(station_id, start_date, end_date, metric, aggregation)
    return data
