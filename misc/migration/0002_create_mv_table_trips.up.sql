CREATE TABLE IF NOT EXISTS trips (
    datasource String,
    datetime DateTime32,
    origin_coord Point,
    destination_coord Point,
    region String
)
ENGINE = MergeTree
ORDER BY (datasource, region, datetime);

CREATE MATERIALIZED VIEW trips_mv TO trips AS
SELECT
    datasource,
    toDateTime(datetime) AS datetime,
    readWKTPoint(origin_coord) AS origin_coord,
    readWKTPoint(destination_coord) AS destination_coord,
    region
FROM 
    trips_raw;

INSERT INTO trips
SELECT
    datasource,
    toDateTime(datetime) AS datetime,
    readWKTPoint(origin_coord) AS origin_coord,
    readWKTPoint(destination_coord) AS destination_coord,
    region
FROM 
    trips_raw;
