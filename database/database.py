import sqlite3
import os
import csv

class Database:
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = None

    def create_connection(self):
        """ create a database connection to the SQLite database
            specified by db_file
        """
        try:
            # create data directory if it doesn't exist
            db_dir = os.path.dirname(self.db_file)
            if not os.path.exists(db_dir):
                os.makedirs(db_dir)
            self.conn = sqlite3.connect(self.db_file)
        except sqlite3.Error as e:
            print(e)

    def close_connection(self):
        """ close the database connection """
        if self.conn:
            self.conn.close()

    def create_tables(self):
        
        """ create tables from the create_table_sql statement """
        sql_create_station_table = """ CREATE TABLE IF NOT EXISTS Station (
                                            Station_ID INT PRIMARY KEY,
                                            von_datum DATE,
                                            bis_datum DATE,
                                            Stattionhoehe INTEGER,
                                            geoBreite REAL,
                                            geoLaenge REAL,
                                            Stationsname TEXT,
                                            Bundesland TEXT,
                                            Abgabe TEXT
                                        ); """

        sql_create_measurement_table = """CREATE TABLE IF NOT EXISTS Measurement (
                                        m_ID INTEGER PRIMARY KEY,
                                        Station_ID INTEGER,
                                        MESS_DATUM DATE,
                                        QN_3 INTEGER,
                                        FX REAL,
                                        FM REAL,
                                        QN_4 INTEGER,
                                        RSK REAL,
                                        RSKF INTEGER,
                                        SDK REAL,
                                        SHK_TAG REAL,
                                        NM REAL,
                                        VPM REAL,
                                        PM REAL,
                                        TMK REAL,
                                        UPM REAL,
                                        TXK REAL,
                                        TNK REAL,
                                        TGK REAL,
                                        FOREIGN KEY (Station_ID) REFERENCES Station(Station_ID)
                                    );"""
        try:
            c = self.conn.cursor()
            c.execute(sql_create_station_table)
            c.execute(sql_create_measurement_table)
        except sqlite3.Error as e:
            print(e)

    def insert_csv(self, csv_filepath):
        """
        Reads data from a given CSV file path and inserts it into the
        'Station' or 'Measurement' table. It determines the target table by
        inspecting the CSV header.
        """
        try:
            with open(csv_filepath, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=';')
                header = [h.strip() for h in next(reader)]

            # Determine table based on headers
            if 'MESS_DATUM' in header and 'STATIONS_ID' in header:
                table_name = 'Measurement'
                
                # Prepare header and SQL for Measurement data
                # Map STATIONS_ID to Station_ID
                db_header = [col if col != 'STATIONS_ID' else 'Station_ID' for col in header]
                
                # Filter out the 'eor' column if it exists
                eor_index = -1
                if 'eor' in db_header:
                    eor_index = db_header.index('eor')
                    del db_header[eor_index]

                columns = ', '.join(db_header)
                placeholders = ', '.join(['?'] * len(db_header))
                sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

                with open(csv_filepath, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f, delimiter=';')
                    next(reader)  # Skip header

                    c = self.conn.cursor()
                    for row in reader:
                        if not row: continue # Skip empty rows
                        
                        # Remove 'eor' value from row if exists
                        if eor_index != -1:
                            del row[eor_index]

                        # Clean row and handle -999 values
                        cleaned_row = []
                        for field in row:
                            cleaned_field = field.strip()
                            if cleaned_field == '-999' or cleaned_field == '':
                                cleaned_row.append(None)
                            else:
                                cleaned_row.append(cleaned_field)
                        
                        try:
                            c.execute(sql, cleaned_row)
                        except sqlite3.IntegrityError as e:
                            print(f"Skipping row due to IntegrityError: {e}")
                    self.conn.commit()
                    print(f"Data from {csv_filepath} successfully inserted into {table_name}.")

            elif 'Stationsname' in header:
                # Existing logic for station files
                table_name = 'Station'
                sql = f"INSERT INTO Station ({', '.join(header)}) VALUES ({', '.join(['?'] * len(header))})"
                with open(csv_filepath, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f, delimiter=';')
                    next(reader)  # Skip header
                    c = self.conn.cursor()
                    for row in reader:
                        cleaned_row = [field.strip() for field in row]
                        for i, field in enumerate(cleaned_row):
                            if field == '': cleaned_row[i] = None
                        try:
                            c.execute(sql, cleaned_row)
                        except sqlite3.IntegrityError as e:
                            print(f"Skipping row due to IntegrityError: {e}")
                    self.conn.commit()
                    print(f"Data from {csv_filepath} successfully inserted into {table_name}.")
            else:
                print(f"Error: Cannot determine table for CSV {csv_filepath}. Headers: {header}")
                return

        except FileNotFoundError:
            print(f"Error: {csv_filepath} not found.")
        except Exception as e:
            print(f"An error occurred while processing {csv_filepath}: {e}")