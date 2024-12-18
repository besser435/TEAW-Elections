import sqlite3
import os
from collections import defaultdict
import traceback

os.chdir(os.path.dirname(os.path.abspath(__file__)))


DB_FILE = "../../db/TEAW_E_1.db"


def total_raw_candidate_points(db_file=DB_FILE) -> dict:
    """
    Returns a breakdown of how many points each candidate has for each rank 
    before the RCV algorithm is applied.
    """
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT candidate, rank, COUNT(*) as count
                FROM ballots
                GROUP BY candidate, rank
                ORDER BY candidate, rank;
            """)
            results = cursor.fetchall()

            raw_points = {}
            for candidate, rank, count in results:
                if candidate not in raw_points:
                    # We still want the zeros values for ranks with no votes
                    # Hardcoded to 10 ranks for now
                    raw_points[candidate] = {rank: 0 for rank in range(1, 11)}  
                    
                raw_points[candidate][rank] = count

            return raw_points

        except Exception as e:
            print(f"Error retrieving raw candidate points: {e}")
            return {}



class Candidate:
    def __init__(self, name: str):
        self.name = name
        self.eliminated = False

        # autism
        self.point_totals = {}

    def __repr__(self):
        return f"{self.name} {self.point_totals})"


def determine_winner(db_file=DB_FILE) -> str:
    """
    Returns a winner based on the RCV algorithm.
    """
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT voter_id, candidate, rank
            FROM ballots
            ORDER BY voter_id, rank;
        """)
        ballots = cursor.fetchall()



        candidates = [
            
        ]



print(determine_winner())



# Pretty print the raw points
# raw_points = total_raw_candidate_points()
# for candidate, points in raw_points.items():
#     print(f"{candidate}:")
#     for rank, count in points.items():
#         print(f"    Rank {rank}: {count}")
#     print()