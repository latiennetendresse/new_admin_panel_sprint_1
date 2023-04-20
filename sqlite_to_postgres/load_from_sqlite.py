import dataclasses
import os
import sqlite3
from contextlib import contextmanager

from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

from movies_admin.config.settings import dsl
from movies_dataclasses import Genre, Person, Filmwork, GenreFilmwork, PersonFilmwork
from sqlite_to_postgres.save_to_postgres import insert_into_postgres

load_dotenv()


@contextmanager
def conn_context(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection):
    """Метод извлечения данных из SQLite"""

    sqlite_cursor = connection.cursor()
    # список всех таблиц из БД
    tables = ['genre', 'person', 'film_work', 'genre_film_work', 'person_film_work']
    # сопоставление датаклассов с названиями таблиц
    tablename_for_dataclasses = {'genre': Genre, 'person': Person,
                                 'film_work': Filmwork,
                                 'genre_film_work': GenreFilmwork,
                                 'person_film_work': PersonFilmwork}

    for table in tables:
        # список столбцов в БД
        columns = sqlite_cursor.execute(f'pragma table_info("{table}");').fetchall()

        sqlite_data_for_upload = sqlite_cursor.execute(f'SELECT * FROM "{table}";').fetchall()
        # порционирование данных
        uploaded_rows = 0
        for num in range(6):
            one_part = len(sqlite_data_for_upload) - uploaded_rows if num == 5 else len(sqlite_data_for_upload) // 5
            need_truncate = True if num == 0 else False
            part_of_data = sqlite_cursor.execute(f'SELECT * FROM "{table}" '
                                                 f'LIMIT {one_part} '
                                                 f'OFFSET {uploaded_rows};').fetchall()

            # формирование параметров для insert-запроса
            data_list = [dataclasses.astuple(tablename_for_dataclasses[f'{table}']
                                             (**data)) for data in part_of_data]
            s_parameters = ['%s' for _ in range(len(columns))]
            columns_for_insert = [column[1] for column in columns]

            pg_data_for_test = insert_into_postgres(pg_conn, table, s_parameters,
                                                    columns_for_insert,
                                                    data_list, need_truncate)

            uploaded_rows += one_part
        sqlite_data = sqlite_cursor.execute(f'SELECT id FROM "{table}";').fetchall()
        sqlite_data_for_test = [tuple(data) for data in sqlite_data]

        yield sqlite_data_for_test, pg_data_for_test


if __name__ == '__main__':
    with conn_context(os.environ.get('DB_PATH')) as sqlite_conn,\
            psycopg2.connect(**dsl, cursor_factory=DictCursor) as pg_conn:
        [_ for _ in load_from_sqlite(sqlite_conn, pg_conn)]
