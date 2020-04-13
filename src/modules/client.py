from toml import load
from datetime import datetime, timedelta
from time import sleep
from socket import gethostname
from threading import Thread, active_count
import logging

from modules.psql_connector import PSQLConnector
from modules.ssl_connection import SSLConnection
from modules.resource_monitor import ResourceMonitor


class Client:
    """
    The Client that keeps sending its server's data to a central server

    '''
    Attributes
    host : str
        The name of the Client, which will be stored as key in Redis
    res_monitor : ResourceMonitor
        Responsible for retrieving resources
    shared_conn : SSLConnection[]
        The SSL connection that is used to send data to central server.
        It is put in a list to ensure that it is accessed by one thread at a
        time
    task_interval : timedelta
        The minimum interval between task sending resources
    is_open : boolean
        Whether the Client is still running
    """
    def __init__(self, conf):
        psql_conn = PSQLConnector(conf["psql"])

        self.host = conf["host"]
        self.res_monitor = ResourceMonitor(psql_conn)
        self.shared_conn = [SSLConnection(conf["daemon"], conf["path"])]
        self.task_interval = timedelta(seconds=0.05)
        self.is_open = True

    def _send_resources(self):
        for res in ResourceMonitor.res_types:
            if self.is_open:
                self._send(res)
        #         thread = Thread(
        #             target=self._send,
        #             args=(res,),
        #             name=res
        #         )
        #         threads.append(thread)
        #         thread.start()
        #         sleep(self.task_interval.total_seconds())

        # for thread in threads:
        #     thread.join(thread_timeout)
        #     if thread.is_alive():
        #         logging.error("Timeout for getting " + str(thread.name))

    def _gen_payload(self, key, value):
        updated_at_key = key + "_updated_at"

        return {
            self.host: {
                key: value,
                updated_at_key: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }

    def _send(self, res_type):
        res = self.res_monitor.get_resource(res_type)
        payload = self._gen_payload(res_type, res)

        while self.is_open:
            if self.shared_conn:
                conn = self.shared_conn.pop()

                try:
                    conn.send(payload)
                    self.shared_conn.append(conn)
                    logging.info("Sent " + str(payload))
                except BrokenPipeError as e:
                    logging.error(e)
                    self.shared_conn.append(conn)
                    self.close()
                return

    def start(self):
        try:
            while self.is_open:
                self._send_resources()
        except Exception as ex:
            logging.error(ex)
            self.close()
            raise

    def close(self):
        self.is_open = False
        while True:
            if self.shared_conn:
                self.shared_conn[0].close()
                break

        logging.info("Closed connection")
