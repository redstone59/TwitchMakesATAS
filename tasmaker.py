import os.path, sys

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(sys.argv[0]))

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

class ToolAssistedSpeedrun:
    def __init__(self, metadata: str):
        self.fm2_metadata = metadata
        self.frames = []
        """
        The `frames` list is just going to be a list of numbers from 0-255
        Each index is a single frame. Each bit represents a button being pressed.
        
               RLDUTSBA
        131 -> 10000011
        
        Therefore 131 represents the buttons R, B, and A being pressed.
        """
    
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
            raise ValueError(f"Invalid buttons {buttons}")
        
        result = 0
        
        for button in [*"RLDUTSBA"]:
            if button in buttons.upper():
                result += 1 << (7 - [*"RLDUTSBA"].index(button))
        
        return result
    
    def export(self, name: str, dir = CURRENT_DIRECTORY):
        exported_tas_path = os.path.join(CURRENT_DIRECTORY, f"{name}.fm2")
        
        with open(exported_tas_path, "w") as fm2_file:
            fm2_file.write(self.fm2_metadata)
            
            for frame in self.frames:
                fm2_file.write("|0|")
                fm2_file.write(self.number_to_buttons(frame))
                fm2_file.write("|||\n")
    
    def is_valid_buttons(self, buttons: str):
        for button in buttons:
            if button not in [*"RLDUTSBA"]:
                return False
        
        return True
    
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
                result_buttons += [*"RLDUTSBA"][x]
            else:
                result_buttons += "."
        
        return result_buttons

    def write(self, frame: int, buttons: str, length = 1, pattern = 0b1):
        pattern_length = len(bin(pattern)) - 2