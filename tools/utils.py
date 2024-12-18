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


def populate_ballots(db_file=DB_FILE, ballot_data=None):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()

        for ballot in ballot_data:
            cursor.execute("""
                INSERT INTO ballots (voter_id, candidate, rank)
                VALUES (?, ?, ?)
            """, ballot)

        conn.commit()

        print("Ballots populated")


def drop(db_file=DB_FILE, table=None):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()

        cursor.execute(f"DROP TABLE {table};")

        conn.commit()
    print(f"Dropped table {table}")


if __name__ == "__main__":
    #drop(table="voters")
    #drop(table="ballots")
    #initialize_database()


    voter_data = [
        ("1111", "1111", "UserOne", "2024-11-27T01:48:05Z"),
        ("2222", "2222", "UserTwo", "2024-11-27T01:48:05Z"),
        ("3333", "3333", "UserThree", "2024-11-27T01:48:05Z")
    ]
    #populate_voters(voter_data=voter_data)


    ballot_data = [
        #("1111", "Green Party", 1),
        #("2222", "Green Party", 1),
        #("3333", "Slommy Party ", 1),
        ("4444", "Slommy Party ", 5),

    ]
    
    populate_ballots(ballot_data=ballot_data)



