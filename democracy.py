import time, random, queue

class Vote:
    def __init__(self, voter: str, choice):
        self.voter = voter
        self.choice = choice

class YayOrNay:
    def __init__(self, yay_length: int, viewers: int, command, majority = 0.3):
        self.voters = []
        self.majority = int(viewers * majority)
        self.has_passed = False
        self.command = command
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
        
        if purgatory:
            self.ballot_end_time = ballot_length
        else:
            self.ballot_end_time = time.time() + ballot_length
        
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
                Any: The winning choice
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
        elif winning_choice == []:
            winning_choice = ""
        else:
            winning_choice = winning_choice[0]
        
        return winning_choice, largest_number_of_votes, is_tied

    def is_over(self):
        if self.purgatory:
            return False
        else:
            return time.time() >= self.ballot_end_time

    def time_left(self):
        return self.ballot_end_time - time.time()

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
        self.has_alerted = False
        
        self.manifest_queue = queue.Queue()
        self.current_ballot = Ballot(0x7fffffff, True)
        
        self.yay_vote_exists = False
        self.yay_vote = YayOrNay(0x7fffffff, 0x7fffffff, "")
        
        self.sequential_empty_ballots = 0
        self.empty_ballot_limit = 3

    def create_yay_vote(self, sender: str, command, viewers: int, yay_length = 30):
        if self.yay_vote_exists:
            self.manifest_queue.put(("message", "There is already a YAY vote on! Wait until that expires!"))
            return
        
        self.yay_vote_exists = True
        self.yay_vote = YayOrNay(yay_length, viewers, command)
        
        self.yay_vote.cast(sender)
        
        if self.yay_vote.has_passed:
            self.manifest_queue.put(("command", self.yay_vote.command))
            return
        
        self.manifest_queue.put(("message", f"{sender} has started a vote for {command}! Type 'YAY' to agree!"))
        self.manifest_queue.put(("message", f"There needs to be {self.yay_vote.majority} YAY votes to pass! It expires in {yay_length} seconds."))
        
        return

    def democracy_loop(self, ballot_length = 45):
        self.current_ballot = Ballot(ballot_length)
        
        while self.is_active:
            if not (self.has_alerted or self.is_purgatory()) and self.current_ballot.time_left() <= 10:
                self.manifest_queue.put(("message", "There is 10 seconds left on the vote!"))
                self.has_alerted = True
            
            if self.current_ballot.is_over():
                ballot_results = self.current_ballot.end()
                
                self.has_alerted = False
                
                if ballot_results[0] == "":
                    self.manifest_queue.put(("message", "No vote has won! Starting new vote..."))
                    self.sequential_empty_ballots += 1
                    self.current_ballot = Ballot(ballot_length)
                    
                    if self.sequential_empty_ballots >= self.empty_ballot_limit:
                        self.manifest_queue.put(("message", f"{self.empty_ballot_limit} unsuccessful votes in a row! Stopping timer..."))
                        self.current_ballot = Ballot(ballot_length, True)
                    continue
                
                self.manifest_queue.put(("command", ballot_results[0]))
                
                self.current_ballot = Ballot(ballot_length)
            
            if self.yay_vote_exists:
                if self.yay_vote.is_over():
                    self.manifest_queue.put(("message", f"The YAY vote for {self.yay_vote.command} has expired."))
                    self.yay_vote_exists = False
                
                if self.yay_vote.has_passed:
                    self.manifest_queue.put(("command", self.yay_vote.command))
                    self.yay_vote_exists = False
    
    def is_purgatory(self):
        return self.sequential_empty_ballots >= self.empty_ballot_limit