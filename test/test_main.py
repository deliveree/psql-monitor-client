from datetime import datetime, timedelta
from src.main import run

def test_client_fetch_figures():
    start = datetime.now()

    run()
    delay_time = None
    total_queries = None
    ram_available = None
    load_average = None
    cpu_usage = None

    runtime = datetime.now() - start

    assert type(delay_time) is int
    assert type(total_queries) is int
    assert type(ram_available) is int
    assert type(load_average) is int
    assert type(cpu_usage) is int

    assert runtime < timedelta(seconds=0.5)
