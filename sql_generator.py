import os
import streamlit as st
from dotenv import load_dotenv
from google import genai

# ==========================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()


def get_secret(name, default=""):
    """
    Get value from Streamlit Secrets when deployed.
    Otherwise use .env / environment variable.
    """
    try:
        return st.secrets.get(name, os.getenv(name, default))
    except Exception:
        return os.getenv(name, default)


# ==========================================
# GEMINI API KEY
# ==========================================

API_KEY = get_secret("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found."
    )


# ==========================================
# GEMINI CLIENT
# ==========================================

client = genai.Client(
    api_key=API_KEY
)


# ==========================================
# MODEL
# ==========================================

MODEL_NAME = "gemini-3.6-flash"


# ==========================================
# DETECT OPERATION
# ==========================================

def detect_operation(question):

    q = question.strip().lower()

    if q.startswith("create"):
        return "CREATE"

    if q.startswith("insert"):
        return "INSERT"

    if q.startswith("select"):
        return "SELECT"

    if "create table" in q:
        return "CREATE"

    if "insert into" in q:
        return "INSERT"

    if any(word in q for word in [
        "show",
        "display",
        "list",
        "find",
        "get",
        "fetch",
        "total",
        "average",
        "count"
    ]):
        return "SELECT"

    return "SELECT"


# ==========================================
# GENERATE SQL
# ==========================================

def generate_sql(question, schema):

    operation = detect_operation(question)

    prompt = f"""
You are an expert MySQL SQL developer.

Your task is to convert a natural-language request
into ONE valid MySQL SQL statement.

CURRENT DATABASE SCHEMA:

{schema}

USER REQUEST:

{question}

DETECTED OPERATION:

{operation}

IMPORTANT RULES:

1. Return ONLY SQL.
2. Do not use markdown.
3. Do not use ```sql.
4. Do not explain anything.
5. Do not generate multiple SQL statements.
6. Use MySQL syntax.
7. If the user asks to CREATE a new table,
   generate CREATE TABLE.
8. Every CREATE TABLE statement MUST contain
   a PRIMARY KEY.
9. For a new table, if the user does not specify
   a primary key, create an ID column such as:
   id INT AUTO_INCREMENT PRIMARY KEY.
10. If the requested table does not currently
    exist, create the requested table.
11. Do NOT replace a requested new table with
    an existing table such as sales or employee.
12. Preserve the table name requested by the user.
13. For INSERT, use INSERT INTO.
14. For SELECT, use SELECT.
15. JOIN tables when the user's request requires
    multiple tables.
16. Use the exact table and column names from the
    CURRENT DATABASE SCHEMA whenever possible.
17. Never invent column names when the required
    column exists in the schema.
18. Never generate DROP DATABASE.
19. Never generate DROP TABLE.
20. Never generate TRUNCATE.
21. Never generate GRANT.
22. Never generate REVOKE.
23. Never generate CREATE USER.
24. Never generate ALTER USER.

Generate the SQL now.
"""

    print()
    print("Sending request to Gemini...")
    print("Model:", MODEL_NAME)

    try:

        chat = client.chats.create(
            model=MODEL_NAME
        )

        response = chat.send_message(
            prompt
        )

        sql = response.text.strip()

        # ======================================
        # CLEAN RESPONSE
        # ======================================

        sql = sql.replace("```sql", "")
        sql = sql.replace("```SQL", "")
        sql = sql.replace("```", "")
        sql = sql.strip()

        # ======================================
        # REMOVE EXTRA SQL STATEMENTS
        # ======================================

        if ";" in sql:

            statements = [
                x.strip()
                for x in sql.split(";")
                if x.strip()
            ]

            sql = statements[0]

            if not sql.endswith(";"):
                sql += ";"

        print()
        print("Gemini response received successfully.")

        return sql

    except Exception as e:

        print()
        print("Gemini generation error:")
        print(e)

        raise