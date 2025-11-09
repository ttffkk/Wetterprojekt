import os
import pandas as pd

class StationImporter:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def import_stations(self, file_path):
        """
        Imports station data from the description file into the database.
        """
        print(f"Importing stations from {file_path}...")
        
        # Define column widths and names
        col_specs = [
            (0, 5), (6, 14), (15, 23), (24, 38), (43, 51), 
            (53, 61), (61, 102), (102, 124)
        ]
        col_names = [
            "Station_ID", "von_datum", "bis_datum", "Stattionhoehe", 
            "geoBreite", "geoLaenge", "Stationsname", "Bundesland"
        ]

        try:
            # Read the fixed-width file, skipping header rows
            df = pd.read_fwf(file_path, colspecs=col_specs, names=col_names, skiprows=2, encoding='latin-1', dtype=str)

            # The 'Abgabe' column is not well-structured, so we'll ignore it for now
            # as it's not critical for the main functionality.

            # Clean up the data
            df['Stationsname'] = df['Stationsname'].str.strip()
            df['Bundesland'] = df['Bundesland'].str.strip()
            
            # Convert data types
            df['Station_ID'] = pd.to_numeric(df['Station_ID'], errors='coerce')
            df['von_datum'] = pd.to_datetime(df['von_datum'], format='%Y%m%d').dt.strftime('%Y-%m-%d')
            df['bis_datum'] = pd.to_datetime(df['bis_datum'], format='%Y%m%d').dt.strftime('%Y-%m-%d')
            df['Stattionhoehe'] = pd.to_numeric(df['Stattionhoehe'], errors='coerce')
            df['geoBreite'] = pd.to_numeric(df['geoBreite'], errors='coerce')
            df['geoLaenge'] = pd.to_numeric(df['geoLaenge'], errors='coerce')

            # Drop rows with invalid Station_ID
            df.dropna(subset=['Station_ID'], inplace=True)
            df['Station_ID'] = df['Station_ID'].astype(int)

            # Insert data into the database
            cursor = self.db_connection.cursor()
            for _, row in df.iterrows():
                try:
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO Station (Station_ID, von_datum, bis_datum, Stattionhoehe, geoBreite, geoLaenge, Stationsname, Bundesland)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (row['Station_ID'], row['von_datum'], row['bis_datum'], row['Stattionhoehe'], row['geoBreite'], row['geoLaenge'], row['Stationsname'], row['Bundesland'])
                    )
                except Exception as e:
                    # This will catch primary key conflicts and other insertion errors
                    print(f"Skipping duplicate or invalid station {row['Station_ID']}: {e}")
            
            self.db_connection.commit()
            print(f"Successfully imported {len(df)} stations.")

        except FileNotFoundError:
            print(f"Error: Station description file not found at {file_path}")
        except Exception as e:
            print(f"An error occurred during station import: {e}")
