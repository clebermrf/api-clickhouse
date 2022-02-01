from fastapi import APIRouter
from typing import List, Optional
from models import Trip
from utils import trips_parser
from clickhouse_driver import Client
import re


router = APIRouter()


clickhouse = Client(host='clickhouse', port=9000)


@router.get("/")
def read_root():
    return {"Hello": "World"}


@router.post("/trips")
async def trips(trips: List[Trip]):

    data = trips_parser(trips)
    clickhouse.execute("INSERT INTO jobsity.trips VALUES", data)

    return trips


@router.get("/trips/getAverage")
async def get_average(
    f_origin: Optional[str] = None,
    f_destination: Optional[str] = None,
    f_region: Optional[str] = None
):

    if f_origin:
        a, b, x, y = re.findall('[0-9]*\.[0-9]*', f_origin)
        rule = f'pointInPolygon(origin_coord, [({a}, {b}), ({x}, {b}), ({x}, {y}), ({a}, {y})])'

    if f_destination:
        a, b, x, y = re.findall('[0-9]*\.[0-9]*', f_destination)
        rule = f'pointInPolygon(destination_coord, [({a}, {b}), ({x}, {b}), ({x}, {y}), ({a}, {y})])'

    if f_region:
        rule = f'region = \'{f_region}\''


    query = f"""
        SELECT concat(
            toString(toYear(day)), '-',
            toString(toWeek(day))
        ) AS week,
        ifNotFinite(avg(qnt), 0) AS average

        FROM (
            SELECT toDate(datetime) AS day,
            count() AS qnt

            FROM jobsity.trips
            WHERE {rule}
            GROUP BY day
        )

        GROUP BY week
        ORDER BY week

    """

    return {"weeklyAverage": {d: q for d, q in clickhouse.execute(query)}}
