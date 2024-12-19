# This script takes ballots from the Google form, validates them, and puts them into the DB

import sqlite3
import requests
import os
import csv
import time
import traceback

import TEAW_ballot_secrets

os.chdir(os.path.dirname(os.path.abspath(__file__)))


CSV_FILE = "_ballots.csv"
DB_FILE = "../../db/teaw_election_1.db"

# TODO: clean up the sheet, ensure that the data is valid
def get_sheet() -> None:
    """
    Fetches the ballot data from the Google Sheet and save it locally as a CSV file.
    """

    request = requests.get(TEAW_ballot_secrets.GOOGLE_SHEET_URL)
    if request.status_code == 200:
        with open(CSV_FILE, "w") as file:
            file.write(request.text.replace("\n", ""))
            # delete the header row
    else:
        raise Exception("Failed to get Google Sheet")


def validate_sheet() -> None:
    """
    Remove duplicate votes in the same row. Use the lowest rank (highest preference).

    remove any old vote rows from the same voter. Use the newest vote.
    
    
    
    
    
    """
    pass


def process_ballots():
    """
    Process the ballots from the CSV file:
    - Validate voter IDs against the 'voters' table.
    - Remove old ballots for re-voting voters.
    - Insert the new ballots into the database.
    """

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        with open(CSV_FILE, "r") as file:
            reader = csv.DictReader(file)
            ballots = list(reader)

        for ballot in ballots:
            voter_id = ballot["Voter ID"]
            
            # NOTE: Ballot validation
            # Check if the voter is in the 'voters' table (note, does not check if the ID is valid, only that it is in the table)
            cursor.execute("SELECT discord_id, discord_username, time_registered FROM voters WHERE voter_id = ?", (voter_id,))
            voter_data = cursor.fetchone()

            if voter_data is None:
                print(f"Invalid voter ID: {voter_id}, ballot discarded.")
                continue

            discord_id, discord_username, time_registered = voter_data
            print(f"Processing ballot for voter {voter_id} ({discord_username}, {discord_id}), registered at {time_registered}.")


            cursor.execute("DELETE FROM ballots WHERE voter_id = ?", (voter_id,)) # Remove old vote if voter has already voted


            # NOTE: Ballot insertion
            for rank, candidate in ballot.items():
                if rank not in ["Timestamp", "Voter ID"] and candidate.strip(): # What the fuck does this do again?
                    try:
                        rank_int = int(rank)  # The rank is derived from the column position. In the election, the lower the rank, the higher the preference.
                        cursor.execute("""
                            INSERT INTO ballots (voter_id, candidate, rank)
                            VALUES (?, ?, ?)
                        """, (voter_id, candidate, rank_int))
                    except ValueError:
                        print(f"Invalid rank or candidate: {rank} -> {candidate}")

        conn.commit()

    print(f"Processed {len(ballots)} ballots")



if __name__ == "__main__":
    while True: # This will redo everything every loop iteration. not ideal, but it works
        try:
            get_sheet()
            process_ballots()
        except Exception:
            print(f"{traceback.format_exc()}")
        except KeyboardInterrupt:
            break
        finally:
            time.sleep(60)
            os.remove(CSV_FILE)
