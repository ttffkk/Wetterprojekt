from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

class Station(BaseModel):
    STATIONS_ID: int
    VON_DATUM: int
    BIS_DATUM: int
    GEOBREITE: float
    GEOLAENGE: float
    STATIONSNAME: str

class StationWithDistance(Station):
    distance_km: float

class LiveWeather(BaseModel):
    error: bool = False
    latitude: float
    longitude: float
    station_name: str
    temperature: float
    relative_humidity: float
    wind_speed_10m: float
    rain: float
    timestamp: datetime

class HistoricalDataRow(BaseModel):
    period: str
    value: Optional[float] = None

class ChartData(BaseModel):
    metric: str
    metric_label: str
    station_id: int
    aggregation: str
    start_date: date
    end_date: date
    rows: List[HistoricalDataRow]
