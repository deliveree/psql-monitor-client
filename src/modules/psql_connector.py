from asyncpg import connect, InterfaceError, create_pool
import logging
import asyncio


class PSQLConnector():
    def __init__(self, conf):
        loop = asyncio.get_event_loop()
        self.conn = loop.run_until_complete(self._connect(conf))
        self.sync_type = conf["sync_type"]
        self.conf = conf

    @staticmethod
    async def _connect(conf):
        conn = await connect(
            database=conf["database"],
            user=conf["user"],
            password=conf["password"],
            host=conf.get("host", "localhost"),
            port=conf.get("port", 5432)
        )

        logging.info('Successfully connected with local PSQL')
        return conn

    async def _select_single_execute(self, query):
        async with create_pool(
            database=self.conf["database"],
            user=self.conf["user"],
            password=self.conf["password"],
            host=self.conf.get("host", "localhost"),
            port=self.conf.get("port", 5432)
        ) as self.pool:
            async with self.pool.acquire() as con:
                value = await con.fetch(query)
                return value[0][0]

    async def select_single(self, query):
        try:
            return await self._select_single_execute(query)
        except InterfaceError as e:
            if "connection already closed" in str(e).lower():
                self.conn = self.connect()
                return await self._select_single_execute(query)
            else:
                raise

    def close(self):
        self.conn.close()
