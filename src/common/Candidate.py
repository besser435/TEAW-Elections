class Candidate:
    def __init__(self, name):
        self.name = name
        self.votes = 0
        self.active = True

    def reset_votes(self):
        """Resets the vote count to 0."""
        self.votes = 0

    def add_votes(self, count):
        """Adds a specified number of votes."""
        self.votes += count

    def eliminate(self):
        """Marks the candidate as eliminated."""
        self.active = False

    def is_active(self):
        """Checks if the candidate is active."""
        return self.active

    def __repr__(self):
        """String representation for debugging."""
        return f"Candidate(name={self.name}, votes={self.votes}, active={self.active})"
