# Table of Contents
- [Table of Contents](#table-of-contents)
- [How to use TwitchMakesATAS](#how-to-use-twitchmakesatas)
  - [TAS Votes](#tas-votes)
  - [Other Votes](#other-votes)
- [Commands](#commands)
  - [Major Syntax Note](#major-syntax-note)
  - [General Commands](#general-commands)
    - [\`help](#help)
    - [\`repo](#repo)
    - [\`timeleft](#timeleft)
    - [\`uptime](#uptime)
  - [TAS Commands](#tas-commands)
    - [WRITE frame,buttons,\[length=1\],\[pattern=1\]](#write-framebuttonslength1pattern1)
    - [REMOVE frame,length,\[buttons="abstudlr"\]](#remove-framelengthbuttonsabstudlr)
    - [INSERT frame,\[buttons=""\]](#insert-framebuttons)
    - [DELETE frame](#delete-frame)
    - [IGNORE](#ignore)
    - [REVERT tas-name](#revert-tas-name)
    - [RETRACT](#retract)
    - [FRAME frame](#frame-frame)
    - [PLAY \[start=0\] \[end=length of the movie\]](#play-start0-endlength-of-the-movie)
    - [PIANO frame](#piano-frame)
    - [REFRESH](#refresh)

# How to use TwitchMakesATAS
TwitchMakesATAS works off a democratic system. Each request to change the TAS is a 'vote'. Whichever command gets the most votes, wins. If there is a tie, then the winner is chosen by random chance.

There are two types of voting in the bot.
* TAS votes - Votes to change the TAS. Includes writing, removal, reverting.
* Other votes - Votes for other elements of the stream. Includes going to a frame, playing from the start, or changing the piano roll.
## TAS Votes
TAS votes occur every 45 seconds. These votes are the ones displayed on the stream. They include
* Writing to the TAS. Example command: `WRITE 1,t,2`
* Removing from the TAS. Example command: `DELETE 50,20,ab`
* Reverting to an older version of the TAS. Example command: `REVERT "11-05 V30"`
  
After 45 seconds have passed, each TAS vote is counted and the command with the most votes is executed.
If there are 3 votes in which no votes have been cast, however, the 45 second timer freezes until the next vote is cast.
## Other Votes
These votes revolve around other elements of the TAS creation process. This includes
* Playing the TAS. Example command: `PLAY 161,803`
* Going to a frame in the TAS. Example command: `FRAME 455`
* Changing the starting frame of the piano roll. Example command: `PIANO 3141`
  
If an 'other' vote is cast, it will require a majority of viewers to agree to the command in order for it to be executed. This is because I believed these features would be better accessed whenever everyone agreed to do it, instead of having to wait for the vote timer to hit 0. This will happen exclusively in chat.

# Commands
Commands in the bot are signified by a capitalised starting word (except for general commands). Examples include `PLAY 31,41`, `WRITE 2718,abr`, `FRAME 250`, `REVERT "12-05 V10"`.
## Major Syntax Note
Each argument in a command is seperated by either a comma, or a comma with a space. The bot (most likely) wil

*How do you know that the command has failed?* The bot wouldn't have responded to your message, or it doesnt appear on the stream.

## General Commands
These commands are the only commands not to use the capitalised starting word format, instead starting with a backtick (\`). These commands take no arguments.
### `help
Links you [here.](about:blank)
### `repo
Links you to the [GitHub repo](about:blank)
### `timeleft
Makes the bot respond with how much time is left on the vote. Really only needed if you have extreme delay on your stream, though. The time left is on the stream itself.
### `uptime
Shows how long the bot has been online.

## TAS Commands
These commands are the ones that you've seen earlier in the document. These commands alter the TAS, or interact with other elements of the stream, such as FCEUX or the piano roll.

Arguments will be displayed like this: `COMMAND required-arg,[optional-arg=default]`
### WRITE frame,buttons,\[length=1\],\[pattern=1\]
Casts a vote to write to the TAS. 

`frame` states the starting frame.

`buttons` is which buttons are to be pressed, written as a string of the characters `abstudlr`. Order is not necessary for the buttons. To write B and R, use the string `br` or `rb`.

`length` states how many future frames will also have the buttons written too (This does **NOT** overwrite other frames.). Defaults to 1 frame.

`pattern` is a number that changes the firing pattern of the button. Example: `WRITE 1,t,32,2` writes T (start) to 32 frames (ending at frame 33), with the pattern On, Off, since 2 in binary is 10. 

To write the "One Quarter" pattern (as it's known in the TAS Editor), first write it out in binary, where 1 is pressed and 0 is not pressed. 1000 is equal to 8 in base 10, and that number is what you would use for the `pattern` argument. By default, `pattern` is set to 1, which means its active each frame.

### REMOVE frame,length,\[buttons="abstudlr"\]
Removes all instances of the buttons specified from the starting frame to the starting frame plus the length.

`frame` is the starting frame.

`length` is how many future frames are also affected.

`buttons` specifies which inputs to remove. Defaults to all buttons, clearing an entire frame.

### INSERT frame,\[buttons=""\]
**NOTE: This command is not present in the current version of the bot.**

Adds one new frame while pushing all future frames forward. Defaults to an empty frame.

### DELETE frame
**NOTE: This command is not present in the current version of the bot.**

Removes one remove while pushing all future frames back.

### IGNORE
Votes to do nothing. Could be useful if someone tries to vote for something malicious (e.g. `REMOVE 0,100000000`).

### REVERT tas-name
**NOTE: This command is not present in the current version of the bot.**

Reverts the TAS to a previous state, the name chosen from the TAS History section, when that gets implemented.

### RETRACT
Removes your vote from the pool. You do not need to call `RETRACT` if you are changing your vote. Changing your vote automatically retracts your previous one.

### FRAME frame
Goes to the frame specified. Requires a majority vote.

### PLAY \[start=0\] \[end=length of the movie\]
Plays the TAS from the specified starting frame to the end frame. If no arguments are specified, then it plays the whole movie.
Requires a majority vote.

### PIANO frame
Changes the piano roll to start from the frame specified. Requires a majority vote.
*Note: Updating the piano roll is a literal snail and will freeze other GUI elements. Use with care.*

### REFRESH
Refreshes the piano roll. Requires a majority vote. *Note: Updating the piano roll is a literal snail and will freeze other GUI elements. Use with care.*