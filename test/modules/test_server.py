import ssl
from socket import socket
from json import loads


class TestServer:
    def __init__(self):
        self.writer = open("output.log", "w")
        self.server = self._get_ssl().wrap_socket(
            socket(), server_hostname="localhost"
        )
        self.server.bind(("localhost", 1191))

    def _get_ssl(self):
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        ssl_context.load_cert_chain(
            '/home/hungtran/Working/Deliveree/psql-monitoring/psql-monitor-client/test/creds/server.crt', 
            '/home/hungtran/Working/Deliveree/psql-monitoring/psql-monitor-client/test/creds/server.key'
        )
        ssl_context.load_verify_locations(cafile="/home/hungtran/Working/Deliveree/psql-monitoring/psql-monitor-client/test/creds/client_certs.crt")
        return ssl_context

    def start(self):
        self.server.listen()
        conn, addr = self.server.accept()

        with conn:
            print('Connected by', addr)

            try:
                while True:
                    data = conn.recv(2048)
                    data = str(loads(data))
                    self.writer.write(data + '\n')
                    self.writer.flush()
            except ConnectionResetError as ex:
                print(ex)

    def close(self):
        self.writer.close()
        self.server.close()

server = TestServer()
server.start()
