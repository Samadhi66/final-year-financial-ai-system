import sqlite3
from pathlib import Path
from datetime import datetime


# ============================================================
# DATABASE PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATABASE_PATH = (
    BASE_DIR
    / "financial_ai.db"
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = (
        sqlite3.Row
    )

    return connection


# ============================================================
# CREATE TRANSACTIONS TABLE
# ============================================================

def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            merchant TEXT NOT NULL,

            amount REAL NOT NULL,

            transaction_date TEXT NOT NULL,

            category TEXT NOT NULL,

            source TEXT NOT NULL DEFAULT 'Manual',

            raw_ocr_text TEXT,

            created_at TEXT NOT NULL

        )
        """
    )

    connection.commit()

    connection.close()


# ============================================================
# SAVE TRANSACTION
# ============================================================

def save_transaction(
    merchant,
    amount,
    transaction_date,
    category,
    source="Manual",
    raw_ocr_text=None
):

    connection = get_connection()

    cursor = connection.cursor()

    created_at = (
        datetime.now()
        .isoformat(
            timespec="seconds"
        )
    )

    cursor.execute(
        """
        INSERT INTO transactions (
            merchant,
            amount,
            transaction_date,
            category,
            source,
            raw_ocr_text,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            merchant,
            float(amount),
            transaction_date,
            category,
            source,
            raw_ocr_text,
            created_at
        )
    )

    connection.commit()

    transaction_id = (
        cursor.lastrowid
    )

    connection.close()

    return transaction_id


# ============================================================
# GET ALL TRANSACTIONS
# ============================================================

def get_all_transactions():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            merchant,
            amount,
            transaction_date,
            category,
            source,
            raw_ocr_text,
            created_at
        FROM transactions
        ORDER BY id DESC
        """
    )

    rows = cursor.fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# GET LATEST TRANSACTION
# ============================================================

def get_latest_transaction():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            merchant,
            amount,
            transaction_date,
            category,
            source,
            raw_ocr_text,
            created_at
        FROM transactions
        ORDER BY id DESC
        LIMIT 1
        """
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    return dict(row)


# ============================================================
# TRANSACTION SUMMARY
# ============================================================

def get_transaction_summary():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            COUNT(*) AS transaction_count,
            COALESCE(SUM(amount), 0) AS total_spending,
            COALESCE(AVG(amount), 0) AS average_amount
        FROM transactions
        """
    )

    row = cursor.fetchone()

    connection.close()

    return {
        "transaction_count":
            int(
                row["transaction_count"]
            ),

        "total_spending":
            round(
                float(
                    row["total_spending"]
                ),
                2
            ),

        "average_amount":
            round(
                float(
                    row["average_amount"]
                ),
                2
            )
    }


# ============================================================
# INITIALIZE DATABASE
# ============================================================

initialize_database()