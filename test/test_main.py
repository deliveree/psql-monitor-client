import os, sys
sys.path.append(os.path.abspath('../src'))

from datetime import datetime, timedelta
from psql_connector import PSQLConnector
from main import get_data
import toml


def test_client_fetch_figures_success():
    conf = toml.load("./creds.conf")
    db = PSQLConnector(conf["psql"])
    interval = timedelta(seconds=3)
    data = get_data(db)

    start = datetime.now()

    delay_time = data["delay_time"]
    total_queries = data["total_queries"]
    ram_available = data["ram_available"]
    load_average = data["load_average"]
    cpu_usage = data["cpu_usage"]

    runtime = datetime.now() - start

    assert delay_time >= 0
    assert total_queries >= 0
    assert ram_available > 0
    assert load_average > 0
    assert cpu_usage > 0

    assert runtime < timedelta(seconds=0.5)
