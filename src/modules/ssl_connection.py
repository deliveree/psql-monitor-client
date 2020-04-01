import ssl
from json import dumps
from socket import socket
import logging


class SSLConnection:
    def __init__(self, daemon_conf, path_conf):
        try:
            conn = self._get_ssl_context(path_conf).wrap_socket(
                socket(), server_hostname=daemon_conf["host"]
            )

            conn.connect((daemon_conf["host"], daemon_conf["port"]))
            self.conn = conn
        except ConnectionRefusedError as ex:
            logging.error(
                "Please make sure the server this app connects to is running"
            )
            raise ex

    @staticmethod
    def _get_ssl_context(paths):
        ssl_context = ssl.create_default_context(
            ssl.Purpose.SERVER_AUTH, cafile=paths["server_crt_path"]
        )
        ssl_context.load_cert_chain(
            paths["client_crt_path"], paths["client_key_path"]
        )
        return ssl_context

    def send(self, data):
        data = dumps(data).encode()
        self.conn.send(data)

    def close(self):
        self.conn.close()
