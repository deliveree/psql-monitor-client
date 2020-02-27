import psql_creds as cred


class PSQLConnector():
    def __init__(self):
        self.conn = self.connect()

    def connect(self):
        conn = connect(
            database=cred.database,
            user=cred.database,
            password=cred.password,
        )

        print('Successfully connected with local PSQL')
        return conn

    def _query_select_execute(self, query):
        cur = self.conn.cursor()
        cur.execute(query)
        values = cur.fetchall()
        return values[0][0]

    def query_select(self, query):
        try:
            return self._query_select_execute(query)
        except InterfaceError as e:
            if "connection already closed" in str(e).lower():
                self.conn = self.connect()
                return self.query_select_execute(query)
            else:
                raise

    def close(self):
        self.conn.close()
