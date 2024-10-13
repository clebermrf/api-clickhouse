from pydantic import BaseModel


class Trip(BaseModel):
    region: str
    origin_coord: str
    destination_coord: str
    datetime: str
    datasource: str
