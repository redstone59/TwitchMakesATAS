import tkinter as tk
from tkinter import ttk
import time, queue, threading

BUTTONS = "RLDUTSBA"

def scale_font(font: tuple, size: int, bold = False):
    """
    Returns the tuple for a font, scaled accordingly.

    Args:
        font (tuple): The font tuple consisting of the font name and it's scale.
        size (int): The size of the font in points.
        bold (bool, optional): Self-explanatory. Defaults to False.

    Returns:
        tuple: The font tuple to be passed into tkinter.
    """
    font_name = font[0]
    if bold:
        font_name += " Bold"
    font_size = int(size * font[1])
    
    return font_name, font_size

class PianoRoll:
    def __init__(self, host: tk.Tk, font: tuple):
        self.is_active = True
        self.is_updating = False
        self.current_frame = 0
        self.displayed_frames = 30
        
        self.font = font
        
        self.piano_roll = tk.Toplevel(host)
        self.piano_roll.geometry("270x1000+50+50")
        self.piano_roll.title("TAS Piano Roll")
        
        self.set_up_labels()
        self.update_piano_roll([], 0)
    
    def main_loop(self):
        while self.is_active:
            self.piano_roll.update()
    
    def set_up_labels(self):
        tk.Label(self.piano_roll,
                 text = "Piano Roll",
                 font = scale_font(self.font, 28, True)
                ).grid(column = 0, row = 0, columnspan = 9)
        tk.Label(self.piano_roll,
                 text = "Frame #",
                 font = scale_font(self.font, 20)
                ).grid(column = 0, row = 1)
        
        for x in range(8):
            tk.Label(self.piano_roll,
                     text = BUTTONS[x],
                     font = scale_font(self.font, 20)
                    ).grid(column = x + 1, row = 1)
        
        for i in range (50):
            for j in range (9):
                tk.Frame(self.piano_roll,
                         borderwidth = 5,
                         relief = "ridge"
                        ).grid(column = j + 1, row = i + 2)
    
    def update_piano_roll(self, tas_list: list, start_frame = -1):
        if start_frame < 0:
            start_frame = self.current_frame
        
        self.current_frame = start_frame
        
        if self.is_updating: return
        self.is_updating = True
        
        n = 0
        
        for label in self.piano_roll.grid_slaves():
            if int(label.grid_info()["row"]) > 1: label.destroy()
            n += 1
            if n % 18 == 0: self.piano_roll.update() # I honestly don't know why this line existed, but I copied it as is.
        
        for x in range(self.displayed_frames):
            tk.Label(self.piano_roll,
                     text = f"{start_frame + x}".zfill(8),
                     font = scale_font(self.font, 20),
                     bg = ["white", "grey90"][x % 2],
                     highlightthickness = 1,
                     highlightbackground = "grey50",
                     highlightcolor = "grey50"
                    ).grid(column = 0, row = x + 2)
            
            for button in BUTTONS:
                input = " "
                index = BUTTONS.index(button)
                
                if start_frame + x < len(tas_list):
                    frame = tas_list[start_frame + x]
                    if (frame >> index) & 1:
                        input = button
                
                tk.Label(self.piano_roll,
                         text = input,
                         font = scale_font(self.font, 20, True),
                         bg = ["white", "grey90"][x % 2],
                         highlightthickness = 1,
                         highlightbackground = "grey50",
                         highlightcolor = "grey50"
                        ).grid(column = 1 + index, row = x + 2)
            
            self.piano_roll.update()
        
        self.is_updating = False

class VoteDisplay:
    def __init__(self, host: tk.Tk, font: tuple):
        self.is_active = True
        
        self.font = font
        
        self.vote_window = tk.Toplevel(host)
        self.vote_window.geometry("480x720+2040+50")
        self.vote_window.title("TAS Votes")
        
        self.end_time = time.time() + 45
        self.vote_range = 17
        
        self.time_label = tk.Label(self.vote_window,
                                   text = "45 seconds",
                                   font = scale_font(self.font, 28)
                                   )
        
        self.set_up_labels()
        self.update_votes({})
    
    def main_loop(self):
        while self.is_active:
            self.update_time()
            self.vote_window.update()
      
    def set_up_labels(self):
        tk.Label(self.vote_window,
                 text = "Votes",
                 font = scale_font(self.font, 28, True)
                ).grid(column = 1, row = 0, columnspan = 2)
        tk.Label(self.vote_window,
                 text = "Vote",
                 font = scale_font(self.font, 20)
                ).grid(column = 1, row = 1)
        tk.Label(self.vote_window,
                 text = "# of votes",
                 font = scale_font(self.font, 20)
                ).grid(column = 2, row = 1)
        tk.Label(self.vote_window,
                 text = " ",
                 font = scale_font(self.font, 20)
                ).grid(column = 0, row = 1)
        tk.Label(self.vote_window,
                 text = " ",
                 font = scale_font(self.font, 20)
                ).grid(column = 3, row = 1)
        tk.Label(self.vote_window,
                 text = "Time Left",
                 font = scale_font(self.font, 32, True)
                ).grid(column = 1, row = 3 + self.vote_range, columnspan = 2)
        tk.Label(self.vote_window,
                 text = " ",
                 font = scale_font(self.font, 20)
                ).grid(column = 1, row = 2 + self.vote_range, columnspan = 2)
        
        self.time_label.grid(column = 1, row = 4 + self.vote_range, columnspan = 2)
    
    def update_time(self):
        if type(self.end_time) == str:
            self.time_label["text"] = "Voting paused!"
            return
        
        self.time_label["text"] = str(int(self.end_time - time.time())) + " seconds"
    
    def update_votes(self, vote_dict: dict):
        sorted_votes = {}
        
        for x in sorted(vote_dict, key=vote_dict.get, reverse=True):
            sorted_votes[x] = vote_dict[x]
        
        for label in self.vote_window.grid_slaves():
            self.update_time()
            if 1 < int(label.grid_info()["row"]) <= self.vote_range:
                label.destroy()
        
        keys = list(sorted_votes.keys())[:self.vote_range]
        
        for x in range(self.vote_range):
            self.update_time()
            
            if x > 30: break
            if x < len(sorted_votes):
                command = keys[x]
                count = str(len(sorted_votes[command]))
            else:
                command = " "
                count = " "
            
            tk.Label(self.vote_window,
                     text = f"{command:>100}"[-26:],
                     font = scale_font(self.font, 20),
                     bg = ["white", "grey90"][x % 2],
                     highlightthickness = 1,
                     highlightcolor = "grey50",
                     highlightbackground= "grey50"
                     ).grid(column = 1, row = 2 + x, sticky = "E")
            tk.Label(self.vote_window,
                     text = f"{count:<20}"[:10],
                     font = scale_font(self.font, 20),
                     bg = ["white", "grey90"][x % 2],
                     highlightthickness = 1,
                     highlightcolor = "grey50",
                     highlightbackground= "grey50"
                     ).grid(column = 2, row = 2 + x, sticky = "W")

class MasterWindow:
    def __init__(self, font_name = "Courier New", scale = 0.75):
        self.tk_queue = queue.Queue()
        self.is_active = True
        
        self.font = (font_name, scale)
        
        self.master = tk.Tk()
        self.master.withdraw()
        
        self.vote = VoteDisplay(self.master, self.font)
        self.piano_roll = PianoRoll(self.master, self.font)
        
    def main_loop(self):
        try:
            while self.is_active:
                self.vote.main_loop()
                self.piano_roll.piano_roll.update()
                self.master.update()
                
                if not self.tk_queue.empty():
                    instruction = self.tk_queue.get()
                    
                    match instruction[0]:
                        case "vote":
                            self.vote.update_votes(instruction[1])
                        case "piano":
                            self.piano_roll.update_piano_roll(instruction[1])
                        case "time":
                            self.vote.end_time = time.time() + instruction[1]
                            self.vote.update_time()
        
        except KeyboardInterrupt:
            self.is_active = False
            self.vote.is_active = False
            self.piano_roll.is_active = False
            return