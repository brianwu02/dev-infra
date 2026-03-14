"""Tool: Natural Language Database Assistant

Ask questions in plain English → generates SQL → runs against TimescaleDB → explains results.

Usage:
    python tools/db_assistant.py "Show me the top 5 largest tables"
    python tools/db_assistant.py  # interactive mode
"""

import json
import os
import sys
import psycopg2
import anthropic

client = anthropic.Anthropic()

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", "5432")),
    "user": os.environ.get("DB_USER", "devuser"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "dbname": os.environ.get("DB_NAME", "devdb"),
}


def get_schema() -> str:
    """Get database schema as context for the model."""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position
    """)
    rows = cur.fetchall()
    conn.close()

    tables = {}
    for table, col, dtype in rows:
        tables.setdefault(table, []).append(f"{col} ({dtype})")

    return "\n".join(
        f"  {table}: {', '.join(cols)}"
        for table, cols in sorted(tables.items())
    ) or "  (no tables found — database is empty)"


def generate_sql(question: str, schema: str) -> str:
    """Generate SQL from a natural language question."""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=(
            "You are a PostgreSQL expert. Generate a single SQL query to answer the user's question. "
            "Return ONLY the SQL, no explanation, no markdown fences.\n\n"
            f"Database schema:\n{schema}"
        ),
        messages=[{"role": "user", "content": question}],
    )
    return response.content[0].text.strip()


def execute_sql(sql: str) -> list[tuple]:
    """Execute SQL and return results."""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute(sql)
    if cur.description:
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
        conn.close()
        return cols, rows
    conn.close()
    return [], []


def explain_results(question: str, sql: str, cols: list, rows: list) -> str:
    """Explain query results in plain English."""
    result_text = f"Columns: {cols}\nRows ({len(rows)} total):\n"
    for row in rows[:20]:
        result_text += f"  {row}\n"
    if len(rows) > 20:
        result_text += f"  ... and {len(rows) - 20} more rows\n"

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": (
                f"Question: {question}\n"
                f"SQL executed: {sql}\n"
                f"Results:\n{result_text}\n\n"
                "Explain these results concisely in plain English."
            ),
        }],
    )
    return response.content[0].text


def ask(question: str):
    """Full pipeline: question → SQL → execute → explain."""
    print(f"\nQ: {question}")

    schema = get_schema()
    sql = generate_sql(question, schema)
    print(f"SQL: {sql}")

    try:
        cols, rows = execute_sql(sql)
        explanation = explain_results(question, sql, cols, rows)
        print(f"Answer: {explanation}")
    except Exception as e:
        print(f"Error: {e}")


def main():
    if len(sys.argv) > 1:
        ask(" ".join(sys.argv[1:]))
    else:
        print("DB Assistant — ask questions in English (type 'quit' to exit)")
        while True:
            q = input("\nQ: ").strip()
            if not q or q.lower() in ("quit", "exit"):
                break
            ask(q)


if __name__ == "__main__":
    main()
