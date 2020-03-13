from psql_connector import PSQLConnector
from datetime import datetime, timedelta
from time import sleep
from ssl_client import SSLClient

from socket import gethostname
from threading import Thread, active_count
import logging
from toml import load

from resource_monitor import (
    ResourceMonitor,
    DELAY, TOTAL_QUERIES, LOAD_AVERAGE, CPU_USAGE, RAM_AVAILABLE
)


def gen_payload(key, value):
    updated_at_key = key + "_updated_at"

    return {
        host: {
            key: value,
            updated_at_key: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    }


def config_log():
    log_conf = load("conf/log.conf")
    log_path = log_conf.get("filepath", "main.log")
    logging.basicConfig(filename=log_path, level=logging.INFO)


def wait(interval, start_time):
    remain = (interval - (datetime.now() - start_time)).total_seconds()
    if remain > 0:
        sleep(remain)


def send(type):
    res = res_monitor.get_resource(type)
    payload = gen_payload(type, res)
    print("Before send")
    client.send(payload)


def run():
    global psql, host, client, res_monitor

    config_log()
    conf = load("conf/creds.conf")
    psql_conn = PSQLConnector(conf["psql"])
    res_monitor = ResourceMonitor(psql_conn)
    host = conf["host"]

    client = SSLClient(conf["daemon"])
    interval = timedelta(seconds=3)
    res_types = DELAY,

    try:
        while True:
            threads = []
            start_time = datetime.now()
            print("Active thread:", active_count())

            for res in res_types:
                threads.append(Thread(target=send, args=(res,)))

            for thread in threads:
                thread.start()

            wait(interval, start_time)
    except Exception as ex:
        logging.error(ex)
        raise
    finally:
        client.close()


if __name__ == "__main__":
    run()
