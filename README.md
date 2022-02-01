# Data Ingestion
This project aims to upload any size of data to a data warehouse. It is divided into three main parts.

## 1. App

The application was built to receive and handle requests. There is no token authentication implemented as we assume the client is on the same network as the API. However, we would like to have authentication to keep it more secure.

### Weekly average
Gets the weekly average trips given a filter. Today we can filter by region, destination coordinates and origin coordinates.
```
GET http://localhost:8080/trips/getAverage?f_region=Prague

GET http://localhost:8080/trips/getAverage?f_destination=(0.0,0.0)(100.0,100.0)

GET http://localhost:8080/trips/getAverage?f_origin=(0.0,0.0)(100.0,100.0)

```
```json
{
    "weeklyAverage": {
        "2018-17": 3.6,
        "2018-18": 2.857142857142857,
        "2018-19": 2.857142857142857,
        "2018-20": 3.857142857142857,
        "2018-21": 3.75
    }
}
```

### Register trips

It is used to record trips. It receives a JSON containing a list of trips.
```
POST http://localhost:8080/trips
```

```json
[{
    "region": "Prague",
    "origin_coord": "POINT (14.4973794438195 50.00136875782316)",
    "destination_coord": "POINT (14.4973794438195 50.00136875782316)",
    "datetime": "2018-05-28 09:03:40",
    "datasource": "funny_car"
},
{
    "region": "Prague",
    "origin_coord": "POINT (14.4973794438195 50.00136875782316)",
    "destination_coord": "POINT (14.4973794438195 50.00136875782316)",
    "datetime": "2018-05-28 09:03:40",
    "datasource": "funny_car"
}]
```


## 2. Uploader

For convenience, there is an uploader to upload any size csv from anywhere to the data api. It displays how many rows have already been loaded.

```
usage: uploader [-h] -p, --path PATH [--domain DOMAIN] [--port PORT] [--chunksize N]

Process args to run file uploader.

optional arguments:
  -h, --help       show this help message and exit
  -p, --path PATH  the file path to be uploaded
  --domain DOMAIN  the domain to be uploaded
  --port PORT      the port to be uploaded
  --chunksize N    the payload size

```
```
$ python uploader -p trips.csv
Lines uploaded: 1000
```


## 3. ClickHouse

ClickHouse is an amazing database to calculate metrics over big data. The folder is just a docker volume to hold the `trips` table. This table has the ReplacingMergeTree() engine that deduplicates data based on columns (origin_coord, destination_coord, datetime).

___

## Requirements
docker, docker-compose, python3+

## Setup

After starting docker, run docker compose on this repository.
```
$ docker-compose up
```
Containers can take a while to fully initialize. Add time later, load the data.
```
$ python uploader -p trips.csv
Lines uploaded: 1000
```
Now you may be ready to get some metrics
```
GET http://localhost:8080/trips/getAverage?f_region=Prague
```
