import argparse


def run_parser() -> argparse.Namespace:
    """Initialize argparse"""

    parser = argparse.ArgumentParser(
        description="Process args to run file uploader."
    )
    parser.add_argument(
        "-p, --path", dest="path", required=True, type=str,
        help="the file path to be uploaded"
    )
    parser.add_argument(
        "--domain", dest="domain", type=str, default="localhost",
        help="the domain to be uploaded"
    )
    parser.add_argument(
        "--port", dest="port", type=int, default=8000,
        help="the port to be uploaded"
    )
    parser.add_argument(
        "--chunksize", dest="chunksize", type=int, default=10, metavar="N",
        help="the payload size"
    )

    return parser.parse_args()
