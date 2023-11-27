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

# Pellson ROM 4-2 with framerule 289. Thanks Lain!
tmat.tas.write(10, 't')
tmat.tas.write(47, 'r', 9, 0b101010001)
tmat.tas.write(53, 's', 9, 0b100010101)
tmat.tas.write(63, 'd', 7, 0b1010001)
tmat.tas.write(67, 'l', 5, 0b10001)
tmat.tas.write(73, 'u', 3, 0b101)
tmat.tas.write(78, 't')

tmat.tas.frame_limit = 100

tmat.start("oauth:eminempussysoundeffect")