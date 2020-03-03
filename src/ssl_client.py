import ssl
from pickle import dumps
from socket import socket


class SSLClient:
    def __init__(self, conf):
        client = self._get_ssl_context().wrap_socket(
            socket(), server_hostname=conf["host"]
        )

        client.connect((conf["host"], conf["port"]))
        self.client = client

    def _get_ssl_context(self):
        ssl_context = ssl.create_default_context(
            ssl.Purpose.SERVER_AUTH, cafile="server.crt"
        )
        ssl_context.load_cert_chain('client.crt', 'client.key')
        return ssl_context

    def send(self, data):
        self.client.send(dumps(data))

    def close(self):
        self.client.close()
