import streamlit as st
import mysql.connector
import pandas as pd
from mysql.connector.connection import MySQLConnection
from typing import Any, Dict, List, Optional, Tuple, Union
from config.config_heatwave import DB_CONFIG


# ------------------------------
# Database Utility Functions
# ------------------------------

def get_db_connection() -> MySQLConnection:
    """
    Establish a connection to the MySQL database using credentials
    from the imported DB_CONFIG dictionary.
    """
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            autocommit=True
        )
        return conn
    except mysql.connector.Error as err:
        st.error(f"Database connection failed: {err}")
        raise


def run_query(
    query: str,
    params: Tuple[Any, ...] = (),
    multi: bool = False
) -> Optional[Union[pd.DataFrame, List[pd.DataFrame]]]:
    """
    Execute a SQL query and return the results as Pandas DataFrame(s).

    Args:
        query: SQL query string.
        params: Optional query parameters.
        multi: Whether to handle multiple result sets.

    Returns:
        A single DataFrame or list of DataFrames, or None if execution fails.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(buffered=True)
            results: Union[List[pd.DataFrame], pd.DataFrame, None] = None

            if multi:
                result_sets: List[pd.DataFrame] = []
                for result in cursor.execute(query, params=params, multi=True):
                    if result.with_rows:
                        result_sets.append(
                            pd.DataFrame(result.fetchall(), columns=result.column_names)
                        )
                results = result_sets
            else:
                results = pd.read_sql(query, conn, params=params)

            return results

    except mysql.connector.Error as err:
        st.error(f"MySQL error: {err}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

    return None


# ------------------------------
# Streamlit App Configuration
# ------------------------------

st.set_page_config(page_title="NL 2 SQL", layout="wide")
st.logo("im/HeatWave_logo.png", size="large")

st.title("The DBA Interpreter")
st.markdown(
    "***MySQL HeatWave GenAI collects information from performance_schema, "
    "information_schema & sys, and then uses an LLM to generate an SQL query "
    "for the question pertaining to your data.***"
)
st.subheader("💬 NL 2 SQL with MySQL HeatWave")

# ------------------------------
# User Input Form
# ------------------------------

with st.form("nl_2_sql_4_dba_form"):
    nl_statement = st.text_area(
        "Ask a question to your MySQL HeatWave database:",
        placeholder="e.g., List all database users and their host access restrictions."
    )

    col1, col2 = st.columns(2)
    with col1:
        db_name = st.multiselect(
            "Select databases:",
            options=["performance_schema", "information_schema", "sys"],
            default=["performance_schema", "information_schema", "sys"]
        )

    with col2:
        model_id = st.selectbox(
            "Select LLM Model:",
            options=[
                "meta.llama-3.3-70b-instruct",
                "llama3.1-8b-instruct-v1",
                "llama3.2-3b-instruct-v1"
            ],
            index=0
        )

    run_query_option = st.checkbox("Run the generated query?", value=False)
    submitted = st.form_submit_button("Submit Query")


# ------------------------------
# Main Logic
# ------------------------------

def build_stored_procedure_call(
    nl_statement: str,
    db_names: List[str],
    model_id: str
) -> str:
    """Constructs the SQL call for sys.NL_SQL stored procedure."""
    schemas_json = ",".join([f"'{db}'" for db in db_names])
    return f"""
        CALL sys.NL_SQL(
            "{nl_statement}",
            @output,
            JSON_OBJECT(
                'schemas', JSON_ARRAY({schemas_json}),
                'model_id', '{model_id}'
            )
        );
    """


if submitted and nl_statement.strip():
    sql = build_stored_procedure_call(nl_statement, db_name, model_id)
    st.write("**Generated Stored Procedure Call:**")
    st.code(sql, language="sql")

    results = run_query(sql, multi=True)

    if results and isinstance(results, list) and len(results) >= 2:
        # First result set = Generated SQL
        generated_sql_df = results[0]
        generated_sql = generated_sql_df.iloc[0, 0] if not generated_sql_df.empty else None

        if generated_sql:
            st.markdown("**Generated SQL:**")
            st.code(generated_sql, language="sql")

        # Second result set = Executed query result
        if run_query_option:
            query_result_df = results[1]
            if not query_result_df.empty:
                st.markdown("**Query Result:**")
                st.dataframe(query_result_df, use_container_width=True, hide_index=True)
            else:
                st.warning("⚠️ The query returned no rows.")
    else:
        st.error("❌ No results returned from the stored procedure.")

