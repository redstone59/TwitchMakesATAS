from bot import *

tmat = TwitchBot()
tmat.connect("oauth:veryrealtwitchapitoken","TwitchMakesATAS","#redstone59")
tmat.send_message("owo")

try:
    tmat.message_loop()
except KeyboardInterrupt:
    tmat.send_message("nya~!")
    tmat.disconnect()