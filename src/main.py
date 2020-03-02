from psql_connector import PSQLConnector
from datetime import datetime, timedelta
from ssl_client import SSLClient
from os import getloadavg
import psutil
import toml


DELAY_KEY = 'delay'
TOTAL_QUERIES_KEY = 'total_queries'
LOAD_AVERAGE_KEY = 'load_average'
RAM_AVAILABLE_KEY = 'ram_available'
LAST_UPDATED_KEY = 'last_updated'


def _get_delay(db):
    query = """SELECT EXTRACT(EPOCH
                FROM (NOW() - pg_last_xact_replay_timestamp()))::INT;"""
    delay = db.query_select(query) or 0
    return delay


def _get_total_queries_in_queue(db):
    query = """SELECT count(*)
                FROM pg_stat_activity
                WHERE datname = 'deliveree'
                        AND state = 'active'"""
    count = db.query_select(query) or 0
    return count if count == 0 else count - 1


def _get_load_average():
    return os.getloadavg()[0]


def _get_cpu_usage():
    return psutil.cpu_percent()


def _get_ram_available():
    return psutil.virtual_memory().free / 1024


def get_data(db):
    client_host = socket.gethostname()

    return {
        client_host: {
            "delay": _get_delay(db),
            "total_queries": _get_total_queries_in_queue(db),
            "load_average": _get_load_average(),
            "ram_available": _get_ram_available(),
            "cpu_usage": _get_cpu_usage(),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    }


def wait(interval, start_time):
    remain = interval - (datetime.now() - start_time)
    if remain > 0:
        sleep(remain)


def run():
    conf = toml.load("./creds.conf")
    db = PSQLConnector(conf["psql"])
    client = SSLClient(conf["daemon"])
    interval = timedelta(seconds=3)

    try:
        while True:
            start_time = datetime.now()
            client.send(get_data(db))
            wait(interval, start_time)
    except Exception as ex:
        print(ex)
    finally:
        client.close()
