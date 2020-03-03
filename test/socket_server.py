import ssl
from socket import socket
from pickle import loads


def run_server():
    ssl_context = ssl.create_default_context(
        ssl.Purpose.CLIENT_AUTH, cafile="server.crt"
    )
    ssl_context.load_cert_chain('server.crt', 'server.key')
    ssl_context.load_verify_locations(cafile="client_certs.crt")
    server = ssl_context.wrap_socket(socket(), server_hostname="localhost")
    server.bind(("localhost", 1191))

    try:
        server.listen()
        conn, addr = server.accept()

        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(2048)
                print("Receive " + str(loads(data)))
    except Exception as e:
        raise
    finally:
        server.close()


run_server()
