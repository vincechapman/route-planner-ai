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