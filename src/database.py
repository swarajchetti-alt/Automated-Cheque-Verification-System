import sqlite3

DB_PATH = "bank.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_no TEXT,
        name TEXT,
        signature_path TEXT,
        balance REAL           
    )
    """)

    conn.commit()
    conn.close()


def add_user(account_no, name, signature_path,balance):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO accounts (account_no, name, signature_path,balance)
    VALUES (?, ?, ?, ?)
    """, (account_no, name, signature_path, balance))

    conn.commit()
    conn.close()


def get_user(account_no):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM accounts WHERE account_no=?", (account_no,))
    user = cursor.fetchone()

    conn.close()
    return user

# def get_user_by_name(name):
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()

#     #cursor.execute("SELECT * FROM accounts WHERE name=?", (name,))
#     cursor.execute("SELECT * FROM accounts WHERE LOWER(name)=LOWER(?)", (name,))
#     user = cursor.fetchone()

#     conn.close()
#     return user

def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM accounts")
    users = cursor.fetchall()

    conn.close()
    return users

def delete_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM accounts WHERE id=?", (user_id,))

    conn.commit()
    conn.close()

from rapidfuzz import process, fuzz

def get_user_by_name(input_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM accounts")
    users = cursor.fetchall()

    conn.close()

    names = [user[2] for user in users]  # name column

    match, score, index = process.extractOne(
        input_name,
        names,
        scorer=fuzz.ratio
    )

    if score >=50:
        return users[index]
    else:
        return None
    
def update_balance(account_no, new_balance):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE accounts SET balance=? WHERE account_no=?",
        (new_balance, account_no)
    )

    conn.commit()
    conn.close()