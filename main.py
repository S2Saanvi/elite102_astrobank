import sqlite3
import random

DB_PATH = "bank_accounts.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bank_accounts (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            balance REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def generate_unique_id():
    conn = get_connection()
    cursor = conn.cursor()
    while True:
        new_id = random.randint(1000000000, 9999999999)
        cursor.execute("SELECT id FROM bank_accounts WHERE id = ?", (new_id,))
        if cursor.fetchone() is None:
            conn.close()
            return new_id


def create_account(name, balance):
    new_id = generate_unique_id()
    conn = get_connection()
    conn.execute(
        "INSERT INTO bank_accounts (id, name, balance) VALUES (?, ?, ?)",
        (new_id, name, balance),
    )
    conn.commit()
    conn.close()
    return new_id


def get_account(account_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT id, name, balance FROM bank_accounts WHERE id = ?", (account_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def search_by_name(name):
    conn = get_connection()
    row = conn.execute(
        "SELECT id, name, balance FROM bank_accounts WHERE LOWER(name) = LOWER(?)", (name,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def deposit(account_id, amount):
    conn = get_connection()
    conn.execute(
        "UPDATE bank_accounts SET balance = balance + ? WHERE id = ?",
        (amount, account_id),
    )
    conn.commit()
    row = conn.execute(
        "SELECT balance FROM bank_accounts WHERE id = ?", (account_id,)
    ).fetchone()
    conn.close()
    return row["balance"] if row else None


def withdraw(account_id, amount):
    conn = get_connection()
    row = conn.execute(
        "SELECT balance FROM bank_accounts WHERE id = ?", (account_id,)
    ).fetchone()
    if row is None:
        conn.close()
        return None, "Account not found"
    if row["balance"] < amount:
        conn.close()
        return None, "Insufficient funds"
    conn.execute(
        "UPDATE bank_accounts SET balance = balance - ? WHERE id = ?",
        (amount, account_id),
    )
    conn.commit()
    new_bal = conn.execute(
        "SELECT balance FROM bank_accounts WHERE id = ?", (account_id,)
    ).fetchone()["balance"]
    conn.close()
    return new_bal, None
