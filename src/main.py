from psql_connector import PSQLConnector
from datetime import datetime, timedelta
from time import sleep
from ssl_client import SSLClient
from os import getloadavg
from psutil import cpu_percent, virtual_memory
from socket import gethostname
import asyncio
import logging
from toml import load


def config_log():
    log_conf = load("conf/log.conf")
    log_path = log_conf.get("filepath", "main.log")
    logging.basicConfig(filename=log_path, level=logging.INFO)


def get_delay(psql):
    query = """SELECT EXTRACT(EPOCH
                FROM (NOW() - pg_last_xact_replay_timestamp()))::INT;"""
    delay = asyncio.run(psql.select_single(query)) or 0
    return delay


def get_total_queries_in_queue(psql):
    query = """SELECT count(*)
                FROM pg_stat_activity
                WHERE datname = 'deliveree'
                        AND state = 'active'"""
    count = asyncio.run(psql.select_single(query)) or 0
    return count if count == 0 else count - 1


def get_load_average():
    return getloadavg()[0]


def get_cpu_usage():
    return cpu_percent()


def get_ram_available():
    return virtual_memory().free / 1024


def get_data(psql):
    client_host = gethostname()

    return {
        client_host: {
            "delay": get_delay(psql),
            "total_queries": get_total_queries_in_queue(psql),
            "load_average": get_load_average(),
            "ram_available": get_ram_available(),
            "cpu_usage": get_cpu_usage(),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    }


def wait(interval, start_time):
    remain = (interval - (datetime.now() - start_time)).total_seconds()
    if remain > 0:
        sleep(remain)


def run():
    config_log()
    conf = load("conf/creds.conf")
    psql = PSQLConnector(conf["psql"])
    client = SSLClient(conf["daemon"])
    interval = timedelta(seconds=3)

    try:
        while True:
            start_time = datetime.now()
            client.send(get_data(psql))
            wait(interval, start_time)
    except Exception as ex:
        logging.error(ex)
        raise
    finally:
        client.close()


if __name__ == "__main__":
    run()
