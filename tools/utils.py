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
                ON CONFLICT(voter_id) DO UPDATE SET
                party = excluded.party,
                time_voted = excluded.time_voted
                
            """, ballot)

        conn.commit()

        print("Ballots populated")


def drop(db_file=DB_FILE, table=None):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()

        cursor.execute(f"DROP TABLE {table};")

        conn.commit()
    print(f"Dropped table {table}")


def remove_candidate(db_file=DB_FILE, party_name=None):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()

        cursor.execute("DELETE FROM candidates WHERE party_name = ?", (party_name,))

        conn.commit()
    print(f"Removed candidate {party_name}")
 

if __name__ == "__main__":
    #drop(table="voters")
    #drop(table="ballots")
    #drop(table="candidates")
    #initialize_database()

    #populate_voters(voter_data=voter_data)


    ballot_data = [
        ("c2828f3d", "Green", "2024-12-20T07:04:32Z"),
        ("3d8a02b1", "Green", "2024-12-20T07:09:43Z"),
        ("5398718a", "Communist", "2024-12-20T07:12:30Z"),
        ("d8b043ed", "Carthage Restoration", "2024-12-20T07:45:47Z"),
        ("b6573e67", "Communist", "2024-12-20T10:04:54Z"),
        ("57897edc", "Democrats For Christ", "2024-12-20T11:38:22Z"),
        ("387ad912", "Carthage Restoration", "2024-12-20T11:53:23Z"),
        ("1831665a", "Green", "2024-12-20T11:54:45Z"),
        ("cb269d70", "Communist", "2024-12-20T13:33:20Z"),
        ("6d4d788c", "Carthage Restoration", "2024-12-20T14:07:34Z"),
        ("fcb14a99", "Communist", "2024-12-20T14:46:09Z"),
        ("0883161d", "Green", "2024-12-20T15:04:51Z"),
        ("f8b49218", "Communist", "2024-12-20T15:35:12Z"),
        ("3636f5ac", "Communist", "2024-12-20T15:52:50Z"),
        ("ebea8e14", "Green", "2024-12-20T19:58:33Z"),
        ("2dadb04d", "Green", "2024-12-21T03:19:48Z"),
        ("27b8e578", "Green", "2024-12-23T04:12:41Z"),
        ("70aed530", "Green", "2024-12-23T05:26:45Z"),
        ("32102bd8", "Communist", "2024-12-23T06:24:02Z"),
        ("d3a558d0", "Communist", "2024-12-23T06:26:39Z")

    ]
    populate_ballots(ballot_data=ballot_data)


    candidates = [
        ("Weed", "707416969372106753", "414509303605755904"),
        #("Irish Republican", "178891657448521738", "568799388651094026"),
        ("Green", "468034405278023690", "232014294303113216"),
        ("Slommy", "463641134896250901", "875854686027133040"),
        ("Communist", "575835458106294272", "307777393160880140"),
        ("Democrats For Christ ", "1057806577253502986", "293385619168690176"),
        ("Carthage Restoration", "939380723494842408", "791861067470864436"),
        ("Freedom", "1120394930519556116", "308667250771230721")
    ]
    #populate_candidates(candidate_data=candidates)

    #remove_candidate(party_name="Irish Republican")




