import os
import pandas as pd

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

# ==========================================
# MYSQL SETTINGS
# ==========================================

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "sql_helper")


# DATABASE URL


DATABASE_URL = (
    f"mysql+mysqlconnector://"
    f"{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
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

        # Get all tables
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