CREATE TABLE Station

(

Station_ID INT PRIMARY KEY,

von_datum DATE,

bis_datum DATE,

Stattionhoehe INTEGER, 
geoBreite REAL,

geoLaenge REAL,

Stationsname TEXT,

Bundesland TEXT,

Abgabe TEXT

);

 

CREATE TABLE Measurement

(

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

);