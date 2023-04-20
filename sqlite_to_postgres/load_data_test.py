import os

import sqlite3
from contextlib import contextmanager
import psycopg2
import pytest

from load_data import load_from_sqlite


@contextmanager
def conn_context(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    yield conn

dsl = {'dbname': 'movies_database', 'user': 'app', 'password': '123qwe', 'host': '127.0.0.1', 'port': 5432}


with conn_context(os.environ.get('DB_PATH')) as sqlite_conn, psycopg2.connect(**dsl) as pg_conn:
    @pytest.mark.parametrize('sqlite_conn, pg_conn', [
        (sqlite_conn, pg_conn),
        ])
    def test_table_row_count(sqlite_conn, pg_conn):
        general_data = load_from_sqlite(sqlite_conn, pg_conn)
        for sqlite_data, pg_data in general_data:
            assert len(sqlite_data) == len(pg_data)


    @pytest.mark.parametrize('sqlite_conn, pg_conn', [
        (sqlite_conn, pg_conn),
    ])
    def test_content_in_table(sqlite_conn, pg_conn):
        general_data = load_from_sqlite(sqlite_conn, pg_conn)
        for sqlite_data, pg_data in general_data:
            for data in sqlite_data:
                assert data in pg_data

