import os
import sqlite3
from datetime import datetime

import psycopg2
import pytest
from dotenv import load_dotenv

from sqlite_to_postgres.movies_dataclasses import SQLDataClass, movies_dcs

load_dotenv()

@pytest.fixture
def postgres_connection():
    """Создаем соединение Postgres"""
    postgres_dsl = {'dbname': os.environ.get('DB_NAME'),
                    'user': os.environ.get('DB_USER'),
                    'password': os.environ.get('DB_PASSWORD'),
                    'host': os.environ.get('DB_HOST'),
                    'port': os.environ.get('DB_PORT')}
    with psycopg2.connect(**postgres_dsl) as connection:
        yield connection

@pytest.fixture
def sqlite_connection():
    """Создаем соединение SQLite"""
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "db.sqlite")
    with sqlite3.connect(db_path) as connection:
        yield connection


def get_row_count(cursor, table_name: str) -> int:
    """Helper function to get row count from a connection."""
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    return cursor.fetchone()[0]

def get_last_id(cursor, table_name: str) -> int:
    """Получаем последний идентификатор в таблице"""
    cursor.execute(f"SELECT id "
                  f"FROM {table_name} "
                  f"ORDER BY id DESC "
                  f"LIMIT 1")
    return cursor.fetchone()[0]

def test_load_from_sqlite_row_count(sqlite_connection, postgres_connection):
    """Тест совпадения количества строк в таблицах"""

    sqlite_cursor = sqlite_connection.cursor()

    # Mock the Postgres connection.  We don't actually insert data in this test
    postgres_cursor = postgres_connection.cursor()

    try:
        for dc in movies_dcs:
            empty_dc: SQLDataClass = dc([], [])
            table_name = empty_dc.get_table_name()
            sqlite_number = get_row_count(sqlite_cursor, table_name)
            postgres_number = get_row_count(postgres_cursor, f"content.{table_name}")
            print(f"{table_name}: {sqlite_number} -> {postgres_number}")
            assert sqlite_number == postgres_number
    finally:
        sqlite_cursor.close()
        postgres_cursor.close()


def test_load_from_sqlite_last_rows(sqlite_connection, postgres_connection):
    """Тест совпадения идентификаторов в таблицах"""
    sqlite_cursor = sqlite_connection.cursor()
    postgres_cursor = postgres_connection.cursor()

    try:
        for dc in movies_dcs:
            empty_dc: SQLDataClass = dc([], [])
            table_name = empty_dc.get_table_name()
            sqlite_last_row = get_last_id(sqlite_cursor, table_name)
            postgres_last_row = get_last_id(postgres_cursor, f"content.{table_name}")
            assert sqlite_last_row == postgres_last_row, f"Идентификаторы отличаются в {table_name}"
    finally:
        sqlite_cursor.close()
        postgres_cursor.close()
