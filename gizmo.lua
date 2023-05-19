if (emu.paused()) then emu.unpause() end
emu.poweron()
emu.speedmode("maximum")
movie.load("twitch.fm2",true)
frame_delay=1
normal_speed_frame=1
pause_frame=movie.length()
stop_movie=true

while (true) do
    f=emu.framecount()
    if (f == normal_speed_frame-frame_delay) then emu.speedmode("normal") end
    if (stop_movie and f == movie.length()-frame_delay or f == pause_frame-frame_delay) then emu.pause() end
    emu.frameadvance()
end