import logging
import pandas as pd
import requests


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger("uploader")


class Uploader:
    def __init__(self, args):
        """Instantiate uploader given argparsers args"""

        self.path = args.path
        self.chunksize = args.chunksize
        self.domain = args.domain
        self.port = args.port

    def upload(self, data) -> requests.Response:
        """Post data to the endpoint /trips"""

        try:
            response = requests.post(
                url=f"http://{self.domain}:{self.port}/trips",
                data=data,
                timeout=60,
            )
            response.raise_for_status()

        except requests.exceptions.HTTPError as err:
            raise SystemExit(err) from err

    def run(self) -> None:
        """Run the read and upload routine"""

        progress = 0
        logger.info("Uploading data")

        for chunk in pd.read_csv(self.path, chunksize=self.chunksize):
            records = chunk.to_json(orient="records")
            self.upload(records)

            progress += len(chunk)
            logger.info("Lines uploaded: %s", progress)
