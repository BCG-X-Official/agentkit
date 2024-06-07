# -*- coding: utf-8 -*-
import re


def is_sql_query_safe(sql_string: str) -> bool:
    """
    Check if the given SQL string contains any DML or DDL statements.

    Only allow SELECT and WITH statements.
    """
    #Allow only the following SELECT and WITH statements queries.
    #Full queries need to be included in the allowed_queries list. Example: allowed_queries = ["select * from table1", "with cte as (select * from table1) select * from cte"]
    allowed_queries = []

    # List of forbidden SQL keywords (DML and DDL statements).
    forbidden_keywords = [
        "base64"
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
    #Convert the SQL string to lowercase.
    sql_string = sql_string.lower()
    # Remove comments from the SQL string
    sql_string = re.sub(
        r"(--[^\n]*|/\*.*?\*/)",
        "",
        sql_string,
        flags=re.MULTILINE | re.DOTALL,
    )
    #------------------------------------------------------------------------------------- 
    # Extract all SQL keywords from the string
#    keywords = re.findall(
#        r"\b[A-Z]+\b",
#        sql_string,
#    )

    # Check if any forbidden keyword is present in the list of extracted keywords
    #for keyword in forbidden_keywords:
        #if keyword in keywords:
            #return False
    #------------------------------------------------------------------------------------- 
    # Check for any forbidden keywords in the SQL string.
    if any(keyword in sql_string for keyword in forbidden_keywords):
        return False
    # Check if the SQL string contains any of the allowed queries included in the allowed_queries list.
    elif any(query in sql_string for query in allowed_queries):
        return True
    else:
        return False