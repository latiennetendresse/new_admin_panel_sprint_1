from psycopg2.extensions import connection as _connection


def insert_into_postgres(pg_conn: _connection,
                         table: str, s_parameters: list,
                         inserted_column: list,
                         data_list: list,
                         need_truncate: bool):
    """Метод для вставки данных в Postgres"""

    pg_cursor = pg_conn.cursor()
    if need_truncate:
        pg_cursor.execute(f'TRUNCATE content.{table} CASCADE')

    args = ','.join(pg_cursor.mogrify(f'({",".join(s_parameters)})', data)
                    .decode() for data in data_list)

    pg_cursor.execute(f'INSERT INTO content.{table} ({",".join(inserted_column)}) VALUES {args} ON CONFLICT DO NOTHING')

    pg_cursor.execute(f'SELECT id FROM content.{table};')
    pg_data_for_test = pg_cursor.fetchall()
    return pg_data_for_test
