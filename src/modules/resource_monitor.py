from os import getloadavg
from psutil import cpu_percent, virtual_memory
import asyncio
import logging


class ResourceMonitor:
    res_types = [
        "delay", "total_queries", "load_average", "cpu_usage", "ram_available"
    ]

    def __init__(self, psql_conn):
        self.psql_conn = psql_conn
        self.loop = asyncio.get_event_loop()

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
        value = self.loop.run_until_complete(
            self.psql_conn.select_single(query))
        if value is None:
            return -1
        return value

    def _get_total_queries(self):
        query = """SELECT count(*)
                    FROM pg_stat_activity
                    WHERE datname = 'deliveree'
                            AND state = 'active'"""

        count = self.loop.run_until_complete(
            self.psql_conn.select_single(query) or 0)
        if count != 0:
            count -= 1
        return count

    @staticmethod
    def _get_load_average():
        return getloadavg()[0]

    @staticmethod
    def _get_cpu_usage():
        return cpu_percent()

    @staticmethod
    def _get_ram_available():
        return virtual_memory().free / 1024

    def get_resource(self, type):
        switcher = {
            "delay": self._get_delay,
            "total_queries": self._get_total_queries,
            "load_average": self._get_load_average,
            "cpu_usage": self._get_cpu_usage,
            "ram_available": self._get_ram_available
        }
        return switcher[type]()
