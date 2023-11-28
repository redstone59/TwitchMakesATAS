from bot import *
from democracy import *
from tasmaker import *
from gui import *
import threading, regex

import integration as nes

class Instruction:
    def __init__(self, command: str, arguments: tuple):
        self.command = command
        self.arguments = arguments
    
    def __getitem__(self, key):
        if key == 0:
            return self.command
        elif key == 1:
            return self.arguments
        
        raise KeyError("Instruction only contains 2 objects.")
    
    def __str__(self):
        return f"{self.command.upper()} {','.join(self.arguments)}"

class TwitchMakesATAS:
    def __init__(self, metadata):
        self.is_active = True
        self.thank_you = {} # Counts the amount of times a viewer contributes to a winning vote. This is literally JUST for a twitter post
        
        self.start_time = 0
        self.vote_count = 0
        self.last_viewed_frame = 0
        
        self.bot = TwitchBot()
        self.democracy = Democracy()
        self.tas = ToolAssistedSpeedrun(metadata)
        self.gui = MasterWindow()

    def backtick_commands(self, command: str):
        if not command.startswith('`'):
            return
        
        match command:
            case "`help":
                self.bot.send_message("You can find out how to use the bot here: https://github.com/redstone59/TwitchMakesATAS/blob/main/README.md")
            case "`repo":
                self.bot.send_message("The GitHub repo can be found here: https://github.com/redstone59/TwitchMakesATAS")
            case "`timeleft":
                if self.democracy.is_purgatory():
                    self.bot.send_message("The timer is paused due to a lack of votes. Vote to start the timer again!")
                else:
                    self.bot.send_message(f"There is {int(self.democracy.current_ballot.time_left())} seconds remaining on the vote!")
            case "`uptime":
                uptime = int(time.time() - self.start_time)
                self.bot.send_message(f"TwitchMakesATAS has been active for {uptime // 3600} hours, {(uptime // 60) % 60} minutes, and {uptime % 60} seconds.")
    
    def disconnect(self):
        try: # The "turning off" part of the bot also throws an error from the socket? Let's just sweep it under the rug.
            self.is_active = False
            self.bot.is_active = False
            self.democracy.is_active = False
            
            self.bot.is_active = False
            self.bot.send_message("nya~!")
            self.bot.disconnect()
        except ConnectionAbortedError:
            pass
        
        print(self.thank_you_string() + "\n\n") # Just in case that error shows up.
        
    def manifest_loop(self):
        while self.is_active:
            if self.democracy.manifest_queue.empty(): # This should mean I can KeyboardInterrupt at any time, since .get() blocks.
                continue
            
            democracy_manifest = self.democracy.manifest_queue.get() # What is the charge? Eating a meal? A succulent Chinese meal?
            
            match democracy_manifest[0]:
                case "message":
                    self.bot.send_message(democracy_manifest[1])
                    
                case "command":
                    self.run_command(democracy_manifest[1])
                
                case "thankyou":
                    self.update_thank_you(democracy_manifest[1])
                
                case "newballot":
                    self.tk_queue.put(Instruction("vote", self.democracy.current_ballot.cast_votes))
                    if self.democracy.current_ballot.purgatory:
                        self.gui.tk_queue.put(Instruction("time", "paused"))
                    else:
                        self.gui.tk_queue.put(Instruction("time", time.time() + 45))
    
    def parsing_loop(self):
        """
        Main loop of TwitchMakesATAS. Waits until a message is sent, then parses and runs the instruction.
        """
        while self.is_active:
            if self.bot.message_queue.empty():
                continue
            
            message = self.bot.message_queue.get()
            parsed_message = self.parse_message(message)
            
            if parsed_message is None:
                continue
            
            vote_result = self.democracy.current_ballot.cast_vote(Vote(message.sender, parsed_message))
            
            if vote_result == "success":
                number_of_votes = len(self.democracy.current_ballot.cast_votes[parsed_message])
                self.bot.send_message(f"{message.sender} has just voted for {parsed_message}! It now has {number_of_votes} vote{'s' if number_of_votes > 1 else ''}!")
            elif vote_result == "retract":
                self.bot.send_message(f"{message.sender} has just retracted their vote!")
            
            self.gui.tk_queue.put(("vote", self.democracy.current_ballot.cast_votes))

    def parse_message(self, message: Message):
        """
        Parses a `Message` object into a command and it's arguments.

        Args:
            message (Message): The message from Twitch chat.

        Returns:
            None: if the message cannot be a valid instruction.
            
            str: "" if the vote is to be retracted.
            
            Instruction: if the instruction is valid.
        """
        message.contents = regex.sub(r"\s*,\s*", ",", message.contents.strip())
        split_instruction = message.contents.split(" ", 1) # Split after the first space
        
        command = split_instruction[0]
        
        self.backtick_commands(command)
        
        if command not in ["WRITE", "REMOVE", "OVERWRITE", "INSERT", "DELETE", "IGNORE", "RETRACT", "FRAME", "PLAY", "PIANO", "REFRESH"]:
            return
        
        if command == "RETRACT":
            return ""
        
        if len(split_instruction) <= 1:
            if command in ["PLAY", "REFRESH"]:
                self.democracy.create_yay_vote(message.sender, Instruction(command, ()), self.bot.viewer_count(), 30)
                return
            
            return Instruction(command, ())
        
        arguments = split_instruction[1].upper() # Remove case sensitivity from command arguments
        arguments = tuple(arguments.split(',')) # Turn command arguments into a tuple
        
        if command in ["FRAME", "PLAY", "PIANO", "REFRESH"]:
            self.democracy.create_yay_vote(message.sender, Instruction(command, arguments), self.bot.viewer_count())
            return
        
        return Instruction(command, arguments)
    
    def run_command(self, instruction: Instruction):
        if type(instruction) != Instruction:
            print("Invalid argument passed to run_command:", instruction)
            return
        
        try:
            match instruction.command:
                case "WRITE":
                    if len(instruction.arguments) <= 1:
                        return
                    
                    self.tas.write(*instruction.arguments)
                
                case "OVERWRITE":
                    if len(instruction.arguments) <= 1:
                        return
                    
                    self.tas.overwrite(*instruction.arguments)

                case "REMOVE":
                    if len(instruction.arguments) <= 0:
                        return
                    
                    self.tas.remove(*instruction.arguments)
                    
                case "INSERT":
                    if len(instruction.arguments) <= 0:
                        return
                    
                    self.tas.insert(*instruction.arguments)
                
                case "DELETE":
                    if len(instruction.arguments) <= 0:
                        return
                    
                    self.tas.delete(*instruction.arguments)
                
                case "IGNORE":
                    pass
                
                case "REVERT":
                    pass
                
                case "FRAME":
                    if instruction.arguments[0][0] in ["+", "-"] and instruction.arguments[0][1:].isdigit():
                        instruction.arguments = tuple(self.last_viewed_frame + int(instruction.arguments[0]))
                    
                    if not all([x.isdigit() for x in instruction.arguments]):
                        return
                    
                    if len(instruction.arguments) <= 0:
                        return
                    
                    self.tas.export("twitch")
                    self.bot.send_message(f"Going to frame {instruction.arguments[0]}...")
                    nes.frame(*[int(x) for x in instruction.arguments])
                    
                    self.last_viewed_frame = instruction.arguments[0]
                    return # To not increment the vote counter.
                
                case "PLAY":
                    instruction.arguments = instruction.arguments[::-1] # Reverse the tuple. For some reason the 'start' and 'end' arguments are the wrong way around
                    
                    if not all([x.isdigit() for x in instruction.arguments]):
                        return
                    
                    self.tas.export("twitch")
                    
                    if len(instruction.arguments) == 1:
                        self.bot.send_message(f"Playing from frame {instruction.arguments[0]}...")
                        nes.play(0, int(instruction.arguments[0]))
                        return
                    elif len(instruction.arguments) == 2:
                        self.bot.send_message(f"Playing from frame {instruction.arguments[1]} until frame {instruction.arguments[0]}...")
                    else:
                        self.bot.send_message("Playing whole movie...")
                    
                    nes.play(*[int(x) for x in instruction.arguments])
                    
                    return # To not increment the vote counter.
                
                case "PIANO":
                    if not all([x.isdigit() for x in instruction.arguments]):
                        return
                    
                    if len(instruction.arguments) <= 0:
                        return
                    
                    self.gui.tk_queue.put(Instruction("piano", (self.tas.frames, int(instruction.arguments[0]))))
                    
                    return # To not increment the vote counter.
                
                case "REFRESH":
                    self.gui.tk_queue.put(Instruction("piano", (self.tas.frames, -1)))
                    
                    return # To not increment the vote counter.
        
        except ValueError:
            pass
        
        self.tas.backup(f"vote_{self.vote_count}")
        self.vote_count += 1
        
        self.gui.tk_queue.put(Instruction("vote", self.democracy.current_ballot.cast_votes))
    
    def start(self, token: str):
        self.start_time = time.time()
        
        self.bot.connect(token ,"TwitchMakesATAS","#redstone59")
        self.bot.send_message("owo")

        nes.file = "twitch"
        
        try:
            bot_thread = threading.Thread(target=self.bot.message_loop)
            democracy_thread = threading.Thread(target=self.democracy.democracy_loop)
            parsing_thread = threading.Thread(target=self.parsing_loop)
            manifest_thread = threading.Thread(target=self.manifest_loop)
            
            bot_thread.start()
            democracy_thread.start()
            parsing_thread.start()
            manifest_thread.start()
            
            try:
                self.gui.main_loop()
            except Exception as e:
                self.bot.send_message(f"Error! {str(e.__class__)[:-2][8:]}: {e}")
        
        except KeyboardInterrupt:
            pass
        
        self.disconnect()
    
    def thank_you_string(self):
        result = ""
        sorted_thank_you = {}
        intermediate_voter_string = []
        
        for x in sorted(self.thank_you, key=self.thank_you.get, reverse=True):
            sorted_thank_you[x] = self.thank_you[x]
        
        for voter in sorted_thank_you:
            intermediate_voter_string += [f"{voter}: {sorted_thank_you[voter]}"]
        
        total_length = max(len(x) for x in intermediate_voter_string) * 2 + 2
        if total_length < 44:
            total_length = 44
        
        for x in range (len(intermediate_voter_string)):
            shift_amount = total_length // 2 - intermediate_voter_string[x].index(':') + 1
            intermediate_voter_string[x] = " " * shift_amount + intermediate_voter_string[x]
        
        result = f"\n{'THANK YOU': ^{total_length}}\n"
        result += f"{' to the following viewers for contributing!': ^{total_length}}\n"
        result += "-" * total_length + "\n"
        
        for x in intermediate_voter_string:
            result += f"{x}\n"
        
        result += "-" * total_length + "\n"
        
        uptime = int(time.time() - self.start_time)
        
        result += f"{'TwitchMakesATAS was live for': ^{total_length}}\n"
        result += f'{f"{uptime // 3600} hours, {(uptime // 60) % 60} minutes, and {uptime % 60} seconds.": ^{total_length}}\n'
        
        result += f"{f'and got {self.vote_count} votes': ^{total_length}}"
        
        return result
    
    def update_thank_you(self, winning_voters):
        for voter in winning_voters:
            if voter == "":
                continue
            
            if voter not in self.thank_you.keys():
                self.thank_you[voter] = 0
            
            self.thank_you[voter] += 1