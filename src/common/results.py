import sqlite3
import os
from collections import defaultdict
from Candidate import Candidate


os.chdir(os.path.dirname(os.path.abspath(__file__)))


DB_FILE = "../../db/TEAW_E_1.db"


# kind of useless given total_raw_candidate_points functions. maybe delete?
def total_candidate_votes(db_file=DB_FILE) -> dict:
    """
    Returns the total amount of votes for each candidate/party.
    """

    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT candidate, COUNT(*) as vote_count
                FROM ballots
                GROUP BY candidate
                ORDER BY vote_count DESC;
            """)
            results = cursor.fetchall()

            vote_totals = {row[0]: row[1] for row in results}   # Convert to dict

            return vote_totals

        except Exception as e:
            print(f"Error retrieving candidate votes: {e}")
            return {}


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

def determine_winner(db_file=DB_FILE) -> str:
    """
    Implements the Ranked Choice Voting (RCV) algorithm using an enhanced Candidate class.
    """
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()

        try:
            # Load all ballots
            cursor.execute("""
                SELECT voter_id, rank, candidate
                FROM ballots
                ORDER BY voter_id, rank;
            """)
            ballots = cursor.fetchall()

            # Organize ballots into a dictionary
            voter_ballots = {}
            for voter_id, rank, candidate in ballots:
                if voter_id not in voter_ballots:
                    voter_ballots[voter_id] = []
                voter_ballots[voter_id].append(candidate)

            # Initialize candidates
            candidates = {candidate: Candidate(candidate) for _, _, candidate in ballots}


            while True:
                # Reset votes
                for candidate in candidates.values():
                    candidate.reset_votes()


                    print(candidate)
                    

                # Count first-choice votes for active candidates
                for ballot in voter_ballots.values():
                    if ballot and candidates[ballot[0]].is_active():
                        candidates[ballot[0]].add_votes(1)

                # Check for a majority
                total_votes = sum(c.votes for c in candidates.values() if c.is_active())
                for candidate in candidates.values():
                    if candidate.is_active() and candidate.votes > total_votes / 2:
                        return f"The default majority winner is {candidate.name} with {candidate.votes} votes!"

                # Eliminate the candidate(s) with the fewest votes
                min_votes = min(c.votes for c in candidates.values() if c.is_active())
                candidates_to_eliminate = [c for c in candidates.values() if c.is_active() and c.votes == min_votes]

                for candidate in candidates_to_eliminate:
                    candidate.eliminate()

                # Redistribute votes
                for voter_id, ballot in voter_ballots.items():
                    voter_ballots[voter_id] = [c for c in ballot if candidates[c].is_active()]

                # If only one candidate remains, declare them the winner
                active_candidates = [c for c in candidates.values() if c.is_active()]
                if len(active_candidates) == 1:
                    return f"The winner is {active_candidates[0].name}, as all other candidates were eliminated."

        except Exception as e:
            print(f"Error during RCV process: {e}")
            return "Error occurred during the election process."



print(determine_winner())



# Pretty print the raw points
# raw_points = total_raw_candidate_points()
# for candidate, points in raw_points.items():
#     print(f"{candidate}:")
#     for rank, count in points.items():
#         print(f"    Rank {rank}: {count}")
#     print()