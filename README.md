# Rev-Debugging-in-Linux-Kernel

Compiling and Storing Perf Data
```
gcc race.c -lpthread -o race
perf record -e intel_pt/cyc,noretcomp/u ./race
perf script --insn-trace --xed -F+srcline,+srccode > race.dec
```



1) Race Condition Analysis

```
cd race
python3 ../objdump_parser.py
```

2)  Deadlock Analysis
```
cd deadlock
python3 ../objdump_deadlock.py

cd ..
cd deadunlock
python3 ../objdump_deadlock.py
```
