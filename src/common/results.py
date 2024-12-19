import sqlite3
import os
from collections import defaultdict
import traceback

os.chdir(os.path.dirname(os.path.abspath(__file__)))


DB_FILE = "../../db/teaw_election_1.db"


def get_votes_by_party(db_file=DB_FILE) -> dict:
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT party, COUNT(party)
            FROM ballots
            GROUP BY party;
        """)
        votes_by_party = cursor.fetchall()

        votes = defaultdict(int)
        for party, count in votes_by_party:

            votes[party] = count

    return dict(votes)


def determine_winner(db_file=DB_FILE) -> list[str]:
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT party, COUNT(*) as vote_count
            FROM ballots
            GROUP BY party
            ORDER BY vote_count DESC;
        """)
        results = cursor.fetchall()

        if results:
            max_votes = results[0][1]
            
            winners = [party for party, vote_count in results if vote_count == max_votes]   # fuck
        else:
            winners = []

    return winners

print(f"Winner: {determine_winner()} party")
print(f"Votes by party: {get_votes_by_party()}")
