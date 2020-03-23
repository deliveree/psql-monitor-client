import os, sys
sys.path.append(os.path.abspath('../src'))

from time import sleep
from toml import load
from multiprocessing import Process

from modules.client import Client
from modules.test_server import TestServer
from modules.resource_monitor import ResourceMonitor


def run_server(server):
    server.start()


def test_connect_server_success():
    try:
        server = TestServer()
        server_proc = Process(
            target=run_server, daemon=True, args=(server,)
        )
        server_proc.start()
        conf = load("conf/creds.conf")
        client = Client(conf)
        client.start()
        sleep(1)

        client.close()
        server.close()
        server_proc.terminate()

        with open("test.log") as f:
            log = f.read().splitlines()

        assert len(log) == 5
        for res in (
            ResourceMonitor.res_types
        ):
            assert res in str(log)
    except KeyboardInterrupt as ex:
        pass
    finally:
        if server_proc.is_alive():
            server_proc.terminate()
