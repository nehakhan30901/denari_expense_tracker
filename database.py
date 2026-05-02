import sqlite3
from contextlib import closing
from pathlib import Path


DATABASE_PATH = Path(__file__).with_name("denari.db")


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with closing(get_connection()) as connection:
        with connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS expense_groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    closed INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    expense_name TEXT NOT NULL,
                    amount REAL NOT NULL,
                    paid_by TEXT NOT NULL,
                    owed_by TEXT NOT NULL,
                    owed_to TEXT NOT NULL,
                    owed_amount REAL NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            columns = connection.execute("PRAGMA table_info(expenses)").fetchall()
            column_names = {column["name"] for column in columns}
            if "settled" not in column_names:
                connection.execute(
                    "ALTER TABLE expenses ADD COLUMN settled INTEGER NOT NULL DEFAULT 0"
                )
            if "group_id" not in column_names:
                connection.execute("ALTER TABLE expenses ADD COLUMN group_id INTEGER")

            default_group_id = ensure_default_group(connection)
            connection.execute(
                "UPDATE expenses SET group_id = ? WHERE group_id IS NULL",
                (default_group_id,),
            )


def ensure_default_group(connection):
    row = connection.execute(
        "SELECT id FROM expense_groups ORDER BY id LIMIT 1"
    ).fetchone()
    if row:
        return row["id"]

    cursor = connection.execute(
        "INSERT INTO expense_groups (name) VALUES (?)",
        ("General",),
    )
    return cursor.lastrowid


def create_group(name):
    with closing(get_connection()) as connection:
        with connection:
            cursor = connection.execute(
                "INSERT INTO expense_groups (name) VALUES (?)",
                (name,),
            )
            return cursor.lastrowid


def list_groups():
    with closing(get_connection()) as connection:
        return connection.execute(
            """
            SELECT id, name, closed, created_at
            FROM expense_groups
            ORDER BY closed ASC, created_at DESC, id DESC
            """
        ).fetchall()


def get_group(group_id):
    with closing(get_connection()) as connection:
        return connection.execute(
            "SELECT id, name, closed, created_at FROM expense_groups WHERE id = ?",
            (group_id,),
        ).fetchone()


def close_group(group_id):
    with closing(get_connection()) as connection:
        with connection:
            cursor = connection.execute(
                "UPDATE expense_groups SET closed = 1 WHERE id = ?",
                (group_id,),
            )
            connection.execute(
                "UPDATE expenses SET settled = 1 WHERE group_id = ?",
                (group_id,),
            )
            return cursor.rowcount


def save_expense(group_id, expense_name, amount, paid_by, owed_by, owed_to, owed_amount):
    with closing(get_connection()) as connection:
        with connection:
            cursor = connection.execute(
                """
                INSERT INTO expenses (
                    group_id,
                    expense_name,
                    amount,
                    paid_by,
                    owed_by,
                    owed_to,
                    owed_amount
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (group_id, expense_name, amount, paid_by, owed_by, owed_to, owed_amount),
            )
            return cursor.lastrowid


def list_expenses(group_id):
    with closing(get_connection()) as connection:
        return connection.execute(
            """
            SELECT
                id,
                group_id,
                expense_name,
                amount,
                paid_by,
                owed_by,
                owed_to,
                owed_amount,
                settled,
                created_at
            FROM expenses
            WHERE group_id = ?
            ORDER BY created_at DESC, id DESC
            """,
            (group_id,),
        ).fetchall()


def get_balance(group_id):
    with closing(get_connection()) as connection:
        row = connection.execute(
            """
            SELECT
                COALESCE(SUM(
                    CASE
                        WHEN owed_by = 'Stephen' AND owed_to = 'Neha' THEN owed_amount
                        WHEN owed_by = 'Neha' AND owed_to = 'Stephen' THEN -owed_amount
                        ELSE 0
                    END
                ), 0) AS stephen_owes_neha
            FROM expenses
            WHERE settled = 0 AND group_id = ?
            """,
            (group_id,),
        ).fetchone()
        return row["stephen_owes_neha"]


def mark_expense_settled(expense_id, group_id):
    with closing(get_connection()) as connection:
        with connection:
            cursor = connection.execute(
                "UPDATE expenses SET settled = 1 WHERE id = ? AND group_id = ?",
                (expense_id, group_id),
            )
            return cursor.rowcount
