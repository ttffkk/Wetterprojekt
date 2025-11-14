import psycopg
import os
import csv
import pandas as pd
import io

class Database:
    def __init__(self, db_config, na_value, file_encoding):
        self.db_config = db_config
        self.conn = None
        self.na_value = na_value
        self.file_encoding = file_encoding

    def create_connection(self):
        """ create a database connection to the PostgreSQL database
            specified by db_config
        """
        try:
            self.conn = psycopg.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                dbname=self.db_config['dbname']
            )
        except psycopg.Error as e:
            print(f"Database connection error: {e}")
            raise

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
            with self.conn.cursor() as cur:
                print("Executing SQL script...")
                cur.execute(sql_script)
            self.conn.commit()
            print("Tables created successfully.")
        except psycopg.Error as e:
            print(f"Database error: {e}")
        except FileNotFoundError:
            print(f"Error: SQL file not found at {sql_file_path}")

    def get_all_stations(self):
        """Query all rows in the Station table"""
        with self.conn.cursor() as cur:
            cur.execute("SELECT Station_ID, geoBreite, geoLaenge, Stationsname FROM Station")
            rows = cur.fetchall()
            return rows

    def get_all_parameters(self):
        """Query all rows in the Parameter table"""
        with self.conn.cursor() as cur:
            cur.execute("SELECT Parameter_Name, Parameter_Description, Unit FROM Parameter")
            rows = cur.fetchall()
            return rows

    def get_weather_data(self, station_id: int, date: str):
        """
        Query weather data for a specific station and date.
        """
        with self.conn.cursor() as cur:
            date_formated = date.replace("-", "")
            cur.execute("SELECT * FROM Measurement WHERE Station_ID = %s AND MESS_DATUM = %s", (station_id, date_formated))
            row = cur.fetchone()
            if row:
                columns = [description[0] for description in cur.description]
                return dict(zip(columns, row))
            return None

    def get_monthly_weather_data(self, station_id: int, year: int, month: int):
        """
        Query weather data for a specific station, year, and month.
        """
        with self.conn.cursor() as cur:
            date_pattern = f'{year}{month:02d}%'
            cur.execute("SELECT * FROM Measurement WHERE Station_ID = %s AND MESS_DATUM LIKE %s", (station_id, date_pattern))
            rows = cur.fetchall()
            if rows:
                columns = [description[0] for description in cur.description]
                return [dict(zip(columns, row)) for row in rows]
            return []

    def get_yearly_weather_data(self, station_id: int, year: int):
        """
        Query weather data for a specific station and year.
        """
        with self.conn.cursor() as cur:
            date_pattern = f'{year}%'
            cur.execute("SELECT * FROM Measurement WHERE Station_ID = %s AND MESS_DATUM LIKE %s", (station_id, date_pattern))
            rows = cur.fetchall()
            if rows:
                columns = [description[0] for description in cur.description]
                return [dict(zip(columns, row)) for row in rows]
            return []

    def insert_csv(self, csv_filepath, delimiter):
        """
        Reads data from a given CSV file path and inserts it into the
        'Station' or 'Measurement' table.
        """
        try:
            with open(csv_filepath, 'r', encoding=self.file_encoding) as f:
                header = [h.strip() for h in f.readline().split(delimiter)]

            if 'MESS_DATUM' in header and 'STATIONS_ID' in header:
                table_name = 'measurement'
                df = pd.read_csv(csv_filepath, delimiter=delimiter, na_values=str(self.na_value), encoding=self.file_encoding)
                df.rename(columns=lambda c: c.strip(), inplace=True)
                df.rename(columns={'STATIONS_ID': 'Station_ID'}, inplace=True)

                if 'eor' in df.columns:
                    df.drop(columns=['eor'], inplace=True)

                if 'RSKF' in df.columns:
                    df['RSKF'] = pd.to_numeric(df['RSKF'], errors='coerce').astype('Int64')
                if 'QN_3' in df.columns:
                    df['QN_3'] = pd.to_numeric(df['QN_3'], errors='coerce').astype('Int64')
                if 'QN_4' in df.columns:
                    df['QN_4'] = pd.to_numeric(df['QN_4'], errors='coerce').astype('Int64')

                df.columns = df.columns.str.lower()
                db_cols = [col for col in df.columns if col in [
                    'station_id', 'mess_datum', 'qn_3', 'fx', 'fm', 'qn_4', 'rsk', 'rskf',
                    'sdk', 'shk_tag', 'nm', 'vpm', 'pm', 'tmk', 'upm', 'txk', 'tnk', 'tgk'
                ]]

                print(f"Columns to be inserted into {table_name}: {db_cols}")
                
                buffer = io.StringIO()
                df[db_cols].to_csv(buffer, index=False, header=False, sep='\t', na_rep='\\N')
                buffer.seek(0)

                with self.conn.cursor() as cur:
                    try:
                        print()
                        with cur.copy(f"COPY {table_name} ({','.join(db_cols)}) FROM STDIN") as copy:
                            copy.write(buffer.read())
                        self.conn.commit()
                        print(f"Data from {os.path.basename(csv_filepath)} successfully inserted into {table_name} using COPY.")
                    except Exception as e:
                        self.conn.rollback()
                        print(f"Error using COPY for {os.path.basename(csv_filepath)}: {e}")
                        print("Falling back to row-by-row insertion...")
                        self._insert_csv_row_by_row(csv_filepath, delimiter)

            elif 'Stationsname' in header:
                self._insert_csv_row_by_row(csv_filepath, delimiter)
            else:
                print(f"Error: Cannot determine table for CSV {csv_filepath}. Headers: {header}")
                return

        except FileNotFoundError:
            print(f"Error: {csv_filepath} not found.")
        except Exception as e:
            print(f"An error occurred while processing {csv_filepath}: {e}")

    def _insert_csv_row_by_row(self, csv_filepath, delimiter):
        """
        Private helper for row-by-row insertion logic.
        """
        with open(csv_filepath, 'r', encoding=self.file_encoding) as f:
            reader = csv.reader(f, delimiter=delimiter)
            header = [h.strip() for h in next(reader)]

        table_name, sql, eor_index = None, None, -1
        if 'MESS_DATUM' in header and 'STATIONS_ID' in header:
            table_name = 'Measurement'
            db_header = [col.replace('STATIONS_ID', 'Station_ID') for col in header if col != 'eor']
            columns = ', '.join(db_header)
            placeholders = ', '.join(['%s'] * len(db_header))
            sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            if 'eor' in header: eor_index = header.index('eor')
        elif 'Stationsname' in header:
            table_name = 'Station'
            columns = ', '.join(header)
            placeholders = ', '.join(['%s'] * len(header))
            sql = f"INSERT INTO Station ({columns}) VALUES ({placeholders})"
        else:
            return

        with open(csv_filepath, 'r', encoding=self.file_encoding) as f:
            reader = csv.reader(f, delimiter=delimiter)
            next(reader)  # Skip header
            with self.conn.cursor() as cur:
                for row in reader:
                    if not row: continue
                    if eor_index != -1: del row[eor_index]
                    
                    cleaned_row = [None if (field.strip() == str(self.na_value) or field.strip() == '') else field.strip() for field in row]
                    try:
                        cur.execute(sql, cleaned_row)
                    except psycopg.IntegrityError as e:
                        print(f"Skipping row due to IntegrityError: {e}")
                        self.conn.rollback()
                self.conn.commit()
            print(f"Data from {os.path.basename(csv_filepath)} successfully inserted into {table_name} (row-by-row).")

    def insert_parameters(self, file_path):
        try:
            with open(file_path, 'r', encoding=self.file_encoding) as f:
                reader = csv.reader(f, delimiter=';')
                header = [h.strip() for h in next(reader)]
                name_index = header.index('Parameter')
                description_index = header.index('Parameterbeschreibung')
                unit_index = header.index('Einheit')

            with self.conn.cursor() as cur:
                for row in reader:
                    if not row or len(row) <= max(name_index, description_index, unit_index): continue
                    
                    parameter_name = row[name_index].strip()
                    cur.execute("SELECT 1 FROM Parameter WHERE Parameter_Name = %s", (parameter_name,))
                    if cur.fetchone(): continue

                    sql = "INSERT INTO Parameter (Parameter_Name, Parameter_Description, Unit) VALUES (%s, %s, %s)"
                    try:
                        cur.execute(sql, (parameter_name, row[description_index].strip(), row[unit_index].strip()))
                    except psycopg.IntegrityError as e:
                        print(f"Skipping row due to IntegrityError: {e}")
                        self.conn.rollback()
                self.conn.commit()
            print(f"Data from {file_path} successfully inserted into Parameter.")
        except (FileNotFoundError, ValueError) as e:
            print(f"Error processing parameter file {file_path}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
