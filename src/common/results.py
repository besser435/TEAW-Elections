import sqlite3
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))


DB_FILE = "../../db/TEAW_E_1.db"


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
    Implements the Ranked Choice Voting (RCV) algorithm to determine the winner.
    """
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()

        try:
            # Step 1: Load all ballots into a dictionary grouped by voter
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

            # Step 2: Start the RCV process
            active_candidates = set(candidate for _, _, candidate in ballots)

            while True:
                # Count first-choice votes
                first_choice_counts = {candidate: 0 for candidate in active_candidates}
                for ballot in voter_ballots.values():
                    if ballot and ballot[0] in active_candidates:
                        first_choice_counts[ballot[0]] += 1

                total_votes = sum(first_choice_counts.values())

                # Check for majority
                for candidate, count in first_choice_counts.items():
                    if count > total_votes / 2:
                        return f"The winner is {candidate} with {count} votes!"

                # If no majority, find the candidate with the fewest first-choice votes
                min_votes = min(first_choice_counts.values())
                candidates_to_eliminate = [c for c, v in first_choice_counts.items() if v == min_votes]

                # Eliminate the candidate(s) with the fewest votes
                for candidate in candidates_to_eliminate:
                    active_candidates.remove(candidate)

                # Reassign votes for eliminated candidates
                for voter_id, ballot in voter_ballots.items():
                    voter_ballots[voter_id] = [c for c in ballot if c in active_candidates]

                # If only one candidate is left, they are the winner
                if len(active_candidates) == 1:
                    winner = next(iter(active_candidates))
                    return f"The winner is {winner} by default, as all other candidates were eliminated."

        except Exception as e:
            print(f"Error during RCV process: {e}")
            return "Error occurred during the election process."






#print(total_candidate_votes())

# Pretty print the raw points
raw_points = total_raw_candidate_points()
for candidate, points in raw_points.items():
    print(f"{candidate}:")
    for rank, count in points.items():
        print(f"    Rank {rank}: {count}")
    print()