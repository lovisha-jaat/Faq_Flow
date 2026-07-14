import os
import sqlite3


def get_connection(database_path):
    """
    Create SQLite database connection.
    """

    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database(database_path):
    """
    Create database and all required tables.
    """

    # Create database folder if it doesn't exist
    os.makedirs(os.path.dirname(database_path), exist_ok=True)

    connection = get_connection(database_path)

    cursor = connection.cursor()

    # -----------------------------
    # Company Table
    # -----------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            company_name TEXT NOT NULL,

            website TEXT,

            description TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    # -----------------------------
    # User Table
    # -----------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL,

            company_id INTEGER,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(company_id)
                REFERENCES companies(id)

        )
    """)

    # -----------------------------
    # FAQ Table
    # -----------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS faqs (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            company_id INTEGER NOT NULL,

            question TEXT NOT NULL,

            answer TEXT NOT NULL,

            category TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(company_id)
                REFERENCES companies(id)

        )
    """)

    # -----------------------------
    # User Queries
    # -----------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS queries (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            company_id INTEGER,

            user_question TEXT NOT NULL,

            bot_answer TEXT,

            status TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(company_id)
                REFERENCES companies(id)

        )
    """)

    connection.commit()

    connection.close()


def execute_query(database_path, query, values=()):
    """
    Execute INSERT, UPDATE or DELETE query.
    """

    connection = get_connection(database_path)

    cursor = connection.cursor()

    cursor.execute(query, values)

    connection.commit()

    last_id = cursor.lastrowid

    connection.close()

    return last_id


def fetch_one(database_path, query, values=()):
    """
    Fetch one row.
    """

    connection = get_connection(database_path)

    cursor = connection.cursor()

    cursor.execute(query, values)

    row = cursor.fetchone()

    connection.close()

    return row


def fetch_all(database_path, query, values=()):
    """
    Fetch multiple rows.
    """

    connection = get_connection(database_path)

    cursor = connection.cursor()

    cursor.execute(query, values)

    rows = cursor.fetchall()

    connection.close()

    return rows