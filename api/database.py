import os

import psycopg


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "host=localhost port=5432 dbname=taskdb user=taskuser password=taskpass",
)


def get_connection():
    return psycopg.connect(DATABASE_URL)