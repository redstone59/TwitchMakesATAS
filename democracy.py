import time, random

class Vote:
    def __init__(self, voter: str, choice: str):
        self.voter = voter
        self.choice = choice.strip()

class YayOrNay:
    def __init__(self, yay_length: int, viewers: int, majority = 0.3):
        self.voters = []
        self.majority = viewers * majority
        self.has_passed = False
        self.yay_end_time = time.time() + yay_length
    
    def cast(self, voter: str):
        if voter not in self.voters:
            self.voters += [voter]
            
            if len(self.voters) >= self.majority:
                self.has_passed = True
    
    def is_over(self):
        return time.time() >= self.yay_end_time

class Ballot:
    def __init__(self, ballot_length: int, purgatory = False):
        self.cast_votes = {}
        self.ballot_end_time = ballot_length
        self.purgatory = purgatory
    
    def cast_vote(self, vote: Vote):
        """
        Casts a `Vote` into the `Ballot`.

        Args:
            vote (Vote): The vote being cast.

        Returns:
            "retract": If the vote is empty.
            "success": If the vote gets counted.
        """
        
        if self.purgatory:
            self.ballot_end_time += time.time()
            self.purgatory = False
        
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
        """
        Ends the `Ballot` being run.

        Returns:
            tuple:
                str: The winning choice
                int: The number of votes it received
                bool: If there was a tie
        """
        largest_number_of_votes = 0
        winning_choice = []
        
        for choice in self.cast_votes:
            number_of_votes = len(self.cast_votes[choice])
            
            if number_of_votes > largest_number_of_votes:
                largest_number_of_votes = number_of_votes
                winning_choice = [choice]
            
            elif number_of_votes == largest_number_of_votes:
                winning_choice += [choice]
        
        is_tied = len(winning_choice) > 1
        
        if is_tied:
            winning_choice = random.choice(winning_choice)
        
        if winning_choice == []:
            winning_choice = ""
        
        return winning_choice, largest_number_of_votes, is_tied

    def is_over(self):
        return time.time() >= self.ballot_end_time

    def trim(self):
        empty_votes = []
        
        for choice in self.cast_votes:
            if self.cast_votes[choice] == []:
                empty_votes += [choice]
        
        for choice in empty_votes:
            self.cast_votes.pop(choice)

class Democracy:
    def __init__(self):
        self.is_active = True
        
        self.yay_vote_exists = False
        self.yay_vote = YayOrNay(0x7fffffff, 0x7fffffff)
        
        self.sequential_empty_ballots = 0
        self.empty_ballot_limit = 3

    def create_yay_vote(self, yay_length = 30):
        if self.yay_vote_exists:
            return "existant"
        
        self.yay_vote_exists = True
        self.yay_vote = YayOrNay(yay_length)
        
        return "success"

    def democracy_loop(self, ballot_length = 45):
        current_ballot = Ballot(ballot_length)
        
        while self.is_active:
            if current_ballot.is_over():
                ballot_results = current_ballot.end()
                
                if ballot_results[0] == "":
                    self.sequential_empty_ballots += 1
                
                if self.sequential_empty_ballots >= self.empty_ballot_limit:
                    current_ballot = Ballot(ballot_length, True)
                    continue
                
                current_ballot = Ballot(ballot_length)
            
            if self.yay_vote_exists:
                if self.yay_vote.is_over() or self.yay_vote.has_passed:
                    self.yay_vote_exists = False
