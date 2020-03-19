from time import sleep
from os import getloadavg
from psutil import cpu_percent, virtual_memory

DELAY = "delay"
TOTAL_QUERIES = "total_queries"
LOAD_AVERAGE = "load_average"
CPU_USAGE = "cpu_usage"
RAM_AVAILABLE = "ram_available"


class ResourceMonitor:
    def __init__(self, psql_conn):
        self.psql_conn = psql_conn

    def _get_delay_query(self):
        psql_sync_type = self.psql_conn.sync_type
        if psql_sync_type == "logical":
            query = """
                SELECT EXTRACT(EPOCH FROM
                (write_lag + flush_lag + replay_lag))::INT
                AS total_delay FROM pg_stat_replication
            """
        else:
            query = """
                SELECT EXTRACT(EPOCH
                FROM (NOW() - pg_last_xact_replay_timestamp()))::INT;
            """
        return query

    def _get_delay(self):
        query = self._get_delay_query()
        delay = self.psql_conn.select_single(query) or 0
        return delay

    def _get_total_queries(self):
        query = """SELECT count(*)
                    FROM pg_stat_activity
                    WHERE datname = 'deliveree'
                            AND state = 'active'"""
        count = self.psql_conn.select_single(query) or 0
        if count != 0:
            count -= 1
        return count

    def _get_load_average(self):
        return getloadavg()[0]

    def _get_cpu_usage(self):
        return cpu_percent()

    def _get_ram_available(self):
        return virtual_memory().free / 1024

    def get_resource(self, type):
        switcher = {
            DELAY: self._get_delay,
            TOTAL_QUERIES: self._get_total_queries,
            LOAD_AVERAGE: self._get_load_average,
            CPU_USAGE: self._get_cpu_usage,
            RAM_AVAILABLE: self._get_ram_available
        }
        return switcher[type]()
