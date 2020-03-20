import os, sys
sys.path.append(os.path.abspath('../src'))

from toml import load
import pytest
from datetime import datetime, timedelta
from time import sleep
from socket import gethostname, socket
from pickle import dumps
import logging
from multiprocessing import Process

from modules.client import Client
from test_server import TestServer
from resource_monitor ResourceMonitor


def run_client():
    client = Client()
    client.start()


def run_server(server):
    server.start()


def test_connect_server_success():
    try:
        server = TestServer()
        server_proc = Process(
            target=run_server, daemon=True, args=(server,)
        )
        server_proc.start()
        client_proc = Process(target=run_client, daemon=True)
        client_proc.start()
        sleep(1)

        server.close()
        server_proc.terminate()
        client_proc.terminate()

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
        if client_proc.is_alive():
            client_proc.terminate()
