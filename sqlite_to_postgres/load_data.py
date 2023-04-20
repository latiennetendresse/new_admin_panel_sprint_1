import dataclasses
import os
from contextlib import contextmanager

from dotenv import load_dotenv
import sqlite3
import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

from movies_dataclasses import Genre, Person, Filmwork, GenreFilmwork, PersonFilmwork

load_dotenv()


@contextmanager
def conn_context(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    yield conn  # С конструкцией yield вы познакомитесь в следующем модуле
    # Пока воспринимайте её как return, после которого код может продолжить выполняться дальше
    conn.close()


def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection):
    """Метод извлечения данных из SQLite"""

    sqlite_cursor = connection.cursor()
    # список всех таблиц из БД
    tables = ['genre', 'person', 'film_work', 'genre_film_work', 'person_film_work']
    # сопоставление датаклассов с названиями таблиц
    tablename_for_dataclasses = {'genre': Genre, 'person': Person, 'film_work': Filmwork,
                                 'genre_film_work': GenreFilmwork, 'person_film_work': PersonFilmwork}

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
            s = ['%s' for _ in range(len(columns))]
            columns_for_insert = [column[1] for column in columns]

            pg_data_for_test = insert_into_postgres(pg_conn, table, s, columns_for_insert,
                                           data_list, need_truncate)

            uploaded_rows += one_part
        sqlite_data = sqlite_cursor.execute(f'SELECT id FROM "{table}";').fetchall()
        sqlite_data_for_test = [tuple(data) for data in sqlite_data]

        yield sqlite_data_for_test, pg_data_for_test


def insert_into_postgres(pg_conn: _connection, table: str, s: list, inserted_column: list,
                         data_list: list, need_truncate: bool):
    """Метод для вставки данных в Postgres"""

    pg_cursor = pg_conn.cursor()
    if need_truncate:
        pg_cursor.execute(f'TRUNCATE content.{table} CASCADE')

    args = ','.join(pg_cursor.mogrify(f'({",".join(s)})', data)
                    .decode() for data in data_list)

    pg_cursor.execute(f'INSERT INTO content.{table} ({",".join(inserted_column)}) VALUES {args} ON CONFLICT DO NOTHING')

    pg_cursor.execute(f'SELECT id FROM content.{table};')
    pg_data_for_test = pg_cursor.fetchall()
    return pg_data_for_test


if __name__ == '__main__':
    dsl = {'dbname': 'movies_database', 'user': 'app', 'password': '123qwe', 'host': '127.0.0.1', 'port': 5432}
    with conn_context(os.environ.get('DB_PATH')) as sqlite_conn, psycopg2.connect(**dsl, cursor_factory=DictCursor) as pg_conn:
        [_ for _ in load_from_sqlite(sqlite_conn, pg_conn)]
