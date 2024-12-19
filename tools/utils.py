import sqlite3
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))


DB_FILE = "../db/teaw_election_1.db"


def initialize_database(db_file=DB_FILE):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()

        # Candidates
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS candidates (
                party_name TEXT PRIMARY KEY,
                president_discord_id TEXT,
                vp_discord_id TEXT
            );
        """)
        cursor.execute("DELETE FROM candidates;")

        # Voters
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS voters (
                voter_id TEXT PRIMARY KEY,
                discord_id TEXT,
                discord_username TEXT,
                time_registered TEXT
            );
        """)
        #cursor.execute("DELETE FROM voters;")

        # Ballots
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ballots (
                voter_id TEXT UNIQUE,
                party TEXT,
                time_voted TEXT,
                FOREIGN KEY (voter_id) REFERENCES voters(voter_id)
            );
        """)
        cursor.execute("DELETE FROM ballots;")

        conn.commit()

    print("Database initialized")


def populate_candidates(db_file=DB_FILE, candidate_data=None):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()

        for candidate in candidate_data:
            cursor.execute("""
                INSERT INTO candidates (party_name, president_discord_id, vp_discord_id)
                VALUES (?, ?, ?)
            """, candidate)

        conn.commit()

        print("Candidates populated")


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
                INSERT INTO ballots (voter_id, party, time_voted)
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
    #drop(table="candidates")
    #initialize_database()

    #populate_voters(voter_data=voter_data)


    ballot_data = [
        #("1", "Carthage Restoration", "2021-10-01T00:00:00Z"),
        #("2", "Green", "2021-10-01T00:00:00Z"),
        ("4", "Slommy", "2021-10-01T00:00:00Z")
    ]
    populate_ballots(ballot_data=ballot_data)


    candidates = [
        ("Weed", "707416969372106753", "414509303605755904"),
        ("Irish Republican", "178891657448521738", "568799388651094026"),
        ("Green", "468034405278023690", "232014294303113216"),
        ("Slommy", "463641134896250901", "875854686027133040"),
        ("Communist", "575835458106294272", "307777393160880140"),
        ("Democrats For Christ ", "1057806577253502986", "293385619168690176"),
        ("Carthage Restoration", "939380723494842408", "791861067470864436"),
        ("Freedom", "1120394930519556116", "308667250771230721")
    ]
    #populate_candidates(candidate_data=candidates)




