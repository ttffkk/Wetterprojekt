from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

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
