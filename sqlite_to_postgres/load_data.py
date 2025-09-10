import logging
import os
import sqlite3

import psycopg2
from dotenv import load_dotenv

from sqlite_to_postgres.movies_dataclasses import movies_dcs, SQLDataClass

load_dotenv()
logging.basicConfig(level=logging.INFO)


def load_from_sqlite(connection: sqlite3.Connection, pg_connection):
    """
    Основной метод загрузки данных из SQLite в Postgres
    Args:
        connection: соединение SQLite для чтения данных
        pg_connection: соединение Postgres для записи данных
    """
    logging.info("Старт переноса данных из SQLite в Postgres")
    cursor = connection.cursor()
    pg_cursor = pg_connection.cursor()
    for dc in movies_dcs:
        empty_dc: SQLDataClass = dc([], [])
        logging.info(f"Таблица {empty_dc.get_table_name()}")
        try:
            cursor.execute(empty_dc.get_select_query())
            column_names = [desc[0] for desc in cursor.description]
            insert_query = empty_dc.get_insert_query()
            while rows:= cursor.fetchmany():
                dc_data = [dc(column_names, row).get_data() for row in rows]
                pg_cursor.executemany(insert_query, dc_data)

        except sqlite3.Error as e:
            logging.error(f"Ошибка чтения из SQLite: {e}")
        except psycopg2.Error as er:
            logging.error(f"Ошибка записи данных: {er}")
            pg_connection.rollback()
            return
        pg_connection.commit()
    logging.info("Копирование завершено")



if __name__ == '__main__':
    postgres_dsl = {'dbname': os.environ.get('DB_NAME'),
           'user': os.environ.get('DB_USER'), 
           'password': os.environ.get('DB_PASSWORD'), 
           'host': os.environ.get('DB_HOST'), 
           'port': os.environ.get('DB_PORT')}
    with sqlite3.connect('db.sqlite') as conn, psycopg2.connect(
            **postgres_dsl
    ) as pg_conn:
        load_from_sqlite(conn, pg_conn)
