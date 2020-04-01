import os, sys
sys.path.append(os.path.abspath('../src'))

from time import sleep
from multiprocessing import Process
import logging

from modules.utils import load_conf
from modules.client import Client
from modules.test_server import TestServer
from modules.resource_monitor import ResourceMonitor


logging.basicConfig(
    filename="./test_main.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

def run_server(server):
    server.start()


def run_client(client):
    client.start()


def test_connect_server_success():
    try:
        server = TestServer()
        server_proc = Process(
            target=run_server, daemon=True, args=(server,)
        )
        server_proc.start()

        conf = load_conf("./conf")
        client = Client(conf)
        client_proc = Process(
            target=run_client, daemon=True, args=(client,)
        )
        client_proc.start()

        sleep(0.5)

        client.close()
        server.close()
        client_proc.terminate()
        server_proc.terminate()

        with open("output.log") as f:
            log = f.read().splitlines()

        for res in (
            ResourceMonitor.res_types
        ):
            assert res in str(log)
    except KeyboardInterrupt as ex:
        if server_proc.is_alive():
            server_proc.terminate()
        if client_proc.is_alive():
            client_proc.terminate()