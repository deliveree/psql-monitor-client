import ssl
from pickle import dumps
from socket import socket
import logging


class SSLConnection:
    def __init__(self, conf):
        conn = self._get_ssl_context().wrap_socket(
            socket(), server_hostname=conf["host"]
        )

        conn.connect((conf["host"], conf["port"]))
        self.conn = conn

    def _get_ssl_context(self):
        ssl_context = ssl.create_default_context(
            ssl.Purpose.SERVER_AUTH, cafile="server.crt"
        )
        ssl_context.load_cert_chain('client.crt', 'client.key')
        return ssl_context

    def send(self, data):
        data = dumps(data)
        self.conn.send(data)

    def close(self):
        self.conn.close()
