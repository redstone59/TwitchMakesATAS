import tkinter as tk
from tkinter import ttk
import tasmaker as tas
import json,time

FONT_NAME="Courier New"
BUTTONS=[*"ABSTUDLR"]
SCALE=0.75
DISPLAYED_FRAMES=30
VOTE_RANGE=17
DEBUG=False
VOTE_LENGTH=45
current_frame=0
closed=False
#master window setup
master=tk.Tk()
master.title("Twitch Makes A TAS")
start_time=time.time()

#vote window setup
vote=tk.Toplevel(master)
vote.title("TAS Votes")
vote.geometry("480x720+0+0")
vote.columnconfigure(1,weight=3)

#piano roll window setup
pr=tk.Toplevel(master)
pr.geometry(f"300x1280+328+0")
pr.title("TAS Piano Roll")

def update_time():
    if type(start_time)==str: time_left['text']="Voting paused!"
    time_left['text']=str(VOTE_LENGTH-int(time.time()-start_time))+" seconds"

def update_piano_roll(start_frame=current_frame):
    if start_frame<0: return
    global current_frame
    current_frame=start_frame
    n=0
    for label in pr.grid_slaves():
        if int(label.grid_info()["row"]) > 1: label.destroy()
        vote.update()
        n+=1
        if n%18==0: pr.update()
        update_time()
    for x in range(DISPLAYED_FRAMES):
        tk.Label(pr,text=f"{start_frame+x}".zfill(8),font=(FONT_NAME,int(20*SCALE)),bg=["white","grey90"][x%2],highlightthickness=1,highlightbackground="grey50",highlightcolor="grey50").grid(column=0,row=2+x)
        for i in BUTTONS:
            if start_frame+x in tas.tas[i.lower()]: input=i
            else: input=" "
            tk.Label(pr,text=input,font=(FONT_NAME+" Bold",int(20*SCALE)),bg=["white","grey90"][x%2],highlightthickness=1,highlightbackground="grey50",highlightcolor="grey50").grid(column=1+BUTTONS.index(i),row=x+2)
        vote.update()
        pr.update()
        update_time()

def update_votes(vote_list:dict):
    votes=[]
    for x in vote_list:
        votes+=[[len(vote_list[x]),x]]
    votes.sort(reverse=True)
    for label in vote.grid_slaves():
        update_time()
        if 1 < int(label.grid_info()["row"]) <= VOTE_RANGE: label.destroy()
    for x in range (VOTE_RANGE):
        update_time()
        if x>30: break
        if x<len(votes):
            command=votes[x][1]
            count=str(votes[x][0])
        else:
            command,count=" "," "
        tk.Label(vote,text=(" "*100+command)[-26:],font=(FONT_NAME,int(20*SCALE)),bg=["white","grey90"][x%2],highlightthickness=1,highlightbackground="grey50",highlightcolor="grey50").grid(column=1,row=2+x,sticky="E")
        tk.Label(vote,text=(count+" "*20)[:10],font=(FONT_NAME,int(20*SCALE)),bg=["white","grey90"][x%2],highlightthickness=1,highlightbackground="grey50",highlightcolor="grey50").grid(column=2,row=2+x,sticky="W")

#PIANO ROLL SETUP

tk.Label(pr,text="Piano Roll",font=(FONT_NAME+" Bold",int(28*SCALE))).grid(column=0,row=0,columnspan=9)
tk.Label(pr,text="Frame #",font=(FONT_NAME,int(20*SCALE))).grid(column=0,row=1)
for x in range (8):
    tk.Label(pr,text=BUTTONS[x],font=(FONT_NAME,int(20*SCALE))).grid(column=x+1,row=1)
for x in range (50):
    for i in range (9):
        tk.Frame(pr,borderwidth=5,relief="ridge").grid(column=1+i,row=x+2)

#VOTE WINDOW SETUP

tk.Label(vote,text="Votes",font=(FONT_NAME+" Bold",int(28*SCALE))).grid(column=1,row=0,columnspan=2)
tk.Label(vote,text="Vote",font=(FONT_NAME,int(20*SCALE))).grid(column=1,row=1)
tk.Label(vote,text="# of votes",font=(FONT_NAME,int(20*SCALE))).grid(column=2,row=1)
tk.Label(vote,text=" ",font=(FONT_NAME,int(20*SCALE))).grid(column=0,row=1)
tk.Label(vote,text=" ",font=(FONT_NAME,int(20*SCALE))).grid(column=3,row=1)
tk.Label(vote,text="Time Left",font=(FONT_NAME+" Bold",int(32*SCALE))).grid(column=1,row=3+VOTE_RANGE,columnspan=2)
tk.Label(vote,text=" ",font=(FONT_NAME,int(20*SCALE))).grid(column=1,row=2+VOTE_RANGE,columnspan=2)

time_left=ttk.Label(vote,text="45 seconds",font=(FONT_NAME,int(28*SCALE)))
time_left.grid(column=1,row=4+VOTE_RANGE,columnspan=2)

if DEBUG:
    gameing=tk.StringVar()
    votelist=tk.StringVar()
    timeleft=tk.StringVar()

    tk.Entry(master,textvariable=gameing).grid(column=0,row=0)
    tk.Button(master,text="update paino rol",command=lambda: update_piano_roll(int(gameing.get()))).grid(column=0,row=1)
    tk.Entry(master,textvariable=votelist).grid(column=1,row=0)
    tk.Button(master,text="update votelist",command=lambda: update_votes(json.loads(votelist.get()))).grid(column=1,row=1)
else: master.withdraw()

update_piano_roll()
update_votes({})

#while True:
#   master.update()
#   vote.update()
#   pr.update()