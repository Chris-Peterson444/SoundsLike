import fst
import math
import sys
import random

if len(sys.argv) != 2:
    print("Usage:", sys.argv[0], "lm")
    sys.exit(1)

lm = fst.load(sys.argv[1])

def randgen():
    currst = lm.initial
    while currst not in lm.final:
        transitions = []
        for t in lm.transitions_by_state[currst]:
            transitions.append((math.exp(-lm.transitions[t]), t))
        r = random.random()
        i = 0
        totalp = transitions[i][0]
        while r > totalp:
            i += 1
            totalp += transitions[i][0]
        currst = transitions[i][1][1]
        sym = transitions[i][1][2]
        if sym == '</s>':
            sym = '\n'
        print(sym, end='')


for i in range(10):
    randgen()
    print()



