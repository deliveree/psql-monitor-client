from os import getloadavg
from psutil import cpu_percent, virtual_memory
import asyncio


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
        # async with self.psql_conn:
        query = self._get_delay_query()
        delay = await self.psql_conn.select_single(query) or 0
        return delay

    async def _get_total_queries(self):
        # async with self.psql_conn:
        query = """SELECT count(*)
                    FROM pg_stat_activity
                    WHERE datname = 'deliveree'
                            AND state = 'active'"""
        count = await self.psql_conn.select_single(query) or 0
        if count != 0:
            count -= 1
        return count

    async def _get_load_average(self):
        return await getloadavg()[0]

    async def _get_cpu_usage(self):
        return await cpu_percent()

    async def _get_ram_available(self):
        return await virtual_memory().free / 1024

    def get_resource(self, res_types):
        switcher = {
            "delay": self.loop.run_until_complete(self._get_delay()),
            "total_queries": self.loop.run_until_complete(self._get_total_queries()),
            "load_average": self.loop.run_until_complete(self._get_load_average()),
            "cpu_usage": self.loop.run_until_complete(self._get_cpu_usage()),
            "ram_available": self.loop.run_until_complete(self._get_ram_available())
        }
        return switcher[type]()
