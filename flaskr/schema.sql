DROP TABLE IF EXISTS nx_stations;
DROP TABLE IF EXISTS nx_journeys;

CREATE TABLE nx_stations (
  stop_id CHAR(10) PRIMARY KEY,
  stop_name TEXT NOT NULL,
  is_origin BOOLEAN NOT NULL,
  is_destination BOOLEAN NOT NULL,
  latitude TEXT,
  longitude TEXT,
  address TEXT
  );

CREATE TABLE nx_journeys (
  journey_id CHAR(1000) PRIMARY KEY,
  departure_stop_id CHAR(10) REFERENCES nx_stations NOT NULL,
  destination_stop_id CHAR(10) REFERENCES nx_stations NOT NULL,
  fare INTEGER NOT NULL
  -- departure_time  
  -- arrival_time
);