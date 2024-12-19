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

        cursor.execute("""
            SELECT party_name, president_discord_id, vp_discord_id
            FROM candidates;
        """)
        candidate_data = cursor.fetchall()

        votes = defaultdict(lambda: {"votes": 0, "president_discord_id": None, "vp_discord_id": None})
        for party, president_id, vp_id in candidate_data:
            votes[party]["president_discord_id"] = president_id
            votes[party]["vp_discord_id"] = vp_id

        for party, count in votes_by_party:
            if party in votes:
                votes[party]["votes"] = count

        sorted_votes = dict(
            sorted(votes.items(), key=lambda item: item[1]["votes"], reverse=True)
        )

    return sorted_votes


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


if __name__ == "__main__":
    print(f"Winner: {determine_winner()} party")
    print(f"Votes by party: {get_votes_by_party()}")
