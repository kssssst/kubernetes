import os
import socket

import psycopg2
from flask import Flask, jsonify, request


app = Flask(__name__)


# -----------------------------
# Configuration
# -----------------------------

DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "appdb")
DB_USER = os.getenv("DB_USER", "appuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Версия приложения передаётся при сборке Docker image.
APP_VERSION = os.getenv("APP_VERSION", "unknown")

# В Kubernetes hostname контейнера по умолчанию соответствует имени Pod.
# Если переменная POD_NAME когда-либо будет передана явно,
# используется она; иначе берётся hostname контейнера.
POD_NAME = os.getenv("POD_NAME") or socket.gethostname()


# -----------------------------
# PostgreSQL connection
# -----------------------------

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
    """Создаёт таблицу счётчика при первом обращении."""
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


# -----------------------------
# Kubernetes probes
# -----------------------------

@app.get("/healthz")
def health():
    """Liveness/startup probe: проверяет работу самого приложения."""
    return jsonify(
        status="ok",
        pod=POD_NAME,
    ), 200


@app.get("/readyz")
def ready():
    """
    Readiness probe:
    Pod считается готовым только при доступности PostgreSQL.
    """
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()

        return jsonify(
            status="ready",
            pod=POD_NAME,
        ), 200

    except Exception as exc:
        return jsonify(
            status="not-ready",
            pod=POD_NAME,
            error=str(exc),
        ), 503


# -----------------------------
# Application API
# -----------------------------

@app.get("/api/version")
def version():
    """
    Возвращает:
    - версию приложения;
    - имя Pod, который обработал запрос.

    Это позволяет подтвердить работу нескольких backend-реплик
    и балансировку запросов Kubernetes Service.
    """
    return jsonify(
        pod=POD_NAME,
        version=APP_VERSION,
    )


@app.route("/api/counter", methods=["GET", "POST"])
def counter():
    """
    GET  — возвращает текущее значение persistent counter.
    POST — увеличивает persistent counter на 1.

    Счётчик хранится в PostgreSQL, поэтому переживает
    удаление и пересоздание postgres-0.
    """
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
                        """
                        SELECT value
                        FROM counter
                        WHERE id = 1
                        """
                    )
                    value = cursor.fetchone()[0]

        return jsonify(
            value=value,
            version=APP_VERSION,
            pod=POD_NAME,
        )

    except Exception as exc:
        return jsonify(
            error=str(exc),
            pod=POD_NAME,
            version=APP_VERSION,
        ), 500
