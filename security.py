import re
# SQL SECURITY VALIDATION
def validate_sql(sql):

    if not sql or not sql.strip():

        return False, "SQL query is empty."
    query = sql.strip()
    upper_query = query.upper()
    # REMOVE COMMENTS FOR SECURITY CHECK

    check_query = re.sub(
        r"--.*?$",
        "",
        query,
        flags=re.MULTILINE
    )
    check_query = re.sub(
        r"/\*.*?\*/",
        "",
        check_query,
        flags=re.DOTALL
    )
    check_query = check_query.strip()
    upper_query = check_query.upper()
    # only these operations will perform
    # ALLOWED OPERATIONS

    
    allowed = (
        upper_query.startswith("SELECT")
        or upper_query.startswith("CREATE TABLE")
        or upper_query.startswith("INSERT INTO")
    )
    if not allowed:
        return False, (
            "Only SELECT, CREATE TABLE and INSERT INTO "
            "queries are allowed."
        )
    # cannot delete drop
    # BLOCK DANGEROUS COMMANDS
    dangerous_commands = [
        "DROP DATABASE",
        "DROP TABLE",
        "DROP SCHEMA",
        "TRUNCATE TABLE",
        "DELETE FROM",
        "UPDATE ",
        "ALTER TABLE",
        "GRANT ",
        "REVOKE ",
        "CREATE USER",
        "DROP USER",
        "RENAME TABLE",
        "LOAD DATA",
        "INTO OUTFILE",
        "INTO DUMPFILE",
        "SHUTDOWN",
        "SET GLOBAL",
        "SET SESSION"
    ]
    for command in dangerous_commands:

        if command in upper_query:

            return False, (
                f"Dangerous SQL command blocked: {command}"
            )

    # BLOCK MULTIPLE STATEMENTS
    # Remove one final semicolon
    without_final_semicolon = upper_query.rstrip(";").strip()
    if ";" in without_final_semicolon:

        return False, (
            "Multiple SQL statements are not allowed."
        )

    # BLOCK SQL COMMENTS / INJECTION PATTERNS


    if "--" in check_query:

        return False, (
            "SQL comments are not allowed."
        )

    if "/*" in check_query or "*/" in check_query:

        return False, (
            "SQL block comments are not allowed."
        )

    # FINAL CHECK

    return True, "SQL query is safe."