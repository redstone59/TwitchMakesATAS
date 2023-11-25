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

TwitchMakesATAS(FM2_METADATA).start()


""" 8-4 pellson rom baloney
tas = ToolAssistedSpeedrun(FM2)

tas.write(10,'t')
tas.write(47,'r',14,2)
tas.write(61,'s')
tas.write(63,'r',6,2)
tas.write(69,'s',6,2)
tas.write(75,'d',20,1135658)
tas.write(77,'l')
tas.write(87,'l')
tas.write(99,'t')

tas.export("new_tas_test")
"""