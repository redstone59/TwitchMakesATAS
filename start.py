from tmat import *

FM2_METADATA = """version 3
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

tmat = TwitchMakesATAS(FM2_METADATA)

# Pellson ROM 8-2 with framerule 526. Thanks Lain!
tmat.tas.write(10, 't')
tmat.tas.write(47, 'r', 17, 0b10101010101010001)
tmat.tas.write(61, 's', 9, 0b100010101)
tmat.tas.write(71, 'd', 7, 0b1010101)
tmat.tas.write(79, 'l', 7, 0b1000001)
tmat.tas.write(81, 'u', 15, 0b101000101010101)
tmat.tas.write(100, 't')

tmat.tas.frame_limit = 101

tmat.start("oauth:eminempussysoundeffect")