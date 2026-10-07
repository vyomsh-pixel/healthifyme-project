"""Persistence for Health.io.

Uses PostgreSQL when DATABASE_URL is configured and falls back to SQLite for
local development so the API can start without extra infrastructure.
"""

from __future__ import annotations

import os
import re
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import psycopg2
import psycopg2.extras


class CursorWrapper:
    def __init__(self, cursor, lastrowid=None):
        self.cursor = cursor
        self.lastrowid = lastrowid

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    @property
    def rowcount(self):
        return self.cursor.rowcount


class PostgresConnectionWrapper:
    def __init__(self, conn):
        self.conn = conn

    def execute(self, query: str, vars=None):
        if isinstance(vars, dict):
            query = re.sub(r'(?<!:):(\w+)', r'%(\1)s', query)
        else:
            query = query.replace("?", "%s")

        query = query.replace("datetime('now')", "CURRENT_TIMESTAMP")

        is_insert = query.strip().upper().startswith("INSERT")
        q_lower = query.lower()
        needs_returning_id = (
            is_insert
            and "returning" not in q_lower
            and "into profiles" not in q_lower
            and "into sessions" not in q_lower
            and "into rate_limits" not in q_lower
            and "into daily_checkins" not in q_lower
        )
        if needs_returning_id:
            query += " RETURNING id"

        cursor = self.conn.cursor()
        cursor.execute(query, vars)

        lastrowid = None
        if is_insert and "RETURNING" in query.upper():
            try:
                row = cursor.fetchone()
                if row:
                    if isinstance(row, dict) and "id" in row:
                        lastrowid = row["id"]
                    elif hasattr(row, "__getitem__"):
                        lastrowid = row[0] if isinstance(row, (tuple, list)) else getattr(row, "id", None)
            except Exception:
                pass

        return CursorWrapper(cursor, lastrowid)

    def executescript(self, query: str):
        statements = [stmt.strip() for stmt in query.split(";") if stmt.strip()]
        cursor = self.conn.cursor()
        for stmt in statements:
            pg_sql = stmt.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
            pg_sql = pg_sql.replace("AUTOINCREMENT", "")
            pg_sql = pg_sql.replace("datetime('now')", "CURRENT_TIMESTAMP")
            cursor.execute(pg_sql)
        self.conn.commit()
        return cursor

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()


class SQLiteConnectionWrapper:
    def __init__(self, conn):
        self.conn = conn
        self.conn.row_factory = sqlite3.Row

    def _prepare_query(self, query: str) -> str:
        return re.sub(r"\bSERIAL\b", "INTEGER", query)

    def execute(self, query: str, vars=None):
        cursor = self.conn.cursor()
        if vars is None:
            cursor.execute(self._prepare_query(query))
        else:
            cursor.execute(self._prepare_query(query), vars)
        return CursorWrapper(cursor, cursor.lastrowid)

    def executescript(self, query: str):
        cursor = self.conn.cursor()
        cursor.executescript(self._prepare_query(query))
        return cursor

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()


def get_connection():
    database_url = (
        os.getenv("DATABASE_URL")
        or os.getenv("SUPABASE_DB_URL")
        or os.getenv("POSTGRES_URL")
        or os.getenv("POSTGRES_PRISMA_URL")
        or ""
    ).strip()
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    if database_url.startswith("sqlite"):
        db_path = database_url.removeprefix("sqlite:///")
        db_path = db_path.replace("/", "\\") if os.name == "nt" else db_path
        connection = sqlite3.connect(db_path, timeout=10.0)
        try:
            connection.execute("PRAGMA journal_mode=WAL;")
            connection.execute("PRAGMA busy_timeout=5000;")
        except Exception:
            pass
        return SQLiteConnectionWrapper(connection)

    if database_url:
        parts = urlsplit(database_url)
        params = [(k, v) for k, v in parse_qsl(parts.query) if k != "pgbouncer"]
        clean_url = urlunsplit(parts._replace(query=urlencode(params)))
        conn_kwargs = {
            "cursor_factory": psycopg2.extras.RealDictCursor,
            "connect_timeout": 10,
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 5,
        }
        if "sslmode" not in clean_url:
            conn_kwargs["sslmode"] = "require"
        connection = psycopg2.connect(clean_url, **conn_kwargs)
        return PostgresConnectionWrapper(connection)

    sqlite_path = os.getenv("SQLITE_DB_PATH")
    if not sqlite_path:
        if os.getenv("VERCEL") or os.getenv("VERCEL_ENV"):
            sqlite_path = "/tmp/healthio.sqlite3"
        else:
            sqlite_path = str(Path(__file__).resolve().parent.parent / "healthio.sqlite3")
    sqlite_path = Path(sqlite_path)
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(sqlite_path, timeout=10.0)
    try:
        connection.execute("PRAGMA journal_mode=WAL;")
        connection.execute("PRAGMA busy_timeout=5000;")
    except Exception:
        pass
    return SQLiteConnectionWrapper(connection)


@contextmanager
def database():
    connection = get_connection()
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialise_database() -> None:
    with database() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                display_name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                google_id TEXT,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS sessions (
                token_hash TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS profiles (
                user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                age INTEGER, gender TEXT, height_cm REAL, weight_kg REAL,
                goal TEXT, activity_level TEXT, diet_preference TEXT,
                bio TEXT, updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS health_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                record_type TEXT NOT NULL,
                payload TEXT NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_health_records_user_type_date
              ON health_records(user_id, record_type, created_at DESC);

            CREATE TABLE IF NOT EXISTS meal_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                goal TEXT NOT NULL, diet_type TEXT NOT NULL, budget REAL,
                meals_per_day INTEGER NOT NULL, extra_instructions TEXT,
                plan_text TEXT NOT NULL, created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                goal TEXT NOT NULL, level TEXT NOT NULL, location TEXT NOT NULL,
                duration_minutes INTEGER NOT NULL, total_calories REAL NOT NULL DEFAULT 0,
                exercises TEXT NOT NULL, completed_at TIMESTAMP WITH TIME ZONE,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                content TEXT NOT NULL, created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS daily_checkins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                checkin_date TEXT NOT NULL, sleep_hours REAL, steps INTEGER,
                water_glasses INTEGER, mood INTEGER, energy INTEGER, soreness INTEGER,
                note TEXT, created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, checkin_date)
            );

            CREATE TABLE IF NOT EXISTS rate_limits (
                key TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                window_start TIMESTAMP WITH TIME ZONE NOT NULL,
                count INTEGER NOT NULL DEFAULT 1,
                PRIMARY KEY (key, endpoint, window_start)
            );
            """
        )
        try:
            connection.execute("SELECT google_id FROM users LIMIT 1")
        except Exception:
            if hasattr(connection, 'conn') and hasattr(connection.conn, 'rollback'):
                connection.conn.rollback()
            try:
                connection.execute("ALTER TABLE users ADD COLUMN google_id TEXT")
            except Exception:
                pass
        try:
            connection.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id) WHERE google_id IS NOT NULL")
        except Exception:
            pass
        connection.execute("DELETE FROM sessions WHERE expires_at < CURRENT_TIMESTAMP")
