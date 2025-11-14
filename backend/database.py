import psycopg
import os
import csv
import pandas as pd
import io

class AsyncDatabase:
    def __init__(self, db_config, na_value, file_encoding):
        self.db_config = db_config
        self.conn = None
        self.na_value = na_value
        self.file_encoding = file_encoding

    async def create_connection(self):
        """ create a database connection to the PostgreSQL database
            specified by db_config
        """
        try:
            self.conn = await psycopg.AsyncConnection.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                dbname=self.db_config['dbname']
            )
        except psycopg.Error as e:
            print(f"Database connection error: {e}")
            raise

    async def close_connection(self):
        """ close the database connection """
        if self.conn:
            await self.conn.close()

    async def create_tables(self, sql_file_path):
        """ create tables from a .sql file """
        try:
            print(f"Attempting to read SQL file from {sql_file_path}...")
            with open(sql_file_path, 'r') as sql_file:
                sql_script = sql_file.read()
            print("SQL file read successfully.")
            async with self.conn.cursor() as acur:
                print("Executing SQL script...")
                await acur.execute(sql_script)
            await self.conn.commit()
            print("Tables created successfully.")
        except psycopg.Error as e:
            print(f"Database error: {e}")
        except FileNotFoundError:
            print(f"Error: SQL file not found at {sql_file_path}")

    async def get_all_stations(self):
        """Query all rows in the Station table"""
        async with self.conn.cursor() as acur:
            await acur.execute("SELECT Station_ID, geoBreite, geoLaenge, Stationsname FROM Station")
            rows = await acur.fetchall()
            return rows

    async def get_all_parameters(self):
        """Query all rows in the Parameter table"""
        async with self.conn.cursor() as acur:
            await acur.execute("SELECT Parameter_Name, Parameter_Description, Unit FROM Parameter")
            rows = await acur.fetchall()
            return rows

    async def get_weather_data(self, station_id: int, date: str):
        """
        Query weather data for a specific station and date.

        :param station_id: The ID of the station.
        :param date: The date in 'YYYY-MM-DD' format.
        :return: A dictionary containing the weather data.
        """
        async with self.conn.cursor() as acur:
            date_formated = date.replace("-", "")
            await acur.execute("SELECT * FROM Measurement WHERE Station_ID = %s AND MESS_DATUM = %s", (station_id, date_formated))
            row = await acur.fetchone()
            if row:
                # get column names from cursor description
                columns = [description[0] for description in acur.description]
                return dict(zip(columns, row))
            return None

    async def get_monthly_weather_data(self, station_id: int, year: int, month: int):
        """
        Query weather data for a specific station, year, and month.

        :param station_id: The ID of the station.
        :param year: The year.
        :param month: The month.
        :return: A list of dictionaries containing the weather data.
        """
        async with self.conn.cursor() as acur:
            date_pattern = f'{year}{month:02d}%'
            await acur.execute("SELECT * FROM Measurement WHERE Station_ID = %s AND MESS_DATUM LIKE %s", (station_id, date_pattern))
            rows = await acur.fetchall()
            if rows:
                columns = [description[0] for description in acur.description]
                return [dict(zip(columns, row)) for row in rows]
            return []

    async def get_yearly_weather_data(self, station_id: int, year: int):
        """
        Query weather data for a specific station and year.

        :param station_id: The ID of the station.
        :param year: The year.
        :return: A list of dictionaries containing the weather data.
        """
        async with self.conn.cursor() as acur:
            date_pattern = f'{year}%'
            await acur.execute("SELECT * FROM Measurement WHERE Station_ID = %s AND MESS_DATUM LIKE %s", (station_id, date_pattern))
            rows = await acur.fetchall()
            if rows:
                columns = [description[0] for description in acur.description]
                return [dict(zip(columns, row)) for row in rows]
            return []

    async def insert_csv(self, csv_filepath, delimiter):
        """
        Reads data from a given CSV file path and inserts it into the
        'Station' or 'Measurement' table. It determines the target table by
        inspecting the CSV header.
        """
        try:
            with open(csv_filepath, 'r', encoding=self.file_encoding) as f:
                header = [h.strip() for h in f.readline().split(delimiter)]

            if 'MESS_DATUM' in header and 'STATIONS_ID' in header:
                table_name = 'measurement'
                
                # Use pandas for efficient cleaning and preparation
                df = pd.read_csv(csv_filepath, delimiter=delimiter, na_values=str(self.na_value), encoding=self.file_encoding)
                df.rename(columns=lambda c: c.strip(), inplace=True)
                df.rename(columns={'STATIONS_ID': 'Station_ID'}, inplace=True)

                if 'eor' in df.columns:
                    df.drop(columns=['eor'], inplace=True)

                df.columns = df.columns.str.lower()
                db_cols = [col for col in df.columns if col in [
                    'station_id', 'mess_datum', 'qn_3', 'fx', 'fm', 'qn_4', 'rsk', 'rskf',
                    'sdk', 'shk_tag', 'nm', 'vpm', 'pm', 'tmk', 'upm', 'txk', 'tnk', 'tgk'
                ]]
                print(f"Columns for COPY: {db_cols}")
                
                buffer = io.StringIO()
                df[db_cols].to_csv(buffer, index=False, header=False, sep='\t', na_rep='\\N')
                buffer.seek(0);

                async with self.conn.cursor() as acur:
                    try:
                        async with acur.copy(f"COPY {table_name} ({','.join(db_cols)}) FROM STDIN") as copy:
                            await copy.write(buffer.read())
                        await self.conn.commit()
                        print(f"Data from {os.path.basename(csv_filepath)} successfully inserted into {table_name} using COPY.")
                    except Exception as e:
                        await self.conn.rollback()
                        print(f"Error using COPY for {os.path.basename(csv_filepath)}: {e}")
                        # Fallback to row-by-row insert for debugging or handling specific errors
                        # (You might want to remove this in production)
                        print("Falling back to row-by-row insertion...")
                        await self._insert_csv_row_by_row(csv_filepath, delimiter)


            elif 'Stationsname' in header:
                # Existing logic for station files (usually small, so row-by-row is fine)
                await self._insert_csv_row_by_row(csv_filepath, delimiter)
            else:
                print(f"Error: Cannot determine table for CSV {csv_filepath}. Headers: {header}")
                return

        except FileNotFoundError:
            print(f"Error: {csv_filepath} not found.")
        except Exception as e:
            print(f"An error occurred while processing {csv_filepath}: {e}")

    async def _insert_csv_row_by_row(self, csv_filepath, delimiter):
        """
        Private helper for original row-by-row insertion logic.
        """
        with open(csv_filepath, 'r', encoding=self.file_encoding) as f:
            reader = csv.reader(f, delimiter=delimiter)
            header = [h.strip() for h in next(reader)]

        if 'MESS_DATUM' in header and 'STATIONS_ID' in header:
            table_name = 'Measurement'
            db_header = [col if col != 'STATIONS_ID' else 'Station_ID' for col in header]
            if 'eor' in db_header:
                db_header.remove('eor')
            
            columns = ', '.join(db_header)
            placeholders = ', '.join(['%s'] * len(db_header))
            sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            
            eor_index = header.index('eor') if 'eor' in header else -1

        elif 'Stationsname' in header:
            table_name = 'Station'
            columns = ', '.join(header)
            placeholders = ', '.join(['%s'] * len(header))
            sql = f"INSERT INTO Station ({columns}) VALUES ({placeholders})"
            eor_index = -1 # No eor column in station files
        else:
            return # Already handled in public method

        with open(csv_filepath, 'r', encoding=self.file_encoding) as f:
            reader = csv.reader(f, delimiter=delimiter)
            next(reader)  # Skip header
            async with self.conn.cursor() as acur:
                for row in reader:
                    if not row: continue
                    if eor_index != -1:
                        del row[eor_index]
                    
                    cleaned_row = []
                    for field in row:
                        cleaned_field = field.strip()
                        if cleaned_field == str(self.na_value) or cleaned_field == '':
                            cleaned_row.append(None)
                        else:
                            cleaned_row.append(cleaned_field)
                    try:
                        await acur.execute(sql, cleaned_row)
                    except psycopg.IntegrityError as e:
                        print(f"Skipping row due to IntegrityError: {e}")
                        await self.conn.rollback()
                await self.conn.commit()
            print(f"Data from {os.path.basename(csv_filepath)} successfully inserted into {table_name} (row-by-row).")

    async def insert_parameters(self, file_path):
        try:
            with open(file_path, 'r', encoding=self.file_encoding) as f:
                reader = csv.reader(f, delimiter=';')
                header = [h.strip() for h in next(reader)]

                # Find the indices of the required columns
                try:
                    name_index = header.index('Parameter')
                    description_index = header.index('Parameterbeschreibung')
                    unit_index = header.index('Einheit')
                except ValueError as e:
                    print(f"Header missing in {file_path}: {e}")
                    return

                async with self.conn.cursor() as acur:
                    for row in reader:
                        if not row or len(row) <= max(name_index, description_index, unit_index):
                            continue  # Skip empty or malformed rows

                        parameter_name = row[name_index].strip()
                        parameter_description = row[description_index].strip()
                        unit = row[unit_index].strip()

                        # Check if the parameter already exists
                        await acur.execute("SELECT 1 FROM Parameter WHERE Parameter_Name = %s", (parameter_name,))
                        if await acur.fetchone():
                            continue  # Skip if parameter name already exists

                        sql = "INSERT INTO Parameter (Parameter_Name, Parameter_Description, Unit) VALUES (%s, %s, %s)"
                        try:
                            await acur.execute(sql, (parameter_name, parameter_description, unit))
                        except psycopg.IntegrityError as e:
                            print(f"Skipping row due to IntegrityError: {e}")
                            await self.conn.rollback()

                    await self.conn.commit()
                    print(f"Data from {file_path} successfully inserted into Parameter.")

        except FileNotFoundError:
            print(f"Error: {file_path} not found.")
        except Exception as e:
            print(f"An error occurred while processing {file_path}: {e}")
