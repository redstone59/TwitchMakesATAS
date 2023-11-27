import os.path, sys, datetime

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(sys.argv[0]))
BUTTONS = "RLDUTSBA"

def bit(number: int, n: int):
    """
    Returns the `n`th bit from a number from right to left.

    Args:
        number (int): The number to find bits from.
        n (int): The bit index.

    Returns:
        int: 1 or 0.
    """
    return (number >> n - 1) & 1

def int_all(*vars):
    vars = list(vars)
    
    for x in range (len(vars)):
        vars[x] = int(vars[x])
        
    return tuple(vars)

class ToolAssistedSpeedrun:
    def __init__(self, metadata = "", frame_limit = 0):
        self.frames = []
        """
        The `frames` list is just going to be a list of numbers from 0-255
        Each index is a single frame. Each bit represents a button being pressed.
        
               RLDUTSBA
        131 -> 10000011
        
        Therefore 131 represents the buttons R, B, and A being pressed.
        """
        self.fm2_metadata = metadata
        self.frame_limit = frame_limit
    
    def backup(self, name: str, dir = os.path.join(CURRENT_DIRECTORY, "backups")):
        """
        Creates a backup of `self.frames`.

        Args:
            name (str): The name of the backup file.
            dir (str, optional): The directory to the backup file. Defaults to `.\\backups`
        """
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M_")
        
        with open(os.path.join(dir, f"{timestamp} {name}.rtas"), "bw") as backup_file:
            backup_file.write(bytearray(self.frames))
    
    def buttons_to_number(self, buttons: str):
        """
        Returns the number representation of a combination of buttons.
        Example: RBA -> `R.....BA` -> 131

        Args:
            buttons (str): The buttons to be changed.

        Raises:
            ValueError: if `buttons` contains characters other than `RLDUTSBA`.

        Returns:
            int: The equivalent buttons in number form.
        """
        if not self.is_valid_buttons(buttons):
            raise ValueError(f"Invalid buttons \"{buttons}\"")
        
        result = 0
        
        for button in BUTTONS:
            if button in buttons.upper():
                result += 1 << (7 - BUTTONS.index(button))
        
        return result
    
    def delete(self, frame: int, length = 1):
        """
        Deletes a range of frames, shifting frames ahead back.

        Args:
            frame (int): The starting frame.
            length (int, optional): Self-explanatory. Defaults to 1.
        """
        
        frame, length = int_all(frame, length)
        
        for i in range (length):
            if frame > len(self.frames): break
            del self.frames[frame]
    
    def export(self, name: str, dir = CURRENT_DIRECTORY):
        exported_tas_path = os.path.join(CURRENT_DIRECTORY, name + ".fm2")
        
        with open(exported_tas_path, "w") as fm2_file:
            fm2_file.write(self.fm2_metadata)
            
            for frame in self.frames:
                fm2_file.write("|0|")
                fm2_file.write(self.number_to_buttons(frame))
                fm2_file.write("|||\n")
    
    def insert(self, frame: int, length = 1, buttons = ""):
        """
        Inserts frames into the TAS, shifting frames ahead forward.

        Args:
            frame (int): The starting frame.
            length (int, optional): Self-explanatory. Defaults to 1.
            buttons (str, optional): The buttons to be pressed in the frames. Defaults to "" (empty frame).
        """
        
        frame, length = int_all(frame, length)
        
        inserted_frames = [self.buttons_to_number(buttons)]
        inserted_frames *= length
        
        self.frames = self.frames[:frame] + inserted_frames
        if not (frame > len(self.frames)):
            self.frames += self.frames[frame:]
    
    def is_valid_buttons(self, buttons: str):
        for button in buttons:
            if button.upper() not in BUTTONS:
                return False
        
        return True
    
    def load_backup(self, name: str, dir = os.path.join(CURRENT_DIRECTORY, "backups")):
        """
        Loads a backup file and sets `self.frames` to it.

        Args:
            name (str): The name of the backup file.
            dir (str, optional): Directory to the file. Defaults to `.\\backups`.
        """
        
        with open(os.path.join(dir, name + ".rtas"), "br") as backup_file:
            self.frames = list(backup_file.read())
    
    def number_to_buttons(self, number: int):
        """
        Turns a number into FM2 formatted buttons.
        Example: 131 -> `10000011` -> `R.....BA`

        Args:
            number (int): The number to change.

        Raises:
            ValueError: If `number` is not in the range 0 to 255.

        Returns:
            str: Button string.
        """
        if not (0 <= number <= 255):
            raise ValueError("number provided to function not in range 0-255")

        result_buttons = ""

        for x in range (8):
            if bit(number, 8 - x):
                result_buttons += BUTTONS[x]
            else:
                result_buttons += "."
        
        return result_buttons

    def overwrite(self, frame: int, buttons: str, length = 1):
        """
        Identical to `write()` but removes existing data from the frames.

        Args:
            frame (int): The starting frame
            buttons (str): The buttons to be written.
            length (int, optional): Self-explanatory. Defaults to 1.
        """
        frame, length = int_all(frame, length)
        
        if frame + length > len(self.frames): # Add frames if they are out of the bound of the frame list.
            self.frames += [0] * (frame + length - len(self.frames))
        
        for i in range (length):
            self.frames[frame + i] = self.buttons_to_number(buttons) # Set the frame to the inputs provided.

    def remove(self, frame: int, length = 1, buttons = "RLDUTSBA"):
        """
        Removes specific buttons from a range of frames in the TAS.

        Args:
            frame (int): The starting frame
            length (int, optional): Self-explanatory. Defaults to 1.
            buttons (str, optional): The buttons to be removed. Defaults to "RLDUTSBA".
        """
        
        frame, length = int_all(frame, length)
        
        for i in range (length):
            if frame + i > len(self.frames): # Skip frames that don't exist.
                break
            self.frames[frame + i] &= ~self.buttons_to_number(buttons) # Retain only the inputs that aren't being removed.

    def write(self, frame: int, buttons: str, length = 1, pattern = 0b1):
        """
        Writes certain buttons to a range of frames in the TAS, according to the pattern.

        Args:
            frame (int): The starting frame.
            buttons (str): The buttons to write.
            length (int, optional): Self-explanatory. Defaults to 1.
            pattern (int, optional): Binary representation of the pattern to write. Defaults to `0b1` (always on).
        """
        
        frame, length, pattern = int_all(frame, length, pattern)
        
        pattern_length = len(bin(pattern)) - 2
        
        if frame + length > len(self.frames): # Add frames if they are out of the bound of the frame list.
            self.frames += [0] * (frame + length - len(self.frames))
        
        for i in range (length):
            if bit(pattern, pattern_length - (i % pattern_length)):
                self.frames[frame + i] |= self.buttons_to_number(buttons) # Add the inputs provided to the frame.