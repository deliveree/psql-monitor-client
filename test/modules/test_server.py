import ssl
from socket import socket
from json import loads


class TestServer:
    def __init__(self):
        self.writer = open("test.log", "w")
        self.server = self._get_ssl().wrap_socket(
            socket(), server_hostname="localhost"
        )
        self.server.bind(("localhost", 1191))

    def _get_ssl(self):
        ssl_context = ssl.create_default_context(
            ssl.Purpose.CLIENT_AUTH, cafile="creds/server.crt"
        )
        ssl_context.load_cert_chain(
            'creds/server.crt', 'creds/server.key'
        )
        ssl_context.load_verify_locations(cafile="creds/client_certs.crt")
        return ssl_context

    def start(self):
        self.server.listen()
        conn, addr = self.server.accept()

        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(2048)
                data = str(loads(data))
                print(data)
                self.writer.write(data + '\n')
                self.writer.flush()

    def close(self):
        self.writer.close()
        self.server.close()
