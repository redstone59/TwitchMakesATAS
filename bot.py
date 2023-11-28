import socket, time
import queue

class Message:
    def __init__(self, sender: str, contents: str):
        self.sender = sender
        self.contents = contents.replace("\n","")
    
    def __str__(self):
        return f"{self.sender}: {self.contents}"
    
    # TODO: function for if sender is a mod or bot?

class TwitchBot:
    def __init__(self):
        self.sock = socket.socket()
        
        self.channel = ""
        self.viewer_list = {}
        self.viewer_expiry = 120
        
        self.can_speak = True
        self.is_active = True
        
        self.time_of_last_message = time.time()
        self.messages_last_minute = 0
        self.message_queue = queue.Queue()
        self.message_limit = 100
    
    def connect(self, token: str, nickname: str, channel: str, server = 'irc.chat.twitch.tv', port = 6667):
        """
        Connects the `TwitchBot` to the Twitch Chat API.

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
        
        print("Bot connected")
    
    def disconnect(self):
        """
        Disconnects the `TwitchBot` from the Twitch Chat API.
        """
        
        self.is_active = False
        self.sock.send("PART\n".encode('utf-8'))
        self.sock.close()
    
    def message_loop(self):
        """
        Starts the bot's loop of checking for new messages and responding.
        """
        
        while self.is_active:
            if time.time() - self.time_of_last_message >= 60:
                self.messages_last_minute = 0
                self.can_speak = True
                self.time_of_last_message = time.time()
            
            response = self.sock.recv(2048).decode('utf-8')

            if response.startswith('PING'):
                self.sock.send("PONG\n".encode('utf-8'))

            message = response.split("#")
            
            if len(message) > 1:
                sender = message[0].split('!')[0][1:]
                contents = message[1].split(':')[1:]
                contents = ':'.join(contents)
                
                print(Message(sender, contents))
                
                self.update_viewer_list(sender)
                self.message_queue.put(Message(sender, contents))
    
    def send_message(self, message: str):
        if self.messages_last_minute >= self.message_limit:
            self.can_speak = False
            return # Is this a minor optimisation? Why check if it can speak after if we just changed it to no?
        
        self.messages_last_minute += 1
        print(f"Sent message: '{message}'. Messages sent in the last minute: {self.messages_last_minute}")
        
        if self.can_speak:
            self.sock.send(f"PRIVMSG {self.channel} :{message}\n".encode('utf-8'))
            
    def update_viewer_list(self, sender: str):
        inactive_viewers = []
        
        for viewer in self.viewer_list:
            if time.time() > self.viewer_list[viewer]:
                inactive_viewers += [viewer]
        
        for viewer in inactive_viewers:
            del self.viewer_list[viewer]
        
        if sender != "":
            self.viewer_list[sender] = time.time() + self.viewer_expiry
        
        print("Current viewers:", self.viewer_count())
    
    def viewer_count(self):
        return len(self.viewer_list)