from cli import run_parser
from uploader import Uploader


if __name__ == '__main__':

    args = run_parser()

    uploader = Uploader(args)
    uploader.run()

