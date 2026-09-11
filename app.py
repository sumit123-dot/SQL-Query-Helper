import streamlit as st

from database import get_schema, execute_query
from sql_generator import generate_sql
from security import validate_sql
from summary import generate_summary


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="SQL Query Helper",
    page_icon="🗄️",
    layout="wide"
)


# =========================================================
# INITIAL SESSION STATE
# =========================================================

if "sql" not in st.session_state:
    st.session_state["sql"] = ""

if "question" not in st.session_state:
    st.session_state["question"] = ""

if "query_results" not in st.session_state:
    st.session_state["query_results"] = None

if "sql_result" not in st.session_state:
    st.session_state["sql_result"] = None

if "operation" not in st.session_state:
    st.session_state["operation"] = ""

if "schema" not in st.session_state:
    st.session_state["schema"] = ""

if "summary" not in st.session_state:
    st.session_state["summary"] = ""


# =========================================================
# TITLE
# =========================================================

st.title("🗄️ SQL Query Helper")

st.write(
    "Ask questions in natural language and generate MySQL "
    "queries using Google Gemini."
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

try:

    schema = get_schema()

    st.session_state["schema"] = schema

    st.success(
        "✅ Connected to MySQL database: sql_helper"
    )

except Exception as e:

    st.error(
        f"❌ Database connection error: {e}"
    )

    st.stop()


# =========================================================
# DATABASE SCHEMA
# =========================================================

with st.expander("📋 View Database Schema"):

    st.code(
        st.session_state["schema"],
        language="text"
    )


# =========================================================
# REFRESH SCHEMA
# =========================================================

if st.button(
    "🔄 Refresh Database Schema",
    use_container_width=True,
    key="refresh_schema_button"
):

    try:

        st.session_state["schema"] = get_schema()

        st.success(
            "✅ Database schema refreshed!"
        )

        st.rerun()

    except Exception as e:

        st.error(
            f"Schema refresh error: {e}"
        )


# =========================================================
# ASK QUESTION
# =========================================================

st.header("Ask a Question")

question = st.text_area(
    "Enter your request",

    placeholder=(
        "Example 1: Show all sales\n"
        "Example 2: Show total sales by city\n"
        "Example 3: Create a table named Employee with "
       
        
    ),

    height=150,

    key="question_textarea"
)


# =========================================================
# GENERATE SQL
# =========================================================

if st.button(
    "⚡ Generate SQL",
    type="primary",
    use_container_width=True,
    key="generate_sql_button"
):

    if not question.strip():

        st.warning(
            "⚠️ Please enter a question."
        )

    else:

        try:

            with st.spinner(
                "🤖 Gemini is generating SQL..."
            ):

                sql = generate_sql(
                    question,
                    st.session_state["schema"]
                )


            # ---------------------------------------------
            # SECURITY VALIDATION
            # ---------------------------------------------

            valid, message = validate_sql(sql)

            if not valid:

                st.error(
                    f"🚫 SQL blocked: {message}"
                )

                st.stop()


            # ---------------------------------------------
            # SAVE
            # ---------------------------------------------

            st.session_state["sql"] = sql

            st.session_state["question"] = question

            # Clear previous execution information
            st.session_state["query_results"] = None

            st.session_state["sql_result"] = None

            st.session_state["operation"] = ""

            st.session_state["summary"] = ""

            st.success(
                "✅ SQL generated successfully!"
            )


        except Exception as e:

            st.error(
                f"❌ Gemini Error: {e}"
            )


# =========================================================
# SHOW GENERATED SQL
# =========================================================

if st.session_state["sql"]:

    sql = st.session_state["sql"]

    st.header("SQL Query")

    st.code(
        sql,
        language="sql"
    )


    # =====================================================
    # DETECT OPERATION
    # =====================================================

    words = sql.strip().split()

    if not words:

        first_word = ""

    else:

        first_word = words[0].upper()


    # =====================================================
    # OPERATION INFORMATION
    # =====================================================

    if first_word == "CREATE":

        st.info(
            "🛠️ This query will create or modify database structure."
        )

    elif first_word == "INSERT":

        st.info(
            "➕ This query will insert data into the database."
        )

    elif first_word == "UPDATE":

        st.warning(
            "⚠️ This query will modify existing data."
        )

    elif first_word == "DELETE":

        st.warning(
            "⚠️ This query will delete data."
        )


    # =====================================================
    # EXECUTE QUERY
    # =====================================================

    st.header("Execute Query")

    if st.button(
        "▶️ Execute Query",
        use_container_width=True,
        key="execute_query_button"
    ):

        try:

            # ---------------------------------------------
            # SECURITY CHECK
            # ---------------------------------------------

            valid, message = validate_sql(sql)

            if not valid:

                st.error(
                    f"🚫 Query blocked: {message}"
                )

                st.stop()


            # ---------------------------------------------
            # EXECUTE
            # ---------------------------------------------

            with st.spinner(
                "Executing query..."
            ):

                result = execute_query(sql)


            # =================================================
            # SAVE EXECUTION INFORMATION
            # =================================================

            st.session_state["operation"] = first_word

            st.session_state["sql_result"] = result

            # Clear old summary
            st.session_state["summary"] = ""


            # =================================================
            # SELECT
            # =================================================

            if first_word == "SELECT":

                st.success(
                    "✅ SELECT query executed successfully!"
                )

                st.session_state["query_results"] = result

                st.header("📊 Query Results")

                if result is not None and not result.empty:

                    st.dataframe(
                        result,
                        use_container_width=True
                    )

                else:

                    st.info(
                        "The query returned no records."
                    )


            # =================================================
            # CREATE TABLE
            # =================================================

            elif first_word == "CREATE":

                st.success(
                    "✅ Table created successfully!"
                )

                # Store result for summary
                st.session_state["query_results"] = None

                # Refresh schema immediately
                new_schema = get_schema()

                st.session_state["schema"] = new_schema

                st.subheader(
                    "📋 Updated Database Schema"
                )

                st.code(
                    new_schema,
                    language="text"
                )


            # =================================================
            # INSERT
            # =================================================

            elif first_word == "INSERT":

                st.success(
                    "✅ Data inserted successfully!"
                )

                # Store result for summary
                st.session_state["query_results"] = None

                st.write(
                    f"Rows affected: {result}"
                )


            # =================================================
            # UPDATE
            # =================================================

            elif first_word == "UPDATE":

                st.success(
                    "✅ Data updated successfully!"
                )

                st.session_state["query_results"] = None

                st.write(
                    f"Rows affected: {result}"
                )


            # =================================================
            # DELETE
            # =================================================

            elif first_word == "DELETE":

                st.success(
                    "✅ Data deleted successfully!"
                )

                st.session_state["query_results"] = None

                st.write(
                    f"Rows affected: {result}"
                )


            else:

                st.success(
                    "✅ Query executed successfully!"
                )

                st.session_state["query_results"] = None


        except Exception as e:

            st.error(
                f"❌ Database Error: {e}"
            )


# =========================================================
# NATURAL LANGUAGE SUMMARY
# =========================================================

if st.session_state["operation"] in [
    "CREATE",
    "INSERT",
    "SELECT"
]:

    st.header(
        "📝 Natural Language Summary"
    )

    operation = st.session_state["operation"]

    if operation == "CREATE":

        st.info(
            "Gemini will explain the table creation."
        )

    elif operation == "INSERT":

        st.info(
            "Gemini will explain the inserted data."
        )

    elif operation == "SELECT":

        st.info(
            "Gemini will explain the query results."
        )


    # =====================================================
    # SUMMARY BUTTON
    # =====================================================

    if st.button(
        "📝 Generate Natural Language Summary",
        use_container_width=True,
        key="generate_summary_button"
    ):

        try:

            results = st.session_state["sql_result"]

            sql = st.session_state["sql"]

            question = st.session_state["question"]


            with st.spinner(
                "🤖 Gemini is analyzing the query..."
            ):

                # IMPORTANT:
                # generate_summary() accepts ONLY 3 arguments
                summary = generate_summary(
                    question,
                    sql,
                    results
                )


            # Save summary
            st.session_state["summary"] = summary


            st.success(
                "✅ Summary generated successfully!"
            )

            # DO NOT DISPLAY SUMMARY HERE.
            #
            # The summary will be displayed once below.
            # This prevents duplicate output.


        except Exception as e:

            st.error(
                f"❌ Summary Error: {e}"
            )


# =========================================================
# SHOW SUMMARY ONCE
# =========================================================

if st.session_state["summary"]:

    st.markdown(
        "### 📋 Explanation"
    )

    st.write(
        st.session_state["summary"]
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "SQL Query Generator"
)