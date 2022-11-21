



import pprint

def is_hex(s):
    try:
        int(s, 16)
        return True
    except ValueError:
        return False

def getSectionName(inputLine):

    sectionlen = 9
    sectionIndex = inputLine.find("section .")
    
    return inputLine[sectionIndex + sectionlen: len(inputLine)-2]

def globalAbsAddress(line):

    RIP_OFFSET_INDEX_READ = 8
    RIP_OFFSET_INDEX_WRITE = 9
    ACCESS_READ = 0
    ACCESS_WRITE = 1
    words = line.split()
    instr_addr = words[4]

    rip_str =  words[RIP_OFFSET_INDEX_READ]
    access_type = ACCESS_READ
    if("%rip" not in rip_str):
        rip_str =  words[RIP_OFFSET_INDEX_WRITE]
        access_type = ACCESS_WRITE
    open_brac_index = rip_str.find("(")
    offset_addr = rip_str[0:open_brac_index]

    instr_addr_int = int(instr_addr,16)
    offset_addr_int = int(offset_addr,16)

    return (instr_addr_int + offset_addr_int + 7), access_type


def hasNoBlackListGlobalVar(varName):

    globalVarBlackList = [ "__dso_handle", "completed.", "_end", "__bss_start", "data_start", "_edata", "__data_start" ,  "__TMC_END__", ".data" , ".bss" ]
    if varName in globalVarBlackList:
            return False
    if "completed." in varName:
            return False
    return True; 


def getGlobalVarDir():

    objDumpFile = open('objdump_t.txt', 'r')
    objDumpLines = objDumpFile.readlines()

    l_globalVarDir = {}
    for line in objDumpLines:
    # 0000000000404068 g     O .bss	0000000000000008              ptr
        if (".bss" in line or ".data" in line) :
            words  = line.split(' ')
            globalVarName = words[len(words)-1]
            globalVarName = globalVarName[:len(globalVarName)-1] # remove trailing /n
            if not hasNoBlackListGlobalVar(globalVarName):
                continue
            l_globalVarDir[globalVarName] = int(words[0],16) # Address

    objDumpFile.close()
    return l_globalVarDir


'''
def getPthreadAddr():
    l_pthread_lock_addr = 0;
    l_pthread_unlock_addr = 0;

    objDumpFile = open('decode.txt', 'r')
    objDumpLines = objDumpFile.readlines()

    
    for line in objDumpLines:
        if "pthread_mutex_lock@plt+0x0" in line:
            words = line.split(" ")
            print(words)
            l_pthread_lock_addr=int(words[23],16)
        if "pthread_mutex_unlock@plt+0x0" in line:
            words = line.split(" ")
            l_pthread_unlock_addr = int(words[23],16)
    objDumpFile.close()
    return l_pthread_lock_addr, l_pthread_unlock_addr
'''

def getPthreadAddr():
    l_pthread_lock_addr = 0;
    l_pthread_unlock_addr = 0;

    objDumpFile = open('objdump_D.txt', 'r')
    objDumpLines = objDumpFile.readlines()

    
    for line in objDumpLines:
        if " <pthread_mutex_lock@plt>:" in line:
            words = line.split(" ")
            l_pthread_lock_addr=int(words[0],16)
        if " <pthread_mutex_unlock@plt>:" in line:
            words = line.split(" ")
            l_pthread_unlock_addr = int(words[0],16)
    objDumpFile.close()
    return l_pthread_lock_addr, l_pthread_unlock_addr


def getFuncList():
    objDumpFile = open('objdump_t.txt', 'r')
    objDumpLines = objDumpFile.readlines()

    globalThreadBlackList = ["__libc_csu_fini","__libc_csu_init", "_dl_relocate_static_pie", "_start"]

    l_threadList = []
    for line in objDumpLines:

        if ".text" in line:
            words = line.split(' ')
            type = words[1];
            if(type != 'g'):
                continue
            threadName = words[len(words)-1]
            threadName = threadName[:len(threadName)-1] # remove trailing /n
            if threadName in globalThreadBlackList:
                continue
           # print(threadName)
            l_threadList.append(threadName)

    return l_threadList


def callqTargetAddr(line):
    words = line.split(" ")  
    return int(words[len(words)-1],16)


def getThreadAndLockVariable(line):
    words = line.split()
    
    NEXT_INSTR_OFFSET = 10
    instr_addr  =  int(words[4],16) + NEXT_INSTR_OFFSET 

    threadName = words[5]
    threadName = threadName[ :threadName.find('+')]
  #  print(threadName)

    lockVarAddr = words[8]
    lockVarAddr = lockVarAddr[1:-1]
 #  print(lockVarName)
    return threadName,lockVarAddr,instr_addr

def getGlobalVarNameFromAddr(addr,globalVarDir):

    for var in globalVarDir.keys():
        if addr == globalVarDir[var]:
            return var
    print("WARNING NO MATCH")
    return ""


def getInstrAddrFromLine(line):
    words = line.split()
    if len(words) >= 5:
        return "0x" + words[4]
    return "NULL"



################### Main ###################
globalVarDir = getGlobalVarDir()

g_pthread_lock_addr ,g_pthread_unlock_addr = getPthreadAddr()

threadList = getFuncList()


'''
Parse the perf data

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
                print(var + " "+ str(abs_addr) + " " + str(int(globalVarDir[var],16))) 
                # Found the line that uses the globale variable 'var' with relative addressing
                if abs_addr == int(globalVarDir[var],16):
                    print("Address Match : " + str(access_type))
                    if access_type == ACCESS_READ:
                        gVarAccessTracking[var]["last_read_func"] = thread
                    else:
                        gVarAccessTracking[var]["last_write_func"] = thread
            

print("============")
pprint.pprint(gVarAccessTracking)
'''


'''
Initialize the thread tracking D.S
'''
threadTracking  = {}
for thread in threadList:
    threadTracking[thread] = [] 

'''
To track lock success
'''
openLocks = {}


perfDecFile = open('decode.txt', 'r')
perfDecLines = perfDecFile.readlines()

prev_line = ""
line_index = 0
for line in perfDecLines:


    # 1) Lock Waiting
    pthreadSearchString  = hex(g_pthread_lock_addr)[2:]+ " "+ "pthread_mutex_lock@plt"
    if pthreadSearchString in line:
        line_loadLockVar =  perfDecLines[line_index - 2]
        threadName,lockVarAddr,lockACQinstrAddr = getThreadAndLockVariable(line_loadLockVar)        
        lockVarName = getGlobalVarNameFromAddr(int(lockVarAddr,16),globalVarDir)
        threadTracking[threadName].append(lockVarName +"_wait")  
        openLocks[hex(lockACQinstrAddr)] = [ threadName, lockVarName]
    else:
    # 2) Lock Acquire
        instrAddr = getInstrAddrFromLine(line)
            
        if openLocks.get(instrAddr) != None:
            threadName = openLocks[instrAddr][0]
            lockName = openLocks[instrAddr][1]
            threadTracking[threadName].append(lockName+"_acquire")
        elif  is_hex(instrAddr) and int(instrAddr,16) == g_pthread_unlock_addr:
            line_loadLockVar =  perfDecLines[line_index - 2]
            threadName,lockVarAddr,lockACQinstrAddr = getThreadAndLockVariable(line_loadLockVar)        
            lockVarName = getGlobalVarNameFromAddr(int(lockVarAddr,16),globalVarDir)
            threadTracking[threadName].append(lockVarName +"_release")  


    # 3) Lock Acquire

    line_index +=1
    # End For

print("")
print("=========RESULTS===============")
pprint.pprint(threadTracking)
pprint.pprint(openLocks)
