DROP TABLE IF EXISTS nx_stations;
DROP TABLE IF EXISTS nx_journeys;

CREATE TABLE nx_stations (
  id CHAR(10) PRIMARY KEY,
  is_origin BOOLEAN NOT NULL,
  is_destination BOOLEAN NOT NULL
);

CREATE TABLE nx_journeys (
  id CHAR(100) PRIMARY KEY,
  destination CHAR(100) NOT NULL
);
