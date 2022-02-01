import pandas as pd
import re


def trips_parser(trips):
    """ Convert trips json as data records"""

    data = pd.DataFrame(
        [trip.dict() for trip in trips]
    )

    data['origin_coord'] = data['origin_coord']\
        .apply(lambda x: tuple(map(float, re.findall('[0-9]*\.[0-9]*', x))))

    data['destination_coord'] = data['destination_coord']\
        .apply(lambda x: tuple(map(float, re.findall('[0-9]*\.[0-9]*', x))))

    data['datetime'] = pd.to_datetime(data['datetime'])

    data = data.drop_duplicates(
        keep='first',
        subset=['origin_coord', 'destination_coord', 'datetime']
    )

    return data.to_dict(orient='records')
