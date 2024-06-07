# -*- coding: utf-8 -*-
import re


def is_sql_query_safe(sql_string: str) -> bool:
    """
    Check if the given SQL string contains any DML or DDL statements.

    Only allow SELECT and WITH statements.
    """
    # List of forbidden SQL keywords (DML and DDL statements)
    forbidden_keywords = [
        "base64",
        "insert",
        "update",
        "delete",
        "replace",
        "create",
        "alter",
        "drop",
        "truncate",
        "grant",
        "revoke",
    ]

    # List of forbidden patterns
    forbidden_patterns = [
        r";",  # Semicolon (to prevent multiple statements)
        r"--",  # SQL comment
        r"/\*",  # Start of block comment
        r"\*/",  # End of block comment
        r"\\",  # Backslash
        r"`",  # Backtick
        r"\|",  # Pipe
        r"&",  # Ampersand
        r"\$",  # Dollar sign
        r"perl",  # Perl keyword
        r"exec",  # Exec keyword
        r"socket",  # Socket keyword
        r"connect",  # Connect keyword
        r"inet_aton",  # inet_aton function
        r"sockaddr_in",  # sockaddr_in function
    ]

    # Allowed characters (whitelist)
    allowed_characters = re.compile(r"^[a-zA-Z0-9\s,.*()_=<>!+-/*]*$")

    sql_string = sql_string.lower()

    # Remove comments from the SQL string
    sql_string = re.sub(
        r"(--[^\n]*|/\*.*?\*/)",
        "",
        sql_string,
        flags=re.MULTILINE | re.DOTALL,
    )

    # Ensure the SQL string starts with SELECT or WITH
    if not re.match(r"^\s*(select|with)\b", sql_string):
        return False

    # Check for any forbidden keywords in the SQL string
    if any(keyword in sql_string for keyword in forbidden_keywords):
        return False

    # Check for any forbidden patterns in the SQL string
    if any(re.search(pattern, sql_string) for pattern in forbidden_patterns):
        return False

    # Check for allowed characters only (whitelist)
    if not allowed_characters.match(sql_string):
        return False

    return True
