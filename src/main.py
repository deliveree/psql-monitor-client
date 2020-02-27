def _get_delay(db):
    query = """SELECT EXTRACT(EPOCH
                FROM (NOW() - pg_last_xact_replay_timestamp()))::INT;"""
    delay = db.query_select(query, fmt="singlevalue") or 0
    return delay


def _get_total_queries_in_queue(db):
    query = """SELECT count(*)
                FROM pg_stat_activity
                WHERE datname = 'deliveree'
                        AND state = 'active'"""
    count = db.query_select(query, fmt="singlevalue") or 0
    return count if count == 0 else count - 1


def run():
    global db
    db = 