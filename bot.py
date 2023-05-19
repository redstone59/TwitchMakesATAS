import socket, threading, time, math, random
import integration as nes
import tasmaker as tas
import gui

SERVER = 'irc.chat.twitch.tv'
PORT = 6667
NICKNAME = 'TwitchMakesATAS'
#region oauth token haha.
TOKEN = 'oauth:c0ck4ndb41lt0rtur30nw1kip3d143'
#endregion
CHANNEL = '#redstone59'
START_TIME = time.time()
GOOD_BOYS = ['redstone59','gaster319']
BOTS = ["twitchmakesatas","wizebot","nightbot","streamelements"]
MAJORITY = 0.5
FRAME_LIMIT=100

FM2_METADATA="""version 3
emuVersion 20605
rerecordCount 11
palFlag 0
romFilename NTSC_SMB1_Practice_ROM_v5.4 (1)
romChecksum base64:PA18Vzl461l4XHMdCj/fHw==
guid 968615CF-38AF-690F-162E-A453B00E80B7
fourscore 0
microphone 1
port0 1
port1 0
port2 0
FDS 0
NewPPU 0
RAMInitOption 0
RAMInitSeed 25271
"""

class BotVariable:
    vote_time = 45
    vote_start_time=time.time()
    voteList={}
    vote_count=0
    
    on=True
    nes_active=True
    has_alerted=False
    can_speak=True
    
    no_votes=0
    no_vote_limit=3

    yay_active=False
    yay_voters=[]
    yay_expiry=0x7fffffff
    yay_command=[]
    
    viewer_list={}
    viewer_expiry=120
    
    tk_queue=[]
    last_viewed_frame=0

sock = socket.socket()

sock.connect((SERVER, PORT))

sock.send(f"PASS {TOKEN}\n".encode('utf-8'))
sock.send(f"NICK {NICKNAME}\n".encode('utf-8'))
sock.send(f"JOIN {CHANNEL}\n".encode('utf-8'))

def gui_thread():
    gui.update_time()
    gui.master.update()
    gui.vote.update()
    gui.pr.update()
    
    if len(g.tk_queue)>0:
        for x in g.tk_queue:
            match x[0]:
                case "piano":
                    if len(x)==2 and x[1]!=-1:
                        gui.update_piano_roll(x[1])
                    else: gui.update_piano_roll()
                case "vote":
                    gui.update_votes(g.voteList)
                case "time":
                    gui.start_time=time.time()
        g.tk_queue=[]

def timed():
    while g.on:
        if time.time()-g.vote_start_time >= g.vote_time and g.no_votes<g.no_vote_limit:
            democracy()
            g.has_alerted=False
        if time.time()-g.vote_start_time >= g.vote_time-10 and g.no_votes<g.no_vote_limit:
            if not g.has_alerted and len(g.viewer_list) <= 3: send_msg("There is 10 seconds left on the vote!")
            g.has_alerted=True
        if time.time()>=g.yay_expiry and g.yay_active:
            yay_complete()

def parse():
    while g.on:
        resp = sock.recv(2048).decode('utf-8')

        if resp.startswith('PING'):
            sock.send("PONG\n".encode('utf-8'))

        msg=resp.split("#")
        
        if len(msg) > 1:
            sender=msg[0].split('!')[0][1:]
            message=msg[1].split(':')
            message.pop(0)
            message=':'.join(message)
            bot([sender,message])

def send_msg(msg: str):
    print("Sent message: '" +msg+"'")
    if g.can_speak: sock.send(f"PRIVMSG {CHANNEL} :{msg}\n".encode('utf-8'))

def update_viewer_list(sender=""):
    inactive_viewers=[]
    for x in g.viewer_list:
        if time.time()>g.viewer_list[x]:
            inactive_viewers+=[x]
    for x in inactive_viewers:
        del g.viewer_list[x]
    if sender != "":
        g.viewer_list[sender]=time.time()+g.viewer_expiry
    print("Current viewers:",len(g.viewer_list))

def start_yay(sender: str,command: str):
    g.yay_voters=[sender]
    if len(g.yay_voters)>=len(g.viewer_list)*MAJORITY:
                g.yay_command=command
                yay_complete()
                return
    if g.yay_active: send_msg("There is already a YAY vote on! Wait until that expires!");return
    g.yay_active=True
    g.yay_expiry=time.time()+30
    g.yay_command=command
    send_msg(f"{sender} has started a vote for {command}! Type 'YAY' to agree!")
    send_msg(f"There needs to be {math.floor(len(g.viewer_list)*MAJORITY)} YAY votes to pass! It expires in 30 seconds.")
    

def yay_complete():
    contents:str=g.yay_command
    g.yay_active=False
    g.yay_expiry=0x7fffffff
    
    user_args=contents.replace(', ',',').split()
    if len(user_args)>1: user_args="".join(user_args[1:]).lower().split(',')
    for x in user_args:
        x.strip()
        
    if contents.startswith("PIANO "):
        args=user_args
        #if len(args)>1 and args[1].isdigit():
        g.last_viewed_frame=int(args[1])
        g.tk_queue+=[["piano",int(args[1])]]
    
    elif contents.startswith("REFRESH"):
        g.tk_queue+=[["piano",g.last_viewed_frame]]
    
    elif g.nes_active:
        if contents.startswith("PLAY"):
            args=user_args
            if len(contents)==4:
                send_msg("Playing whole movie...")
                tas.export("d:/! various files/python/twitch bot doodads","twitch",FM2_METADATA)
                nes.play()
                return
            
            elif len(contents)>4 and contents[4]==" ":
                args=contents.split()
                if not args[1].isdigit(): 
                    send_msg("Invalid frame!")
                    return
                start=args[1]
                end=0x7fffffff
                
                if len(args) > 2 and args[2].isdigit():
                    end=args[2]
                send_msg("Playing from frame " + start + "...")
                tas.export("d:/! various files/python/twitch bot doodads","twitch",FM2_METADATA)
                nes.play(int(end),int(start))
        
        elif contents.startswith("FRAME "):
            frame=contents.split()[1]
            if frame.isdigit() and int(frame) >= 0:
                send_msg(f"Going to frame {contents.split()[1]}...")
                tas.export("d:/! various files/python/twitch bot doodads","twitch",FM2_METADATA)
                nes.frame(int(contents.split()[1]))


def vote(voter: str, vote: str):
    if g.no_votes >= g.no_vote_limit: 
        g.no_votes=0
        g.vote_start_time=time.time()
        gui.start_time=time.time()
        send_msg("Restarting timer...")
    for x in g.voteList:
        if voter in g.voteList[x]: g.voteList[x].remove(voter)
    if vote=="": send_msg(f"{voter} has retracted their vote!"); return
    if vote not in g.voteList.keys():
        g.voteList[vote]=[]
    g.voteList[vote].append(voter)
    g.tk_queue+=[["vote",-1]]
    send_msg(f"{voter} voted for {vote}! It currently has {len(g.voteList[vote])} vote{['s',''][len(g.voteList[vote]) < 2]}!")

def democracy():
    victor=[0,""]
    tie_list=[]
    for x in g.voteList:
        if len(g.voteList[x]) == victor[0] != 0: tie_list+=[[len(g.voteList[x]), x]]
        if len(g.voteList[x]) > victor[0]: 
            tie_list=[[len(g.voteList[x]), x]]
            victor=[len(g.voteList[x]), x]
    g.vote_start_time=time.time()
    gui.start_time=time.time()
    g.voteList={}
    send_msg("Vote over!")
    if victor==[0,""]: 
        send_msg("No vote has won! Starting new vote...")
        g.no_votes+=1
        if g.no_votes==g.no_vote_limit: 
            send_msg(f"{g.no_vote_limit} unsuccessful votes in a row! Stopping timer...")
            g.vote_start_time=0xFFFFFFFF
            gui.start_time="stopped"
        return
    g.no_votes=0
    if len(tie_list) > 1:
        send_msg(f"There is a tie between {len(tie_list)} entries! Choosing by random chance.")
        victor=random.choice(tie_list)
    send_msg(f"The winning vote is {victor[1]}! Starting new vote...")
    g.vote_count+=1
    g.tk_queue+=[["vote",-1]]
    tas.backup("d:/! various files/python/twitch bot doodads/backups",f"vote_{g.vote_count}")
    democracy_manifest(victor[1])

def democracy_manifest(command:str):
    
    #argument parsing
    user_args=command.replace(', ',',').split()
    if len(user_args)>1: user_args="".join(user_args[1:]).lower().split(',')
    for x in user_args:
        x.strip()

    frames=[-1,-1]
    if command.startswith("WRITE "):
        if len(user_args)<2: send_msg("Missing arguments!"); return
        args=["N/A","N/A","1","1"]
        for x in range (len(user_args)):
            args[x]=user_args[x]
        
        if not (args[0].isdigit() and args[2].isdigit() and args[3].isdigit()): return
        check_frame=int(args[0])
        check_buttons=[*args[1]]
        check_length=int(args[2])
        check_pattern=int(args[3])
        frames=[check_frame,check_frame+check_length]
        if tas.is_valid_command(frame=check_frame,buttons=check_buttons,length=check_length,pattern=check_pattern):
            tas.write(check_frame,check_buttons,check_length,check_pattern)
    
    elif command.startswith("REMOVE "):
        if len(user_args)<2: send_msg("Missing arguments!"); return
        args=["N/A","N/A",'abstudlr']
        for x in range (len(user_args)):
            args[x]=user_args[x]
        
        if not (args[0].isdigit() and args[1].isdigit()): return
        check_frame=int(args[0])
        check_length=int(args[1])
        check_buttons=[*args[2]]
        frames=[check_frame,check_frame+check_length]
        if tas.is_valid_command(frame=check_frame,length=check_length,buttons=check_buttons):
            tas.remove(check_frame,check_length,check_buttons)
    
    elif command.startswith("INSERT "):
        user_args=command.split()
        if len(user_args)>1: user_args[1].split(',')
        
        if len(user_args)<2: send_msg("Missing arguments!"); return
        args=["N/A",""]
        for x in range (len(user_args)):
            args[x]=user_args[x]
        
        if not (args[0].isdigit()): return
        check_frame=int(args[0])
        check_buttons=[*args[1]]
        if tas.is_valid_command(frame=check_frame,buttons=check_buttons):
            tas.insert(check_frame,check_buttons)
    
    elif command.startswith("DELETE "):
        user_args=command.split()
        if len(user_args)>1: user_args[1].split(',')

        if len(user_args)<2: send_msg("Missing arguments!"); return
        if not (user_args[0].isdigit()): return
        check_frame=int(args[0])
        if tas.is_valid_command(frame=check_frame):
            tas.delete(check_frame)
    
    elif command.startswith("REVERT "):
        pass
    
    elif command.startswith("IGNORE"):
        pass
    
    if g.last_viewed_frame<=frames[0]<=g.last_viewed_frame+gui.VOTE_RANGE or g.last_viewed_frame>=frames[1]>=g.last_viewed_frame+gui.VOTE_RANGE: g.tk_queue+=[["piano",g.last_viewed_frame]]

def bot(message: list):
    try:
        sender:str=message[0]
        contents:str=message[1].replace("\r\n","")
        if sender.lower() in BOTS: return
        print(sender,':',contents)
        update_viewer_list(sender)
        
        #argument parsing
        
        user_args=contents.replace(', ',',').split()
        if len(user_args)>1: user_args="".join(user_args[1:]).lower().split(',')
        for x in user_args:
            x.strip()
        
        #general commands
        #note to self: using elif statements for this is annoying as fuck,
        #rewrite later with match statements for the zeroth index of the user_args kthxbye :3

        if contents.startswith("`help"):
            send_msg("You can find out how to use the bot here: https://github.com/redstone59/TwitchMakesATAS/blob/main/README.md")
            
        elif contents.startswith("`repo"):
            send_msg("The GitHub repo can be found here: https://github.com/redstone59/TwitchMakesATAS")
        
        elif contents.startswith("`uptime"):
            uptime=math.floor(time.time()-START_TIME)
            send_msg(f"TwitchMakesATAS has been active for {uptime//3600} hours, {(uptime//60)%60} minutes, and {uptime%60} seconds.")
        
        #twitch makes a TAS stuff now
        
        elif contents.startswith("`timeleft"):
            if g.no_votes<g.no_vote_limit: send_msg(f"There is {g.vote_time-math.floor(time.time()-g.vote_start_time)} seconds left to vote!")
            else: send_msg("The timer is paused due to a lack of votes. Vote to start the timer again!")
        
        #yay votes/majority votes
        
        elif contents.startswith("YAY"):
            if not g.yay_active:
                send_msg("No yay vote is active!")
            elif time.time()>g.yay_expiry:
                send_msg("The vote has ended!")
                yay_complete()
            elif sender not in g.yay_voters:
                g.yay_voters+=[sender]
                send_msg(f"There are now {len(g.yay_voters)} yay votes!")
                if len(g.yay_voters)>=len(g.viewer_list)*MAJORITY:
                    yay_complete()
        
        elif contents.startswith("RETRACT"):
            vote(sender,"")
        
        #TAS votes
        
        elif contents.startswith("WRITE "):
            if len(user_args)<2: send_msg("Missing arguments!"); return
            args=["N/A","N/A","1","1"] #setting defaults
            for x in range (len(user_args)):
                args[x]=user_args[x]
            
            if not (args[0].isdigit() and args[2].isdigit() and args[3].isdigit()): return
            check_frame=int(args[0])
            if check_frame<=FRAME_LIMIT: send_msg(f"Invalid frame! Must be after frame {FRAME_LIMIT}!"); return
            check_buttons=[*args[1].lower()]
            check_length=int(args[2])
            check_pattern=int(args[3])
            if tas.is_valid_command(frame=check_frame,buttons=check_buttons,length=check_length,pattern=check_pattern):
                vote(sender,contents.split()[0]+" "+",".join(args))
        
        elif contents.startswith("REMOVE "):
            if len(user_args)<2: send_msg("Missing arguments!"); return
            args=["N/A","1",'abstudlr']
            for x in range (len(user_args)):
                args[x]=user_args[x]
            
            if not (args[0].isdigit() and args[1].isdigit()): return
            check_frame=int(args[0])
            if check_frame<=FRAME_LIMIT: send_msg(f"Invalid frame! Must be after frame {FRAME_LIMIT}!"); return
            check_length=int(args[1])
            check_buttons=[*args[2]]
            if tas.is_valid_command(frame=check_frame,length=check_length,buttons=check_buttons):
                vote(sender,contents.split()[0]+" "+",".join(args))
        
        elif contents.startswith("INSERT "):
            return #remove when implemented
            if len(user_args)<2: send_msg("Missing arguments!"); return
            args=["N/A",""]
            for x in range (len(user_args)):
                args[x]=user_args[x]
            
            if not (args[0].isdigit()): return
            check_frame=int(args[0])
            check_buttons=[*args[1]]
            if tas.is_valid_command(frame=check_frame,buttons=check_buttons):
                vote(sender,contents.split()[0]+" "+",".join(args))
        
        elif contents.startswith("DELETE "):
            return #remove when implemented
            if len(user_args)<2: send_msg("Missing arguments!"); return
            if not (user_args[0].isdigit()): return
            check_frame=int(args[0])
            if tas.is_valid_command(frame=check_frame):
                vote(sender,contents.split()[0]+" "+",".join(args))
        
        
        elif contents.startswith("REVERT "):
            print(1/0)
            pass
        
        elif contents.startswith("IGNORE"):
            vote(sender,contents)
        
        #other votes
        
        elif contents.startswith("PIANO "):
            args=contents.split()
            if len(args)>1 and args[1].isdigit():
                start_yay(sender,contents)
                
        elif contents.startswith("REFRESH"):
            start_yay(sender,contents)
        
        elif g.nes_active:
            if contents.startswith("PLAY"):
                if len(contents)==4 or len(contents)>4 and contents[4]==" ":
                    start_yay(sender,contents)
            
            elif contents.startswith("FRAME "):
                frame=contents.split()[1]
                if frame.isdigit() and int(frame) >= 0:
                    start_yay(sender,contents)
        
        #mod specific things (i will make it auto do a mod list sometime)
        
        elif sender in GOOD_BOYS:
            if contents.startswith("`endvote"):
                democracy()
            elif contents.startswith("`changevotetime"):
                g.vote_start_time=time.time()
                g.vote_time=int(contents.split()[1])
                send_msg(f"Changed vote time to {g.vote_time} seconds!")
            elif contents.startswith("`changenovotelimit"):
                g.no_vote_limit=int(contents.split()[1])
                send_msg(f"Changed no vote limit to {g.no_vote_limit} votes!")
            elif contents.startswith("`shutup"):
                send_msg("ok :(")
                g.can_speak=False
            elif contents.startswith("`talknow"):
                g.can_speak=True
                send_msg("yippee :D")
            elif contents.startswith("`execute"):
                try:
                    exec(contents)
                except Exception as e:
                    print(type(e).__name__, ":", e)
    except ConnectionAbortedError:
        raise KeyboardInterrupt
    except ConnectionResetError:
        raise KeyboardInterrupt
    except Exception as e:
        send_msg(f"Error! {type(e).__name__}: {e}")
        print(f"Error! {type(e).__name__}: {e}")

g=BotVariable
try:
    nes.file='twitch'
    a=threading.Thread(target=parse)
    a.start()
    b=threading.Thread(target=timed)
    b.start()
    send_msg('TwitchMakesATAS is now ONLINE!')
    while True:
        gui_thread()
        if not a.is_alive() or not b.is_alive():
            send_msg("Thread has stopped! Shutting down bot!")
            tas.backup("d:/! various files/python/twitch bot doodads/backups",f"error at vote_{g.vote_count}")
            g.on=False
            raise KeyboardInterrupt

except KeyboardInterrupt:
    g.on=False
    send_msg('nya~~!')
    sock.send("PART\n".encode('utf-8'))
    sock.close()