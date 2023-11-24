from bot import *
from democracy import *
import threading, regex

class TwitchMakesATAS:
    def __init__(self):
        self.is_active = True
        
        self.bot = TwitchBot()
        self.democracy = Democracy()

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
        
        if len(split_command) <= 1:
            return None
        
        command = split_command[0]
        arguments = split_command[1].upper() # Remove case sensitivity from command arguments
        
        return command, arguments
    
    def run_command(self, command: str, arguments: str):
        if command in ["WRITE", "REMOVE", "GAMER", "TEST"]:
            print("Command said:", command, arguments)
    
    def start(self):
        self.bot.connect("oauth:eminempussysoundeffect","TwitchMakesATAS","#redstone59")
        self.bot.send_message("owo")

        try:
            bot_thread = threading.Thread(target=self.bot.message_loop)
            democracy_thread = threading.Thread(target=self.democracy.democracy_loop)
            parsing_thread = threading.Thread(target=self.parsing_loop)
            
            bot_thread.start()
            #democracy_thread.start()
            parsing_thread.start()
        
        except KeyboardInterrupt:
            self.is_active = False
            
            self.bot.is_active = False
            self.bot.send_message("nya~!")
            self.bot.disconnect()