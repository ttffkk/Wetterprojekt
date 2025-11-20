CREATE TABLE IF NOT EXISTS stations (
    station_id INT PRIMARY KEY,
    start_date DATE,
    end_date DATE,
    altitude REAL,
    latitude REAL,
    longitude REAL,
    station_name TEXT,
    state TEXT
);

CREATE TABLE IF NOT EXISTS measurements (
    measurement_id SERIAL PRIMARY KEY,
    station_id INTEGER,
    mess_datum DATE,
    qn_3 INTEGER,
    fx REAL,
    fm REAL,
    qn_4 INTEGER,
    rsk REAL,
    rskf INTEGER,
    sdk REAL,
    shk_tag REAL,
    nm REAL,
    vpm REAL,
    pm REAL,
    tmk REAL,
    upm REAL,
    txk REAL,
    tnk REAL,
    tgk REAL,
    FOREIGN KEY (station_id) REFERENCES stations(station_id)
);
