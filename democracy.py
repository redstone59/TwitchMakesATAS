import time, random

class Vote:
    def __init__(self, voter: str, choice: str):
        self.voter = voter
        self.choice = choice.strip()
        
class Ballot:
    def __init__(self, ballot_length: int):
        self.cast_votes = {}
        self.ballot_end_time = time.time() + ballot_length
    
    def cast_vote(self, vote: Vote):
        for choice in self.cast_votes:
            if vote.voter in self.cast_votes[choice]:
                self.cast_votes[choice].remove(vote.voter)
        
        self.trim()
        
        if vote.choice == "":
            # This is for retracted vote, which the bot should respond to.
            return "retract"
        
        if vote.choice not in self.cast_votes.keys():
            self.cast_votes[vote.choice] = []
        
        self.cast_votes[vote.choice] += [vote.voter]
        
        return "success"

    def end(self):
        largest_number_of_votes = 0
        winning_choice = []
        
        for choice in self.cast_votes:
            number_of_votes = len(self.cast_votes[choice])
            
            if number_of_votes > largest_number_of_votes:
                largest_number_of_votes = number_of_votes
                winning_choice = [choice]
            
            elif number_of_votes == largest_number_of_votes:
                winning_choice += [choice]
        
        return random.choice(winning_choice) # Select a random item if there is a tie.

    def is_over(self):
        return time.time() >= self.ballot_end_time

    def trim(self):
        for choice in self.cast_votes:
            if self.cast_votes[choice] == []:
                self.cast_votes.pop(choice)