from asyncpg import connect, InterfaceError, create_pool
import logging
import asyncio
from async_timeout import timeout


class PSQLConnector():
    def __init__(self, conf):
        loop = asyncio.get_event_loop()
        self.sync_type = conf["sync_type"]
        self.conf = conf
        self.pool = loop.run_until_complete(self._create_pool())

    async def _create_pool(self):
        pool = await create_pool(
            database=self.conf["database"],
            user=self.conf["user"],
            password=self.conf["password"],
            host=self.conf.get("host", "localhost"),
            port=self.conf.get("port", 5432),
            max_inactive_connection_lifetime=0.05,
            timeout=0.05)

        logging.info('Successfully connected with local PSQL')
        return pool

    async def _select_single_execute(self, query):
        value = await self.pool.fetch(query, timeout=0.05)
        return value[0][0]

    async def select_single(self, query):
        try:
            async with timeout(0.05):
                return await self._select_single_execute(query)
        except InterfaceError as e:
            if "connection already closed" in str(e).lower():
                self.conn = loop.run_until_complete(self._create_pool())
                async with timeout(0.05):
                    return await self._select_single_execute(query)
            else:
                raise

    def close(self):
        self.conn.close()
