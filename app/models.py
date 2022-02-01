from datetime import datetime
from pydantic import BaseModel, validator
from datetime import datetime


class Trip(BaseModel):
    region: str
    origin_coord: str
    destination_coord: str
    datetime: str
    datasource: str