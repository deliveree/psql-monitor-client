from psycopg2 import connect, InterfaceError


class PSQLConnector():
    def __init__(self, conf):
        self.conn = self._connect(conf)
        self.sync_type = conf["sync_type"]

    def _connect(self, conf):
        conn = connect(
            database=conf["database"],
            user=conf["user"],
            password=conf["password"],
        )

        print('Successfully connected with local PSQL')
        return conn

    async def select_single(self, query):
        try:
            return self.conn.fetch(query)
        except InterfaceError as e:
            if "connection already closed" in str(e).lower():
                self.conn = self.connect()
                return self._select_single_execute(query)
            else:
                raise

    def close(self):
        self.conn.close()
