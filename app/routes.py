import json
import random
import asyncio
from typing import List, Optional
import logging
import re

from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from aiokafka import AIOKafkaProducer
from aiokafka.helpers import create_ssl_context
import clickhouse_connect

from app.models import Trip
from credentials.config import (
    CLICKHOUSE_HOST,
    CLICKHOUSE_USER,
    CLICKHOUSE_PASSWORD,
    KAFKA_SERVER,
    KAFKA_SSL_PASSWORD,
)

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("uploader")
router = APIRouter()
loop = asyncio.get_event_loop()

SSL_CONTEXT = create_ssl_context(
    cafile="credentials/ca.pem",
    certfile="credentials/service.cert",
    keyfile="credentials/service.key",
)


@router.get("/")
def read_root():
    return {"Hello": "World"}


ssl_context = create_ssl_context(
    cafile="credentials/ca.pem",
    certfile="credentials/service.cert",
    keyfile="credentials/service.key",
    password=KAFKA_SSL_PASSWORD,
)


@router.post("/trips")
async def send_trips(trips: List[Trip]) -> None:
    kafka_producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_SERVER,
        security_protocol="SSL",
        ssl_context=ssl_context,
    )

    await kafka_producer.start()
    batch = kafka_producer.create_batch()

    for trip in trips:
        message = json.dumps(jsonable_encoder(trip)).encode("utf-8")
        metadata = batch.append(key=None, value=message, timestamp=None)

        if metadata is None:
            partitions = await kafka_producer.partitions_for("trips")
            partition = random.choice(tuple(partitions))
            await kafka_producer.send_batch(batch, "trips", partition=partition)
            batch = kafka_producer.create_batch()

    partitions = await kafka_producer.partitions_for("trips")
    partition = random.choice(tuple(partitions))

    await kafka_producer.send_batch(batch, "trips", partition=partition)
    await kafka_producer.stop()


@router.get("/trips/getAverage")
async def get_average(
    f_origin: Optional[str] = None,
    f_destination: Optional[str] = None,
    f_region: Optional[str] = None,
):
    clickhouse_client = clickhouse_connect.get_client(
        host=CLICKHOUSE_HOST,
        user=CLICKHOUSE_USER,
        password=CLICKHOUSE_PASSWORD,
        secure=True,
        database="challenge",
    )

    rules = ["1 = 1"]
    if f_origin:
        a, b, x, y = re.findall(r"[0-9]*\.[0-9]*", f_origin)
        rules.append(
            f"pointInPolygon(origin_coord, [({a}, {b}), ({x}, {b}), ({x}, {y}), ({a}, {y})])"
        )

    if f_destination:
        a, b, x, y = re.findall(r"[0-9]*\.[0-9]*", f_destination)
        rules.append(
            f"pointInPolygon(destination_coord, [({a}, {b}), ({x}, {b}), ({x}, {y}), ({a}, {y})])"
        )

    if f_region:
        rules.append(f"region = '{f_region}'")

    query = f"""
        WITH counts AS (
            SELECT
                toDate(datetime) AS date,
                count() AS qnt
            FROM
                trips
            WHERE
                {(' AND ').join(rules)}
            GROUP BY
                date
        )

        SELECT
            toStartOfWeek(toDateTime(date), 1) AS week,
            round(ifNotFinite(avg(qnt), 0), 2) AS average
        FROM
            counts
        GROUP BY
            week
        ORDER BY
            week
    """

    result = clickhouse_client.query(query)
    return {"weeklyAverage": dict(result.result_rows)}


@router.get("/trips/getCommonAreas")
async def get_common_areas(
    f_origin: Optional[str] = None,
    f_destination: Optional[str] = None,
    f_region: Optional[str] = None,
):
    clickhouse_client = clickhouse_connect.get_client(
        host=CLICKHOUSE_HOST,
        user=CLICKHOUSE_USER,
        password=CLICKHOUSE_PASSWORD,
        secure=True,
        database="challenge",
    )

    rules = ["1 = 1"]
    if f_origin:
        a, b, x, y = re.findall(r"[0-9]*\.[0-9]*", f_origin)
        rules.append(
            f"pointInPolygon(origin_coord, [({a}, {b}), ({x}, {b}), ({x}, {y}), ({a}, {y})])"
        )

    if f_destination:
        a, b, x, y = re.findall(r"[0-9]*\.[0-9]*", f_destination)
        rules.append(
            f"pointInPolygon(destination_coord, [({a}, {b}), ({x}, {b}), ({x}, {y}), ({a}, {y})])"
        )

    if f_region:
        rules.append(f"region = '{f_region}'")

    query = f"""
        SELECT
            region,
            concat(
                trunc(origin_coord.1, 1), '-',
                trunc(origin_coord.2, 1)
            ) AS origin_area,
            concat(
                trunc(destination_coord.1, 1), '-',
                trunc(destination_coord.2, 1)
            ) AS destination_area,
            count() AS trips
        FROM 
            trips
        WHERE
            {(' AND ').join(rules)}
        GROUP BY
            region,
            origin_area,
            destination_area
        ORDER BY
            trips DESC
    """

    result = clickhouse_client.query_df(query)
    return {"commonAreas": result.to_dict(orient='records')}
