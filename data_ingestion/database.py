import sqlite3
import os
import csv

class Database:
    def __init__(self, db_file, na_value, file_encoding):
        self.db_file = db_file
        self.conn = None
        self.na_value = na_value
        self.file_encoding = file_encoding

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

    def create_tables(self, sql_file_path):
        """ create tables from a .sql file """
        try:
            print(f"Attempting to read SQL file from {sql_file_path}...")
            with open(sql_file_path, 'r') as sql_file:
                sql_script = sql_file.read()
            print("SQL file read successfully.")
            c = self.conn.cursor()
            print("Executing SQL script...")
            c.executescript(sql_script)
            self.conn.commit()
            print("Tables created successfully.")
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        except FileNotFoundError:
            print(f"Error: SQL file not found at {sql_file_path}")

    def get_all_stations(self):
        """Query all rows in the Station table"""
        cur = self.conn.cursor()
        cur.execute("SELECT Station_ID, geoBreite, geoLaenge, Stationsname FROM Station")
        rows = cur.fetchall()
        return rows

    def get_weather_data(self, station_id: int, date: str):
        """
        Query weather data for a specific station and date.

        :param station_id: The ID of the station.
        :param date: The date in 'YYYY-MM-DD' format.
        :return: A dictionary containing the weather data.
        """
        cur = self.conn.cursor()
        date_formated = date.replace("-", "")
        cur.execute("SELECT * FROM Measurement WHERE Station_ID = ? AND MESS_DATUM = ?", (station_id, date_formated))
        row = cur.fetchone()
        if row:
            # get column names from cursor description
            columns = [description[0] for description in cur.description]
            return dict(zip(columns, row))
        return None

    def get_monthly_weather_data(self, station_id: int, year: int, month: int):
        """
        Query weather data for a specific station, year, and month.

        :param station_id: The ID of the station.
        :param year: The year.
        :param month: The month.
        :return: A list of dictionaries containing the weather data.
        """
        cur = self.conn.cursor()
        date_pattern = f'{year}{month:02d}%'
        cur.execute("SELECT * FROM Measurement WHERE Station_ID = ? AND MESS_DATUM LIKE ?", (station_id, date_pattern))
        rows = cur.fetchall()
        if rows:
            columns = [description[0] for description in cur.description]
            return [dict(zip(columns, row)) for row in rows]
        return []

    def insert_csv(self, csv_filepath, delimiter):
        """
        Reads data from a given CSV file path and inserts it into the
        'Station' or 'Measurement' table. It determines the target table by
        inspecting the CSV header.
        """
        try:
            with open(csv_filepath, 'r', encoding=self.file_encoding) as f:
                reader = csv.reader(f, delimiter=delimiter)
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

                with open(csv_filepath, 'r', encoding=self.file_encoding) as f:
                    reader = csv.reader(f, delimiter=delimiter)
                    next(reader)  # Skip header

                    c = self.conn.cursor()
                    for row in reader:
                        if not row: continue # Skip empty rows
                        
                        # Remove 'eor' value from row if exists
                        if eor_index != -1:
                            del row[eor_index]

                        # Clean row and handle configured na_value values
                        cleaned_row = []
                        for field in row:
                            cleaned_field = field.strip()
                            if cleaned_field == str(self.na_value) or cleaned_field == '':
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
                with open(csv_filepath, 'r', encoding=self.file_encoding) as f:
                    reader = csv.reader(f, delimiter=delimiter)
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
