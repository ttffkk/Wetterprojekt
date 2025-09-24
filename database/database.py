
import sqlite3
import os

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


