import psycopg
import os
import csv
import pandas as pd
import io
import time

class Database:
    def __init__(self, db_config, na_value, file_encoding, logger):
        self.db_config = db_config
        self.conn = None
        self.na_value = na_value
        self.file_encoding = file_encoding
        self.logger = logger

    def create_connection(self):
        """ create a database connection to the PostgreSQL database
            specified by db_config
        """
        retries = 10
        delay = 10
        for i in range(retries):
            try:
                # Fallback to environment variables if not in config
                host = self.db_config.get('host') or os.environ.get('DB_HOST')
                port = self.db_config.get('port') or os.environ.get('DB_PORT')
                user = self.db_config.get('user') or os.environ.get('DB_USER')
                password = self.db_config.get('password') or os.environ.get('DB_PASSWORD')
                dbname = self.db_config.get('dbname') or os.environ.get('DB_NAME')

                self.conn = psycopg.connect(
                    host=host,
                    port=port,
                    user=user,
                    password=password,
                    dbname=dbname
                )
                self.logger.info("Database connection established.")
                return # connection successful
            except psycopg.OperationalError as e:
                if "the database system is starting up" in str(e) and i < retries - 1:
                    self.logger.warning(f"Database is starting up. Retrying in {delay} seconds... ({i+1}/{retries})")
                    time.sleep(delay)
                else:
                    self.logger.error(f"Database connection error: {e}")
                    raise
        # If loop finishes without connecting
        self.logger.error("Could not connect to the database after several retries.")
        raise psycopg.OperationalError("Could not connect to the database.")

    def close_connection(self):
        """ close the database connection """
        if self.conn:
            self.conn.close()

    def create_tables(self, sql_file_path):
        """ create tables from a .sql file """
        try:
            self.logger.info(f"Attempting to read SQL file from {sql_file_path}...")
            with open(sql_file_path, 'r') as sql_file:
                sql_script = sql_file.read()
            self.logger.info("SQL file read successfully.")
            with self.conn.cursor() as cur:
                self.logger.info("Executing SQL script...")
                cur.execute(sql_script)
            self.conn.commit()
            self.logger.info("Tables created successfully.")
        except psycopg.Error as e:
            self.logger.error(f"Database error: {e}")
        except FileNotFoundError:
            self.logger.error(f"Error: SQL file not found at {sql_file_path}")

    def insert_csv(self, csv_filepath, delimiter):
        """
        Reads data from a given CSV file path and inserts it into the
        'measurements' table.
        """
        try:
            with open(csv_filepath, 'r', encoding=self.file_encoding) as f:
                header = [h.strip() for h in f.readline().split(delimiter)]

            if 'MESS_DATUM' in header and 'STATIONS_ID' in header:
                table_name = 'measurements'
                df = pd.read_csv(csv_filepath, delimiter=delimiter, na_values=str(self.na_value), encoding=self.file_encoding)
                df.rename(columns=lambda c: c.strip(), inplace=True)
                df.rename(columns={'STATIONS_ID': 'station_id'}, inplace=True)

                if 'eor' in df.columns:
                    df.drop(columns=['eor'], inplace=True)

                # Ensure correct types for specific columns before insertion
                for col in ['RSKF', 'QN_3', 'QN_4']:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
                
                df['MESS_DATUM'] = pd.to_datetime(df['MESS_DATUM'], format='%Y%m%d').dt.strftime('%Y-%m-%d')


                df.columns = df.columns.str.lower()
                db_cols = [col for col in df.columns if col in [
                    'station_id', 'mess_datum', 'qn_3', 'fx', 'fm', 'qn_4', 'rsk', 'rskf',
                    'sdk', 'shk_tag', 'nm', 'vpm', 'pm', 'tmk', 'upm', 'txk', 'tnk', 'tgk'
                ]]

                self.logger.info(f"Columns to be inserted into {table_name}: {db_cols}")
                
                buffer = io.StringIO()
                df[db_cols].to_csv(buffer, index=False, header=False, sep='\t', na_rep='\\N')
                buffer.seek(0)

                with self.conn.cursor() as cur:
                    try:
                        self.logger.info(f"Using COPY to insert data from {os.path.basename(csv_filepath)} into {table_name}.")
                        with cur.copy(f"COPY {table_name} ({','.join(db_cols)}) FROM STDIN") as copy:
                            copy.write(buffer.read())
                        self.conn.commit()
                        self.logger.info(f"Data from {os.path.basename(csv_filepath)} successfully inserted into {table_name} using COPY.")
                    except Exception as e:
                        self.conn.rollback()
                        self.logger.error(f"Error using COPY for {os.path.basename(csv_filepath)}: {e}")
                        self.logger.info("Falling back to row-by-row insertion...")
                        self._insert_csv_row_by_row(df, db_cols)

            else:
                self.logger.error(f"Error: Cannot determine table for CSV {csv_filepath}. Headers: {header}")
                return

        except FileNotFoundError:
            self.logger.error(f"Error: {csv_filepath} not found.")
        except Exception as e:
            self.logger.error(f"An error occurred while processing {csv_filepath}: {e}")

    def _insert_csv_row_by_row(self, df, db_cols):
        """
        Private helper for row-by-row insertion logic using the dataframe.
        """
        table_name = 'measurements'
        
        with self.conn.cursor() as cur:
            for row in df.itertuples(index=False, name=None):
                row_dict = dict(zip(df.columns, row))
                
                # Construct the insert statement dynamically
                columns = [col for col in db_cols if pd.notna(row_dict.get(col))]
                if not columns:
                    continue
                
                placeholders = ', '.join(['%s'] * len(columns))
                values = [row_dict[col] for col in columns]
                
                sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
                
                try:
                    cur.execute(sql, values)
                except psycopg.IntegrityError as e:
                    self.logger.warning(f"Skipping row due to IntegrityError: {e}")
                    self.conn.rollback()
                except psycopg.Error as e:
                    self.logger.error(f"An error occurred during row-by-row insert: {e}")
                    self.conn.rollback()
            self.conn.commit()
        self.logger.info(f"Data successfully inserted into {table_name} (row-by-row).")

