DROP TABLE IF EXISTS Queries;
CREATE TABLE Queries (
  session_id UUID PRIMARY KEY,
  state CHAR(2),
  age SMALLINT,
  zipcode CHAR(5),
  health TEXT,
  created_queries TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'UTC')
);

DROP TABLE IF EXISTS Clicks;
CREATE TABLE Clicks (
  session_id UUID,
  plan_id TEXT,
  created_clicks TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'UTC')
);

DROP TABLE IF EXISTS Ranks;
CREATE TABLE Ranks (
  session_id UUID,
  plan_id TEXT,
  plan_score REAL,
  created_ranks TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'UTC')
);

DROP TABLE IF EXISTS ZipToCoord;
CREATE TABLE ZipToCoord (
  zipcode CHAR(5),
  lat DOUBLE PRECISION,
  lon DOUBLE PRECISION
);
