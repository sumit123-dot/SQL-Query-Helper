import os
from dotenv import load_dotenv
from google import genai

# LOAD ENVIRONMENT VARIABLES

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found in .env"
    )

# GEMINI CLIENT

client = genai.Client(
    api_key=API_KEY
)



# MODEL

MODEL_NAME = "gemini-3.6-flash"

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

# GENERATE SQL


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
8. If the requested table does not currently
   exist, you may create it.
9. Do NOT replace a requested new table with
   an existing table such as sales or employee.
10. Preserve the table name requested by the user.
11. For INSERT, use INSERT INTO.
12. For SELECT, use SELECT.
13. JOIN tables when the user's request requires
    multiple tables.
14. Never generate DROP DATABASE.
15. Never generate DROP TABLE.
16. Never generate TRUNCATE.
17. Never generate GRANT.
18. Never generate REVOKE.
19. Never generate CREATE USER.
20. Never generate ALTER USER.

Generate the SQL now.
"""

    print()
    print("Sending request to Gemini...")
    print("Model:", MODEL_NAME)

    try:

        chat = client.chats.create(
            model=MODEL_NAME
        )

        response = chat.send_message(    #Natural Language Understanding
            prompt
        )

        sql = response.text.strip()

        # CLEAN RESPONSE
        
        sql = sql.replace("```sql", "")
        sql = sql.replace("```SQL", "")
        sql = sql.replace("```", "")
        sql = sql.strip()

        # REMOVE EXTRA TEXT
    
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