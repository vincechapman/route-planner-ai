DROP TABLE IF EXISTS nx_journeys;
DROP TABLE IF EXISTS nx_stations;

CREATE TABLE nx_stations (
  stop_id VARCHAR(10) PRIMARY KEY,
  stop_name TEXT NOT NULL,
  is_origin BOOLEAN NOT NULL,
  is_destination BOOLEAN NOT NULL,
  latitude TEXT,
  longitude TEXT,
  address TEXT,
  airport_stop BOOLEAN,
  country TEXT,
  type TEXT,
  european BOOLEAN,
  euroline BOOLEAN
  );

CREATE TABLE nx_journeys (
  journey_id VARCHAR(500) PRIMARY KEY,
  departure_stop_id VARCHAR(10) REFERENCES nx_stations NOT NULL,
  destination_stop_id VARCHAR(10) REFERENCES nx_stations NOT NULL,
  departure_date DATE NOT NULL,
  arrival_date DATE NOT NULL,
  departure_time TIME NOT NULL,
  arrival_time TIME NOT NULL,
  price REAL NOT NULL,
  extra_fees REAL,
  payload_hash TEXT NOT NULL,
  request_time TIMESTAMP NOT NULL
);