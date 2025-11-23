import asyncpg
from typing import List, Dict, Any, Tuple
from datetime import date

class Database:
    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config
        self.pool = None

    async def create_connection(self):
        if not self.pool:
            self.pool = await asyncpg.create_pool(
                user=self.db_config['user'],
                password=self.db_config['password'],
                database=self.db_config['dbname'],
                host=self.db_config['host'],
                port=self.db_config['port']
            )

    async def close_connection(self):
        if self.pool:
            await self.pool.close()

    async def get_all_stations(self) -> List[Dict[str, Any]]:
        async with self.pool.acquire() as connection:
            rows = await connection.fetch("SELECT station_id, station_name, latitude, longitude, start_date, end_date FROM stations ORDER BY station_name")
            return [dict(row) for row in rows]

    async def get_stations_with_distance(self, lat: float, lon: float, limit: int = 5) -> List[Dict[str, Any]]:
        query = """
            SELECT
                station_id,
                station_name,
                latitude,
                longitude,
                start_date,
                end_date,
                (6371 * acos(
                    cos(radians($1)) * cos(radians(latitude)) *
                    cos(radians(longitude) - radians($2)) +
                    sin(radians($1)) * sin(radians(latitude))
                )) AS distance_km
            FROM stations
            ORDER BY distance_km
            LIMIT $3;
        """
        async with self.pool.acquire() as connection:
            rows = await connection.fetch(query, lat, lon, limit)
            return [dict(row) for row in rows]

    async def get_aggregated_data(self, station_id: int, start_date: date, end_date: date, aggregation: str, metrics: Dict[str, str]) -> List[Dict[str, Any]]:
        if aggregation == 'daily':
            group_by_clause = "mess_datum"
        elif aggregation == 'monthly':
            group_by_clause = "DATE_TRUNC('month', mess_datum)"
        elif aggregation == 'yearly':
            group_by_clause = "DATE_TRUNC('year', mess_datum)"
        else:
            raise ValueError("Invalid aggregation level")

        metric_selections = [f"{func} as {alias}" for alias, func in metrics.items()]
        query = f"""
            SELECT
                {group_by_clause} as period,
                {', '.join(metric_selections)}
            FROM measurements
            WHERE station_id = $1 AND mess_datum BETWEEN $2 AND $3
            GROUP BY period
            ORDER BY period;
        """
        async with self.pool.acquire() as connection:
            rows = await connection.fetch(query, station_id, start_date, end_date)
            # Format the period based on aggregation
            formatted_rows = []
            for row in rows:
                row_dict = dict(row)
                if aggregation == 'daily':
                    row_dict['period'] = row_dict['period'].strftime('%Y-%m-%d')
                elif aggregation == 'monthly':
                    row_dict['period'] = row_dict['period'].strftime('%Y-%m')
                elif aggregation == 'yearly':
                    row_dict['period'] = row_dict['period'].strftime('%Y')
                
                # Skip rows where all metric values are null
                if all(row_dict.get(alias) is None for alias in metrics.keys()):
                    continue
                
                formatted_rows.append(row_dict)
            return formatted_rows
