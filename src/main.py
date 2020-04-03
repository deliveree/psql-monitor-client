import logging
import argparse

from modules.client import Client
from modules.utils import load_conf


parser = argparse.ArgumentParser()
parser.add_argument(
    "--loglevel", "-l", type=str, default="ERROR",
    help="The log level (default: ERROR)"
)
parser.add_argument(
    "--logfile", "-f", type=str,
    help="The path to logfile (default: None)"
)

if __name__ == "__main__":
    args = parser.parse_args()
    loglevel = args.loglevel
    logfile = args.logfile

    logging.basicConfig(
        filename=logfile,
        level=loglevel,
        format="%(asctime)s - %(message)s"
    )

    conf = load_conf()
    client = Client(conf)

    try:
        client.start()
    except KeyboardInterrupt:
        client.close()
        logging.info("Client is shut down by KeyboardInterrupt")
