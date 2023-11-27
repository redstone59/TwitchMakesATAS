import os, psutil

file = "test"

def run():
    if "fceux64.exe" in (i.name() for i in psutil.process_iter()): os.system("taskkill /f /im fceux64.exe")
    os.system(r'"D:\! various files\python\twitch bot doodads\lua fceux.bat"')

def play(pause=-1, start=1, stop_movie=True):
    j = open(r"D:\! various files\python\twitch bot doodads\gizmo.lua").readlines()
    j[3] = f'movie.load("{file}.fm2",true)\n'
    j[5] = f"normal_speed_frame={start}\n"
    if pause > 0:
        j[6] = f"pause_frame={pause}\n"
    else:
        j[6] = "\n"
    j[7] = f"stop_movie={'true' if stop_movie else 'false'}\n"
    with open(r"D:\! various files\python\twitch bot doodads\gizmo.lua","w") as lua:
        lua.writelines(j)
    run()

def frame(frame: int):
    play(frame, frame - 1)