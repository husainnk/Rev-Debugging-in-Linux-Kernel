import json

import pprint

def getSectionName(inputLine):

    sectionlen = 9
    sectionIndex = inputLine.find("section .")
    
    return inputLine[sectionIndex + sectionlen: len(inputLine)-2]

def globalAbsAddress(line):

    RIP_OFFSET_INDEX_READ = 8
    RIP_OFFSET_INDEX_WRITE = 9
    ACCESS_READ = 0
    ACCESS_WRITE = 1
    INSTRUCTION_WIDTH_MOV_REG = 7

    words = line.split()
    instr_addr = words[4]

    rip_str =  words[RIP_OFFSET_INDEX_READ]
    access_type = ACCESS_READ
    inst_width = 7
    if("%rip" not in rip_str):
        rip_str =  words[RIP_OFFSET_INDEX_WRITE]
        access_type = ACCESS_WRITE
        if "$0x" in words[RIP_OFFSET_INDEX_READ]:  # in the SRC Register
            inst_width = 11
    open_brac_index = rip_str.find("(")
    offset_addr = rip_str[0:open_brac_index]

    instr_addr_int = int(instr_addr,16)
    offset_addr_int = int(offset_addr,16)
    return (instr_addr_int + offset_addr_int +inst_width ), access_type

'''
objDumpFile = open('assem.txt', 'r')
objDumpLines = objDumpFile.readlines()

parsedSections = {}
currentSection = ""
for line in objDumpLines:

    if "Disassembly" in line:
        currentSection =  getSectionName(line)
        parsedSections[currentSection] = []
        continue
    if currentSection is not "":
        if line is "\n":
            continue
        if line is "\t...\n":
            continue
        parsedSections[currentSection].append(line)

pprint.pprint(parsedSections)
'''

def hasNoBlackListGlobalVar(line):

    globalVarBlackList = ["completed.0", "_end", "__bss_start", "data_start", "_edata", "__data_start" ,  ".hidden __TMC_END__" ]
    for var in globalVarBlackList:
        if var in line:
            return False
    return True; 



## Main ##
objDumpFile = open('objdump_t.txt', 'r')
objDumpLines = objDumpFile.readlines()

globalVarDir = {}
for line in objDumpLines:
    # 0000000000404068 g     O .bss	0000000000000008              ptr
    if (".bss" in line or ".data" in line) and hasNoBlackListGlobalVar(line) :
        words  = line.split(' ')
        globalVarName = words[len(words)-1]
        globalVarName = globalVarName[:len(globalVarName)-1] # remove trailing /n
#        print(globalVarName)
#        print(words[0])
        globalVarDir[globalVarName] = words[0] # Address

print(globalVarDir)

globalThreadBlackList = ["_dl_relocate_static_pie", "_start"]
threadList = []
for line in objDumpLines:

    if ".text" in line:
        words = line.split(' ')
        type = words[1];
        if(type != 'g'):
            continue
       # print(line)
        threadName = words[len(words)-1]
        threadName = threadName[:len(threadName)-1] # remove trailing /n
        if threadName in globalThreadBlackList:
            continue
       # print(threadName)
        threadList.append(threadName)
print(threadList)
print("")

'''
Parse the perf data
'''

gVarAccessTracking  = {}

for gvar in globalVarDir:
    gVarAccessTracking[gvar] = { "last_read_func" : "NULL", "last_write_func" : "NULL"} 

pprint.pprint(gVarAccessTracking)

perDecFile = open('decode.txt', 'r')
perDecLines = perDecFile.readlines()

ACCESS_READ = 0
ACCESS_WRITE = 1
for line in perDecLines:
    if "%rip" not in line:
        continue;

    for thread in threadList:
        threadname = " "+thread + "+";
        #  race_new_workin 57228 [006] 28247.676638077:            4011d3 PrintHello1+0x1b (/home/sandeep/coursework/Fall22/OS/project/temp/test/race_new_working) 		movq  0x2e8e(%rip), %rax
        if threadname in line:
            print(line)
            abs_addr, access_type  = globalAbsAddress(line)
            for var in globalVarDir.keys():
                print( "relative_addr :" +  var + " "+ str(abs_addr) + " " + str(int(globalVarDir[var],16))) 
                # Found the line that uses the globale variable 'var' with relative addressing
                print(hex(abs_addr) + " == " + globalVarDir[var])
                if abs_addr == int(globalVarDir[var],16):
                    print("Address Match : " + str(access_type))
                    if access_type == ACCESS_READ:
                        gVarAccessTracking[var]["last_read_func"] = (thread, perDecLines.index(line)+1)
                    else:
                        gVarAccessTracking[var]["last_write_func"] = (thread, perDecLines.index(line)+1)
            

print("============")
pprint.pprint(gVarAccessTracking)
with open("race_tracking.json", "w") as outfile:
    json.dump(gVarAccessTracking, outfile)

with open("race_function.json", "w") as outfile:
    json.dump({"functions": threadList}, outfile)                                                                                                  

with open("race_variable.json", "w") as outfile:
    json.dump(globalVarDir, outfile) 


