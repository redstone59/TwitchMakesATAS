import socket, threading, time, math, random
import integration as nes
import tasmaker as tas
import gui

class Message:
    def __init__(self, sender: str, contents: str):
        self.sender = sender
        self.contents = contents
    
    def __str__(self):
        return f"{self.sender}: {self.contents}"
    
    # TODO: function for if sender is a mod or bot?

class Vote:
    def __init__(self, voter: str, choice: str, cast_time: float):
        self.voter = voter
        self.choice = choice
        self.cast_time = cast_time
        
class Ballot:
    def __init__(self, ballot_length: int):
        self.cast_votes = []
        self.ballot_end_time = time.time() + ballot_length

# Should the above classes be moved to a new file? Probably.        

class TwitchBot:
    def __init__(self):
        self.sock = socket.socket()
        
        self.channel = ""
        
        self.is_active = True
        self.can_speak = True
        
        self.messages_last_minute = 0
        self.message_queue = [] # This feels clunky, replace?
        self.message_limit = 100
        
        self.sequential_empty_ballots = 0
    
    def connect(self, token: str, nickname: str, channel: str, server = 'irc.chat.twitch.tv', port = 6667):
        """
        Connects TwitchMakesATAS to the Twitch Chat API.

        Args:
            token (str): OAuth token used to connect with Twitch API.
            nickname (str): Name of the account being used.
            channel (str): Name of the Twitch channel being connected to.
            server (str, optional): The URL of the server being connected to. Defaults to 'irc.chat.twitch.tv'.
            port (int, optional): The server port being connected to. Defaults to 6667.
        """
        
        self.channel = channel
        
        self.sock.connect((server, port))

        self.sock.send(f"PASS {token}\n".encode('utf-8'))
        self.sock.send(f"NICK {nickname}\n".encode('utf-8'))
        self.sock.send(f"JOIN {channel}\n".encode('utf-8'))
        
        print("TwitchMakesATAS connected")
    
    def message_loop(self):
        """
        Starts the bot's loop of checking for new messages and responding.
        """
        while self.is_active:
            response = self.sock.recv(2048).decode('utf-8')

            if response.startswith('PING'):
                self.sock.send("PONG\n".encode('utf-8'))

            message = response.split("#")
            
            if len(message) > 1:
                sender = message[0].split('!')[0][1:]
                contents = message[1].split(':')[1:]
                contents = ':'.join(contents)
                
                print(Message(sender, contents))
                self.message_queue += [Message(sender, contents)] # Should probably respond to messages as soon as they arrive, like in the previous version.
    
    def send_message(self, message: str):
        self.messages_last_minute += 1
        print(f"Sent message: '{message}'. Messages sent in the last minute: {self.messages_last_minute}")
        if self.messages_last_minute >= self.message_limit:
            self.can_speak = False
            return # Is this a minor optimisation? Why check if it can speak after if we just changed it to no?
        if self.can_speak:
            self.sock.send(f"PRIVMSG {self.channel} :{message}\n".encode('utf-8'))
    
    def timer_loop(self):
        while self.is_active:
            current_time = time.time()
            
            if int(current_time) % 60 == 0:
                self.messages_last_minute = 0
                self.can_speak = True
            
            if not (self.sequential_empty_ballots < self.empty_ballot_limit):
                continue

tmat = TwitchBot()
tmat.connect("oauth:veryrealtwitchapitoken","TwitchMakesATAS","#redstone59")
tmat.send_message("owo")
tmat.message_loop()