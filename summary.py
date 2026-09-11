from google import genai
import os
from dotenv import load_dotenv


# ==========================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()


# ==========================================
# GET GEMINI API KEY
# ==========================================

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found in .env file"
    )


# ==========================================
# CREATE GEMINI CLIENT
# ==========================================

client = genai.Client(
    api_key=api_key
)


# ==========================================
# GENERATE NATURAL LANGUAGE SUMMARY
# ==========================================

def generate_summary(question, sql, results):

    # ==========================================
    # CONVERT RESULTS INTO TEXT
    # ==========================================

    if results is None:

        result_text = "The query executed successfully, but there are no tabular results."

    else:

        try:

            # If result is a Pandas DataFrame
            if hasattr(results, "to_string"):

                result_text = results.to_string(
                    index=False
                )

            else:

                result_text = str(results)

        except Exception:

            result_text = str(results)


    # ==========================================
    # GEMINI PROMPT
    # ==========================================

    prompt = f"""
You are a SQL data analyst.

The user asked:
{question}

The SQL query executed was:
{sql}

The query result is:
{result_text}

Provide a short and clear natural-language explanation of the result.

Instructions:

- Explain what the query did.
- Explain the important result or findings.
- Mention important numbers, cities, names, dates, or values when useful.
- If the query is a SELECT query, summarize the returned records.
- If the query is a CREATE TABLE query, explain what was created.
- If the query is an INSERT query, explain what data was inserted.
- Keep the explanation simple and easy to understand.
- Do not repeat the SQL query.
- Do not create unnecessary headings.
- Do not say "Here is the summary".
- Give only the final explanation.
"""


    # ==========================================
    # CALL GEMINI
    # ==========================================

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )


        # ==========================================
        # RETURN SUMMARY ONLY
        # ==========================================

        if response and response.text:

            return response.text.strip()

        return "No summary was generated."


    except Exception as e:

        return f"Unable to generate summary: {str(e)}"