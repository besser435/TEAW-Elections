import sqlite3
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))


DB_FILE = "../db/TEAW_E_1.db"


def initialize_database(db_file=DB_FILE):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()

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
        conn.commit()

    print("Database initialized")


def populate_voters(db_file=DB_FILE, voter_data=None):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()

        for voter in voter_data:
            cursor.execute("""
                INSERT INTO voters (voter_id, discord_id, discord_username, time_registered)
                VALUES (?, ?, ?, ?)
            """, voter)

        conn.commit()

        print("Voters populated")


def drop(db_file=DB_FILE, table=None):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()

        cursor.execute(f"DROP TABLE {table};")

        conn.commit()
    print(f"Dropped table {table}")


if __name__ == "__main__":
    #drop("voters")
    #drop("ballots")
    #initialize_database()


    voter_data = [
        ("1111", "123123123123", "UserOne", "2024-11-27T01:48:05Z"),
    ]

    populate_voters(voter_data=voter_data)

    pass
