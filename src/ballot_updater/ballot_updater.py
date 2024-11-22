# This script takes ballots from the Google form, validates them, and puts them into the DB

import sqlite3
import requests
import os
import csv

import src.TEAW_E_secrets as TEAW_E_secrets

os.chdir(os.path.dirname(os.path.abspath(__file__)))



CSV_FILE = "_ballots.csv"
DB_FILE = "../../db/TEAW_E_1.db"

def get_sheet() -> None:
    request = requests.get(TEAW_E_secrets.GOOGLE_SHEET_URL)
    if request.status_code == 200:
        with open(CSV_FILE, "w") as file:
            file.write(request.text.replace("\n", ""))
    else:
        raise Exception("Failed to get Google Sheet")
get_sheet()

def process_ballots():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    with open(CSV_FILE, "r") as file:
        reader = csv.DictReader(file)
        ballots = list(reader)


    for ballot in ballots:
        voter_id = ballot["Voter ID"]
        
        # NOTE: Ballot validation
        # Check if the voter is in the 'voters' table (note, does not check if the ID is valid, only that it is in the table)
        cursor.execute("SELECT discord_username, time_registered FROM voters WHERE voter_id = ?", (voter_id,))
        voter_data = cursor.fetchone()

        if voter_data is None:
            print(f"Invalid voter ID: {voter_id}, ballot discarded.")
            continue

        discord_username, time_registered = voter_data
        print(f"Processing ballot for voter {voter_id} ({discord_username}), registered at {time_registered}.")

        cursor.execute("DELETE FROM ballots WHERE voter_id = ?", (voter_id,)) # remove old vote if voter has already voted


        # NOTE: Ballot insertion
        for candidate, rank in ballot.items():
            if candidate != "Timestamp" and candidate != "Voter ID":
                cursor.execute("""
                    INSERT INTO ballots (voter_id, candidate, rank)
                    VALUES (?, ?, ?)
                """, (voter_id, candidate, int(rank) if rank else None))

    conn.commit()
    conn.close()



if __name__ == "__main__":
    try:
        get_sheet()
        process_ballots()
        print("Ballots processed successfully.")
    except Exception as e:
        print(f"Error: {e}")