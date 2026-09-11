import os
import pandas as pd

import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

# ==========================================
# MYSQL SETTINGS
# ==========================================

def get_secret(name, default=""):
    """
    Get value from Streamlit Secrets when deployed.
    Otherwise use environment variable from .env.
    """
    try:
        return st.secrets.get(name, os.getenv(name, default))
    except Exception:
        return os.getenv(name, default)


DB_HOST = get_secret("DB_HOST", "localhost")
DB_PORT = get_secret("DB_PORT", "3306")
DB_USER = get_secret("DB_USER", "root")
DB_PASSWORD = get_secret("DB_PASSWORD", "")
DB_NAME = get_secret("DB_NAME", "sql_helper")


# ==========================================
# DATABASE URL
# ==========================================

DATABASE_URL = (
    f"mysql+mysqlconnector://"
    f"{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    f"?ssl_disabled=false"
)


# ==========================================
# CREATE ENGINE
# ==========================================

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)


# ==========================================
# TEST CONNECTION
# ==========================================

def test_connection():

    with engine.connect() as connection:

        result = connection.execute(
            text("SELECT DATABASE()")
        )

        database_name = result.scalar()

        return database_name


# ==========================================
# GET DATABASE SCHEMA
# ==========================================

def get_schema():

    schema_text = ""

    with engine.connect() as connection:

        tables = connection.execute(
            text("""
                SELECT TABLE_NAME
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = :db
                AND TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
            """),
            {
                "db": DB_NAME
            }
        ).fetchall()

        for table in tables:

            table_name = table[0]

            schema_text += f"\nTable: {table_name}\n"

            columns = connection.execute(
                text("""
                    SELECT
                        COLUMN_NAME,
                        DATA_TYPE,
                        COLUMN_TYPE
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = :db
                    AND TABLE_NAME = :table
                    ORDER BY ORDINAL_POSITION
                """),
                {
                    "db": DB_NAME,
                    "table": table_name
                }
            ).fetchall()

            for column in columns:

                column_name = column[0]
                data_type = column[2]

                schema_text += (
                    f"Column: {column_name} "
                    f"Type: {data_type}\n"
                )

    return schema_text


# ==========================================
# EXECUTE QUERY
# ==========================================

def execute_query(sql):

    sql = sql.strip()

    first_word = sql.split()[0].upper()

    # ======================================
    # SELECT
    # ======================================

    if first_word == "SELECT":

        with engine.connect() as connection:

            result = pd.read_sql(
                text(sql),
                connection
            )

        return result

    # ======================================
    # CREATE / INSERT / UPDATE
    # ======================================

    else:

        with engine.begin() as connection:

            result = connection.execute(
                text(sql)
            )

            return result.rowcount