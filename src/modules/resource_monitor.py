from os import getloadavg
from psutil import cpu_percent, virtual_memory
import asyncio
import logging
from async_timeout import timeout


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

    async def _get_delay(self):
        async with timeout(0.05):
            query = self._get_delay_query()
            delay = await self.psql_conn.select_single(query) or 0
            return delay

    async def _get_total_queries(self):
        query = """SELECT count(*)
                    FROM pg_stat_activity
                    WHERE datname = 'deliveree'
                            AND state = 'active'"""

        async with timeout(0.05):
            count = await self.psql_conn.select_single(query) or 0
            if count != 0:
                count -= 1
            return count

    @staticmethod
    async def _get_load_average():
        async with timeout(0.05):
            await asyncio.sleep(0.0001)
            return getloadavg()[0]

    @staticmethod
    async def _get_cpu_usage():
        async with timeout(0.05):
            await asyncio.sleep(0.05)
            return cpu_percent()

    @staticmethod
    async def _get_ram_available():
        async with timeout(0.05):
            await asyncio.sleep(0.0001)
            return virtual_memory().free / 1024

    def get_resource(self, type):
        try:
            switcher = {
                "delay": self.loop.run_until_complete(self._get_delay()),
                "total_queries": self.loop.run_until_complete(self._get_total_queries()),
                "load_average": self.loop.run_until_complete(self._get_load_average()),
                "cpu_usage": self.loop.run_until_complete(self._get_cpu_usage()),
                "ram_available": self.loop.run_until_complete(self._get_ram_available())
            }
            return switcher[type]
        except asyncio.TimeoutError as e:
            logging.error("timeout")
