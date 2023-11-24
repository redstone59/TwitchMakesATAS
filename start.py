from bot import *
from democracy import *
import threading

tmat = TwitchBot()
tmat.connect("oauth:eminempussysoundeffect","TwitchMakesATAS","#redstone59")
tmat.send_message("owo")

vote = Democracy()

try:
    bot_thread = threading.Thread(target=tmat.message_loop)
    democracy_thread = threading.Thread(target=vote.democracy_loop)
    
    bot_thread.run()
    #democracy_thread.run()
except KeyboardInterrupt:
    tmat.is_active = False
    tmat.send_message("nya~!")
    tmat.disconnect()