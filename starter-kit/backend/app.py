import os

import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "appdb")
DB_USER = os.getenv("DB_USER", "appuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
APP_VERSION = os.getenv("APP_VERSION", "unknown")


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        connect_timeout=3,
    )


def initialize_database():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS counter (
                    id INTEGER PRIMARY KEY,
                    value INTEGER NOT NULL
                )
                """
            )

            cursor.execute(
                """
                INSERT INTO counter (id, value)
                VALUES (1, 0)
                ON CONFLICT (id) DO NOTHING
                """
            )


@app.get("/healthz")
def health():
    return jsonify(status="ok"), 200


@app.get("/readyz")
def ready():
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()

        return jsonify(status="ready"), 200

    except Exception as exc:
        return jsonify(status="not-ready", error=str(exc)), 503


@app.get("/api/version")
def version():
    return jsonify(version=APP_VERSION)


@app.route("/api/counter", methods=["GET", "POST"])
def counter():
    try:
        initialize_database()

        with get_connection() as connection:
            with connection.cursor() as cursor:

                if request.method == "POST":
                    cursor.execute(
                        """
                        UPDATE counter
                        SET value = value + 1
                        WHERE id = 1
                        RETURNING value
                        """
                    )
                    value = cursor.fetchone()[0]

                else:
                    cursor.execute(
                        "SELECT value FROM counter WHERE id = 1"
                    )
                    value = cursor.fetchone()[0]

        return jsonify(value=value, version=APP_VERSION)

    except Exception as exc:
        return jsonify(error=str(exc)), 500
