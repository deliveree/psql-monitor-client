from psql_connector import PSQLConnector
from datetime import datetime
from os import getloadavg
import psutil


DELAY_KEY = 'delay'
TOTAL_QUERIES_KEY = 'total_queries'
LOAD_AVERAGE_KEY = 'load_average'
RAM_AVAILABLE_KEY = 'ram_available'
LAST_UPDATED_KEY = 'last_updated'


def _get_delay(db):
    query = """SELECT EXTRACT(EPOCH
                FROM (NOW() - pg_last_xact_replay_timestamp()))::INT;"""
    delay = db.query_select(query, fmt="singlevalue") or 0
    return delay


def _get_total_queries_in_queue():
    query = """SELECT count(*)
                FROM pg_stat_activity
                WHERE datname = 'deliveree'
                        AND state = 'active'"""
    count = db.query_select(query, fmt="singlevalue") or 0
    return count if count == 0 else count - 1


def _get_load_average():
    return os.getloadavg()[0]

def _get_cpu_usage():


def _get_ram_available():
    return psutil.virtual_memory().free / 1024



def run():
    global db
    db = PSQLConnector()

    while True:
        db_name = "dw-1"

        data = {
            db_name: {
                "delay": _get_delay(),
                "total_queries": _get_total_queries_in_queue(),
                "load_average":
                "ram_available":
                "cpu_usage":,
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
