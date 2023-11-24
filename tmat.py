from bot import *
from democracy import *
import threading, regex

class TwitchMakesATAS:
    def __init__(self):
        self.is_active = True
        
        self.start_time = 0
        
        self.bot = TwitchBot()
        self.democracy = Democracy()

    def backtick_commands(self, command: str):
        if not command.startswith('`'): return
        match command:
            case "`help":
                self.bot.send_message("You can find out how to use the bot here: https://github.com/redstone59/TwitchMakesATAS/blob/main/README.md")
            case "`repo":
                self.bot.send_message("The GitHub repo can be found here: https://github.com/redstone59/TwitchMakesATAS")
            case "`timeleft":
                if self.democracy.is_purgatory():
                    self.bot.send_message("The timer is paused due to a lack of votes. Vote to start the timer again!")
                else:
                    self.bot.send_message("this has not been implemented yet. teehee :3")
            case "`uptime":
                uptime = int(time.time() - self.start_time)
                self.bot.send_message(f"TwitchMakesATAS has been active for {uptime//3600} hours, {(uptime//60)%60} minutes, and {uptime%60} seconds.")

    def parsing_loop(self):
        """
        Main loop of TwitchMakesATAS. Waits until a message is sent, then parses and runs the command.
        """
        while self.is_active:
            if self.bot.message_queue.empty():
                continue
            
            message = self.bot.message_queue.get()
            parsed_message = self.parse_message(message)
            
            if parsed_message is None:
                continue
            
            self.run_command(*parsed_message)
            

    def parse_message(self, message: Message):
        """
        Parses a `Message` object into a command and it's arguments.

        Args:
            message (Message): The message from Twitch chat.

        Returns:
            None: if the message cannot be a valid command.
            
            tuple:
                str: The name of the command.
                str: The arguments of the command.
        """
        message.contents = regex.sub(r"\s*,\s*", ",", message.contents.strip())
        split_command = message.contents.split(" ", 1) # Split after the first space
        
        command = split_command[0]
        
        self.backtick_commands(command)
        
        if len(split_command) <= 1:
            return None
        
        arguments = split_command[1].upper() # Remove case sensitivity from command arguments
        
        return command, arguments
    
    def run_command(self, command: str, arguments: str):
        match command:
            case "WRITE":
                pass
            case "REMOVE":
                pass
            case "INSERT":
                pass
            case "DELETE":
                pass
            case "IGNORE":
                pass
            case "REVERT":
                pass
            case "RETRACT":
                pass
            case "FRAME":
                pass
            case "PLAY":
                pass
            case "PIANO":
                pass
            case "REFRESH":
                pass
    
    def start(self):
        self.start_time = time.time()
        
        self.bot.connect("oauth:eminempussysoundeffect","TwitchMakesATAS","#redstone59")
        self.bot.send_message("owo")

        try:
            bot_thread = threading.Thread(target=self.bot.message_loop)
            democracy_thread = threading.Thread(target=self.democracy.democracy_loop)
            parsing_thread = threading.Thread(target=self.parsing_loop)
            
            bot_thread.start()
            #democracy_thread.start()
            parsing_thread.run()
        
        except KeyboardInterrupt:
            self.is_active = False
            
            self.bot.is_active = False
            self.bot.send_message("nya~!")
            self.bot.disconnect()