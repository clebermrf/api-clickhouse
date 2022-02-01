import pandas as pd
import requests
import re


class Uploader:

    def __init__(self, args):
        """ Instantiate uploader given argparsers args """

        self.path = args.path
        self.chunksize = args.chunksize
        self.domain = args.domain
        self.port = args.port


    @staticmethod
    def points_formater(data):
        """ Format actual point data for the ClickHouse point format """

        rule = '\([0-9]*\.*[0-9]+ [0-9]*\.*[0-9]+\)'
        return re.findall(rule, data)[0].replace(' ', ',')


    def upload(self, data) -> requests.Response:
        """ Post data to the endpoint /trips """

        try:
            response = requests.post(url=f'http://{self.domain}:{self.port}/trips', data=data)
            response.raise_for_status()

        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)


    def run(self) -> None:
        """ Run the read and upload routine """

        progress = 0

        for chunk in pd.read_csv(self.path, chunksize=self.chunksize):

            chunk['origin_coord'] = chunk['origin_coord'] \
                .apply(lambda x: self.points_formater(x))

            chunk['destination_coord'] = chunk['destination_coord'] \
                .apply(lambda x: self.points_formater(x))

            data = chunk.to_json(orient='records')
            self.upload(data)

            progress += len(chunk)
            print(f'Lines uploaded: {progress}', end='\r')

