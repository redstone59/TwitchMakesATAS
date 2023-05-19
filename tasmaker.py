import os.path,math,json,datetime

tas={"a":[],"b":[],"s":[],"t":[],"u":[],"d":[],"l":[],"r":[]}

def bit(num, n):
    return (num >> n-1) & 1

def check(frame:int,button:str):
    if frame in tas[button]:
        return button.upper()
    return '.'

def export(dir:str,name:str,metadata:str):
    frames=0
    for x in tas:
        for y in tas[x]:
            if y>frames: frames=y
    file=os.path.join(dir,name+".fm2")
    tasf=open(file,"w")
    tasf.write(metadata)
    for x in range (frames+1):
        tasf.write(f"|0|{check(x,'r')}{check(x,'l')}{check(x,'d')}{check(x,'u')}{check(x,'t')}{check(x,'s')}{check(x,'b')}{check(x,'a')}|||\n")
    tasf.close()

#def tas_import(file_path:str):
#    frames=0
#    for x in tas:
#       for y in tas[x]:
#           if y>frames: frames=y
#    file=os.path.join(file_path)
#    tasf=open(file,"r")
#    g=tasf.readlines()[19:]
#    for x in range (len(g)):
#        for i in range (8):
#            print(x,g[x],g[x][i+3],[*"RDLUTSBA"][i],g[x][i+3]==[*"RDLUTSBA"][i])
#            if g[x][i+3]==[*"RDLUTSBA"][i]: tas[[*"rdlutsba"][i]]+=[x]
#    tasf.close()

def backup(dir:str,name:str):
    file_name=datetime.datetime.now().strftime("%Y-%m-%d %H-%M ")+name+".json"
    file=os.path.join(dir,file_name)
    backup_file=open(file,"w")
    backup_file.write(str(tas))
    backup_file.close()

def load_backup(dir:str,name:str):
    global tas
    file=os.path.join(dir,name+".json")
    backup_file=open(file,"r")
    tas=json.loads(backup_file.read().replace("'",'"'))
    backup_file.close()

def write(frame:int, buttons: list, length=1, pattern=0b1):
    if pattern <= 0 or frame <= 0 or not valid_buttons(buttons): return
    patternlen=math.floor(math.log(pattern,2)+1)
    for x in buttons:
        if x not in tas.keys(): continue
        for i in range (length):
            if bit(pattern, patternlen-(i%patternlen)): tas[x.lower()]+=[frame+i] if frame+i not in tas[x.lower()] else []

def remove(frame: int, length=1, buttons=[*"abstudlr"]):
    if frame <= 0 or not valid_buttons(buttons): return
    for x in buttons:
        if x not in tas.keys(): continue
        for i in range (length):
            if frame+i in tas[x.lower()]: tas[x.lower()].remove(frame+i)

def insert(frame:int,buttons=[]):
    if frame <= 0 or not valid_buttons(buttons): return
    for x in tas:
        for i in range (len(tas[x])):
            if tas[x][i]>=frame: tas[x][i]+=1
    for i in buttons:
            if i in tas.keys(): tas[i]+=[frame]
                
def delete(frame:int):
    if frame <= 0: return
    for i in tas.keys():
            if frame in tas[i]: tas[i].remove(frame)
    for x in tas:
        for i in range (len(tas[x])):
            if tas[x][i]>=frame: tas[x][i]-=1

def valid_buttons(buttons:list):
    valid=True
    for x in buttons:
        if x.lower() not in [*"abstudlr"]: return False
    return valid

def length():
    n=0
    for x in tas:
        for y in tas[x]:
            if y>n: n=y
    return n

def is_valid_command(frame=0, buttons=[*"abstudlr"], length=1, pattern=1):
    if length < 0: return False
    if pattern < 0: return False
    if frame < 0: return False
    if not valid_buttons(buttons): return False
    return True

write(10,['t'])
write(47,['r'],14,2)
write(61,['s'])
write(63,['r'],6,2)
write(69,['s'],6,2)
write(75,['d'],20,1135658)
write(77,['l'])
write(87,['l'])
write(99,['t'])

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

export("d:/! various files/python/twitch bot doodads","twitch",FM2_METADATA)