from toml import load
from datetime import datetime, timedelta
from time import sleep
from socket import gethostname
from threading import Thread, active_count
import logging

from psql_connector import PSQLConnector
from ssl_connection import SSLConnection
from resource_monitor import (
    ResourceMonitor,
    DELAY, TOTAL_QUERIES, LOAD_AVERAGE, CPU_USAGE, RAM_AVAILABLE
)


class Client():
    def __init__(self):
        conf = load("conf/creds.conf")
        psql_conn = PSQLConnector(conf["psql"])

        self.host = conf["host"]
        self.res_monitor = ResourceMonitor(psql_conn)
        self.shared_conn = [SSLConnection(conf["daemon"])]
        self.interval = timedelta(seconds=1)
        self.res_types = (
            DELAY, TOTAL_QUERIES, LOAD_AVERAGE, CPU_USAGE, RAM_AVAILABLE
        )

    def _send_resources(self):
        threads = []
        start_time = datetime.now()
        thread_timeout = 0.05

        for res in self.res_types:
            thread = Thread(
                target=self._send,
                args=(res,),
                name=res
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join(thread_timeout)
            if thread.is_alive():
                logging.error("Timeout for getting " + str(thread.name))

        self._wait(self.interval, start_time)

    def _gen_payload(self, key, value):
        updated_at_key = key + "_updated_at"

        return {
            self.host: {
                key: value,
                updated_at_key: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }

    def _wait(self, interval, start_time):
        remain = (interval - (datetime.now() - start_time)).total_seconds()
        if remain > 0:
            sleep(remain)

    def _send(self, res_type):
        res = self.res_monitor.get_resource(res_type)
        payload = self._gen_payload(res_type, res)

        while True:
            if self.shared_conn:
                conn = self.shared_conn.pop()
                conn.send(payload)
                self.shared_conn.append(conn)
                logging.info("Sent " + str(payload))
                return

    def start(self):
        try:
            while True:
                self._send_resources()
        except Exception as ex:
            logging.error(ex)
            raise
        finally:
            while True:
                if self.shared_conn:
                    self.shared_conn[0].close()
