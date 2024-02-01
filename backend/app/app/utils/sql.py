# -*- coding: utf-8 -*-
import re


def is_sql_query_safe(sql_string: str) -> bool:
    """
    Check if the given SQL string contains any DML or DDL statements.

    Only allow SELECT and WITH statements.
    """
    # List of forbidden SQL keywords (DML and DDL statements)
    forbidden_keywords = [
        "INSERT",
        "UPDATE",
        "DELETE",
        "REPLACE",
        "CREATE",
        "ALTER",
        "DROP",
        "TRUNCATE",
        "GRANT",
        "REVOKE",
    ]

    # Remove comments from the SQL string
    sql_string = re.sub(
        r"(--[^\n]*|/\*.*?\*/)",
        "",
        sql_string,
        flags=re.MULTILINE | re.DOTALL,
    )

    # Extract all SQL keywords from the string
    keywords = re.findall(
        r"\b[A-Z]+\b",
        sql_string,
    )

    # Check if any forbidden keyword is present in the list of extracted keywords
    for keyword in forbidden_keywords:
        if keyword in keywords:
            return False

    return True
