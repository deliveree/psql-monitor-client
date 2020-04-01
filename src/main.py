import logging

from modules.client import Client
from modules.utils import load_conf


def config_log(log_conf):
    log_path = log_conf["filepath"]
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s - %(message)s"
    )


if __name__ == "__main__":
    conf = load_conf()
    config_log(conf["log"])
    client = Client(conf)

    try:
        client.start()
    except KeyboardInterrupt:
        client.close()
        logging.info("Client is shut down by KeyboardInterrupt")
