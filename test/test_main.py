import os, sys
sys.path.append(os.path.abspath('../src'))

from toml import load
import asyncio
import pytest
from datetime import datetime, timedelta
from socket import gethostname, socket
from pickle import dumps
import asyncpg

from psql_connector import PSQLConnector
from ssl_client import SSLClient
from main import get_total_queries_in_queue, get_delay


def test_client_fetch_figures_success():
    conf = load("./creds.conf")
    db = PSQLConnector(conf["psql"])
    data = get_data(db)[gethostname()]

    delay = data["delay"]
    total_queries = data["total_queries"]
    ram_available = data["ram_available"]
    load_average = data["load_average"]
    cpu_usage = data["cpu_usage"]
    updated_at = data["updated_at"]

    assert delay >= 0
    assert total_queries >= 0
    assert ram_available > 0
    assert load_average > 0
    assert cpu_usage > 0
    assert type(updated_at) is str


def test_connect_server_success():
    try:
        data = {
            "key": "value"
        }

        conf = load("./creds.conf")
        client = SSLClient(conf["daemon"])
        client.send(data)
        client.close()
    except ConnectionRefusedError as ex:
        raise Exception(
            "Please make sure you start the server "
            "by running 'python socket_server.py'"
        ) from ex


def test_async():
    conf = load("../src/conf/creds.conf")
    db = PSQLConnector(conf["psql"])
    start = datetime.now()
    total = get_total_queries_in_queue(db)
    delay = get_delay(db)
    print("Runtime: ", str(datetime.now() - start))


# from test_main import test_async
