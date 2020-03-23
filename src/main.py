import logging
from toml import load

from modules.client import Client


def config_log():
    log_conf = load("conf/log.conf")
    log_path = log_conf.get("filepath", "main.log")
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s - %(message)s"
    )


if __name__ == "__main__":
    conf = load("conf/creds.conf")
    config_log()
    client = Client(conf)
    client.start()
