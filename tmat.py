from bot import *
from democracy import *
from tasmaker import *
import threading, regex

import integration as nes
# import gui

class Instruction:
    def __init__(self, command: str, arguments: tuple):
        self.command = command
        self.arguments = arguments
    
    def __str__(self):
        return f"{self.command.upper()} {','.join(self.arguments)}"

class TwitchMakesATAS:
    def __init__(self, metadata):
        self.is_active = True
        self.thank_you = {} # Counts the amount of times a viewer contributes to a winning vote. This is literally JUST for a twitter post
        
        self.start_time = 0
        self.vote_count = 0
        
        self.bot = TwitchBot()
        self.democracy = Democracy()
        self.tas = ToolAssistedSpeedrun(metadata)
        
        self.tk_queue = queue.Queue()
        self.last_viewed_frame = 0

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
    '''
    def gui_loop(self):
        """
        Main loop of the GUI. Could do with a rewrite at some point.
        """
        while self.is_active:
            
            gui.update_time()
            gui.master.update()
            gui.vote.update()
            gui.pr.update()
            
            if self.tk_queue.empty():
                continue
            
            tk_instruction = self.tk_queue.get()
            
            match tk_instruction.command:
                case "vote":
                    gui.update_votes(self.democracy.current_ballot.cast_votes)
                case "piano":
                    if tk_instruction.arguments == ():
                        gui.update_piano_roll()
                    else:
                        gui.update_piano_roll(tk_instruction.arguments[0])
                case "time":
                    gui.update_time()
    '''

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
            
            self.tk_queue.put(Instruction("vote", ()))

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
        
        if command not in ["WRITE", "REMOVE", "INSERT", "DELETE", "IGNORE", "RETRACT", "FRAME", "PLAY", "PIANO", "REFRESH"]:
            return
        
        if command == "RETRACT":
            return ""
        
        if len(split_instruction) <= 1:
            if command in ["PLAY", "PIANO", "REFRESH"]:
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
                    if not all([x.isdigit() for x in instruction.arguments]):
                        return
                    
                    if len(instruction.arguments) <= 0:
                        return
                    
                    self.tas.export("twitch")
                    self.bot.send_message(f"Going to frame {instruction.arguments[0]}...")
                    nes.frame(*[int(x) for x in instruction.arguments])
                
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
                        self.bot.send_message(f"Playing from frame {instruction.arguments[1]} until frame {instruction.arguments[0]}")
                    else:
                        self.bot.send_message("Playing whole movie...")
                    
                    nes.play(*[int(x) for x in instruction.arguments])
                
                case "PIANO":
                    if not all([x.isdigit() for x in instruction.arguments]):
                        return
                    
                    if len(instruction.arguments) <= 0:
                        return
                    
                    self.tk_queue.put(Instruction("piano", *[int(x) for x in instruction.arguments]))
                
                case "REFRESH":
                    self.tk_queue.put(Instruction("piano", ()))
        
        except ValueError:
            pass
        
        self.tas.backup(f"vote_{self.vote_count}")
        self.vote_count += 1
        
        self.tk_queue.put(Instruction("vote", ()))
    
    def start(self, token: str):
        self.start_time = time.time()
        
        self.bot.connect(token ,"TwitchMakesATAS","#redstone59")
        self.bot.send_message("owo")

        nes.file = "twitch"
        
        try:
            bot_thread = threading.Thread(target=self.bot.message_loop)
            democracy_thread = threading.Thread(target=self.democracy.democracy_loop)
            parsing_thread = threading.Thread(target=self.parsing_loop)
            # gui_thread = threading.Thread(target=self.gui_loop)
            
            bot_thread.start()
            democracy_thread.start()
            parsing_thread.start()
            # gui_thread.start()
            
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
        
        except KeyboardInterrupt:
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
    
    def thank_you_string(self):
        result = ""
        sorted_thank_you = {}
        intermediate_voter_string = []
        
        for x in sorted(self.thank_you, key=self.thank_you.get, reverse=True):
            sorted_thank_you[x] = self.thank_you[x]
        
        for voter in sorted_thank_you:
            intermediate_voter_string += [f"{voter}: {sorted_thank_you[voter]}"]
        
        total_length = max(len(x) for x in intermediate_voter_string) + 2
        if total_length < 44: total_length = 44
        
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