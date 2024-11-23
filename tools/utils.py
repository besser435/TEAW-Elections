import sqlite3
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))


DB_FILE = "../db/TEAW_E_1.db"


def initialize_database():
    db = sqlite3.connect(DB_FILE)
    cursor = db.cursor()

    # Create voters table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS voters (
            voter_id TEXT PRIMARY KEY,
            discord_id TEXT,
            discord_username TEXT,
            time_registered TEXT
        );
    """)

    # Create ballots table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ballots (
            voter_id TEXT,
            candidate TEXT,
            rank INTEGER,
            FOREIGN KEY (voter_id) REFERENCES voters(voter_id)
        );
    """)

    cursor.execute("DELETE FROM voters;")
    cursor.execute("DELETE FROM ballots;")
    db.commit()

    print("Database initialized")
    db.close()


def populate_voters(voter_data):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    for voter in voter_data:
        cursor.execute("""
            INSERT INTO voters (voter_id, discord_id, discord_username, time_registered)
            VALUES (?, ?, ?, ?)
        """, voter)

    conn.commit()
    conn.close()

    print("Voters populated")


def drop(table):    # mainly for testing
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(f"DROP TABLE {table};")
    print(f"Dropped table {table}")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    drop("voters")
    drop("ballots")
    initialize_database()


    voter_data = [
        ("1111", "123123123123", "UserOne", "1732268289"),
        ("2222", "345345345345", "UserTwo", "1732268289")
    ]
    #populate_voters(voter_data)

    pass
