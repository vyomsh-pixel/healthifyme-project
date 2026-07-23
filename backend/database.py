"""PostgreSQL persistence for Health.io.

Keeps all data behind a PostgreSQL database so records remain scoped
to one account and writes are atomic.
"""

from __future__ import annotations

import psycopg2
import psycopg2.extras
import os
import re
from contextlib import contextmanager
from typing import Iterator


DATABASE_URL = os.getenv("DATABASE_URL")

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
        # Translate SQLite ? positional params to Postgres %s
        query = query.replace("?", "%s")
        
        # Translate SQLite :named params to Postgres %(named)s
        # Only when vars is a dict (named parameter mode)
        if isinstance(vars, dict):
            query = re.sub(r':(\w+)', r'%(\1)s', query)
        
        is_insert = query.strip().upper().startswith("INSERT")
        
        # Don't append RETURNING id if it's already there or if the table doesn't have an 'id' column
        # Profiles table uses 'user_id' as PK, sessions table uses 'token_hash'
        if is_insert and "RETURNING ID" not in query.upper() and "into profiles" not in query.lower() and "into sessions" not in query.lower():
            query += " RETURNING id"

        cursor = self.conn.cursor()
        cursor.execute(query, vars)

        lastrowid = None
        if is_insert and "RETURNING ID" in query.upper():
            row = cursor.fetchone()
            if row and 'id' in row:
                lastrowid = row['id']
                
        return CursorWrapper(cursor, lastrowid)

    def executescript(self, query: str):
        cursor = self.conn.cursor()
        cursor.execute(query)
        return cursor

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()


def get_connection():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    # psycopg2 does not support the '?pgbouncer=true' query parameter
    # which is often included in Supabase connection strings.
    clean_url = DATABASE_URL.replace("?pgbouncer=true", "")
    
    connection = psycopg2.connect(clean_url, cursor_factory=psycopg2.extras.RealDictCursor)
    return PostgresConnectionWrapper(connection)


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
                id SERIAL PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                display_name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
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
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                record_type TEXT NOT NULL,
                payload TEXT NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_health_records_user_type_date
              ON health_records(user_id, record_type, created_at DESC);

            CREATE TABLE IF NOT EXISTS meal_plans (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                goal TEXT NOT NULL, diet_type TEXT NOT NULL, budget REAL,
                meals_per_day INTEGER NOT NULL, extra_instructions TEXT,
                plan_text TEXT NOT NULL, created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS workouts (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                goal TEXT NOT NULL, level TEXT NOT NULL, location TEXT NOT NULL,
                duration_minutes INTEGER NOT NULL, total_calories REAL NOT NULL DEFAULT 0,
                exercises TEXT NOT NULL, completed_at TIMESTAMP WITH TIME ZONE,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS chat_messages (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                content TEXT NOT NULL, created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS daily_checkins (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                checkin_date TEXT NOT NULL, sleep_hours REAL, steps INTEGER,
                water_glasses INTEGER, mood INTEGER, energy INTEGER, soreness INTEGER,
                note TEXT, created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, checkin_date)
            );
            """
        )
