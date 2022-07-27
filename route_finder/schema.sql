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
  journey_id CHAR(1000) PRIMARY KEY,
  departure_stop_id CHAR(10) REFERENCES nx_stations NOT NULL,
  destination_stop_id CHAR(10) REFERENCES nx_stations NOT NULL,
  fare INTEGER NOT NULL,
  payload_hash TEXT NOT NULL UNIQUE
  -- departure_time  
  -- arrival_time
);