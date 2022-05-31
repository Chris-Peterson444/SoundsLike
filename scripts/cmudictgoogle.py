# py
#
# Weighted Finite State Transducers, with composition and
# shortest paths.

import pickle
import heapq
from collections import defaultdict
import re

EPS='<eps>'

class FST(object):
    """
    A finite-state transducer, defined as an initial state,
    a set of final states, and a set of weighted transitions.
    Each transition from state1 to state2 with input symbol
    isym and output symbol osym is a tuple
    (state1, state2, isym, osym). Transitions are additionally
    indexed by state1, isym and osym.
    """

    def __init__(self):
        self.initial = None
        self.final = set()
        self.sigma = set()
        self.gamma = set()
        self.states = set()
        self.from_states = defaultdict(int)
        self.to_states = defaultdict(int)
        self.transitions = defaultdict(float)
        self.transitions_by_isym = defaultdict(set)
        self.transitions_by_osym = defaultdict(set)
        self.transitions_by_state = defaultdict(set)
        
    def add_transition(self, state1, state2, isym, osym, weight=0):
        """
        Add a transition to the FST. If the transition already
        exists, add weight to the existing weight.
        """
        self.states.add(state1)
        self.states.add(state2)
        if not (state1, state2, isym, osym) in self.transitions:
            self.from_states[state1] += 1
            self.to_states[state2] += 1
        self.transitions[(state1, state2, isym, osym)] += weight
        self.transitions_by_state[state1].add((state1, state2, isym, osym))
        self.transitions_by_isym[isym].add((state1, state2, isym, osym))
        self.transitions_by_osym[osym].add((state1, state2, isym, osym))

    def rm_transition(self, t):
        """
        Removes a transition from the FST.
        """
        if t in self.transitions:
            del self.transitions[t]
            self.transitions_by_isym[t[2]].remove(t)
            self.transitions_by_osym[t[3]].remove(t)
            self.transitions_by_state[t[0]].remove(t)
            self.from_states[t[0]] -= 1
            self.to_states[t[1]] -= 1

    def cleanup(self):
        """
        Remove unused states and transitions.
        """
        states_to_remove = []
        while True:
            transitions_to_remove = set()
            for t in self.transitions:
                if self.to_states[t[0]] == 0 and t[0] != self.initial:
                    transitions_to_remove.add(t)
                if self.from_states[t[1]] == 0 and t[1] not in self.final:
                    transitions_to_remove.add(t)
            for t in transitions_to_remove:
                self.rm_transition(t)
            if len(transitions_to_remove) == 0:
                break
        for s in self.states:
            if self.from_states[s] == 0 and self.to_states[s] == 0:
                states_to_remove.append(s)
        for s in states_to_remove:
            self.states.remove(s)
            del self.from_states[s]
            del self.to_states[s]
            
    def set_initial(self, s):
        """
        Set the initial state. There is only one initial state.
        """
        self.initial = s

    def set_final(self, s):
        """
        Set state s as a final state. There can be multiple final states.
        """
        self.final.add(s)

    def unset_final(self, s):
        if s in self.final:
            self.final.remove(s)

    def short_paths(self, n=1, dups=False):
        """
        Find n shortest paths. 
        Won't work with negative weights.
        """
        if self.initial == None:
            return None
        if len(self.final) == 0:
            return None

        # Best first search, from the initial state to any of
        # the final states. Won't work with negative weights.
        
        h = []
        itemcnt = 0
        heapq.heappush(h, (0, itemcnt, self.initial, []))
        paths = []
        chart = {}
        
        while len(paths) < n and len(h) > 0:
            accepted = False
            while len(h) > 0:
                curr1 = heapq.heappop(h)
                curr = (curr1[0], curr1[2], curr1[3])
                #print(curr)
                if curr[1] in self.final:
                    accepted = True
                    break
                if curr[1] not in self.transitions_by_state:
                    continue
                for transition in self.transitions_by_state[curr[1]]:
                    tost = transition[1]
                    score = curr[0]+self.transitions[transition]
                    if tost not in chart:
                        chart[tost] = []
                    item = (score, itemcnt, transition[1], curr[2]+[(transition[2], transition[3])])
                    itemcnt += 1
                    heapq.heappush(chart[tost], (item))
                    if item == chart[tost][0]:
                        heapq.heappush(h, item)

            if accepted:
                istr = [w[0] for w in curr[2]]
                ostr = [w[1] for w in curr[2]]
                while EPS in ostr:
                    ostr.remove(EPS)
                while EPS in istr:
                    istr.remove(EPS)
                if dups or len(paths) == 0 or not(istr == paths[-1][1] and ostr == paths[-1][2]):
                    paths.append((curr[0], istr, ostr))
                for tost in chart:
                    if len(chart[tost]) > 0:
                        heapq.heappop(chart[tost])
                        if len(chart[tost]) > 0:
                            heapq.heappush(h, chart[tost][0])

            if len(paths) > n:
                break
        
        return paths

    def print_transitions(self):
        print(self.initial)
        print(self.final)
        for t in self.transitions:
            print(t, self.transitions[t])

    def save(self, fname):
        pickle.dump(self, open(fname, 'wb'))

def load(fname):
    f = pickle.load(open(fname, 'rb'))
    return f

def inverted(origf):
    """
    Create an inverted FST from another FST.
    """
    newf = FST()
    newf.initial = origf.initial
    newf.final = origf.final.copy()
    for t in origf.transitions:
        newf.add_transition(t[0], t[1], t[3], t[2], origf.transitions[t])

    return newf

def compose(f, g,weight=-1):
    """
    Compose two FSTs, f and g.
    """
                    
    c = FST()
    c.states.add((f.initial, g.initial))
    c.initial = (f.initial, g.initial)
    a = [(f.initial, g.initial)]

    while len(a) > 0:
        (q1, q2) = a.pop(0)
        
        for t2 in g.transitions_by_state[q2]:
            if t2[2] == EPS and ((q1, t2[0]),
                                (q1, t2[1]),
                                EPS,
                                t2[3]) not in c.transitions:
                c.add_transition((q1, t2[0]),
                                (q1, t2[1]),
                                EPS,
                                t2[3],
                                g.transitions[t2])
                a.append((q1, t2[1]))

        for t1 in f.transitions_by_state[q1]:
            for t2 in g.transitions_by_state[q2]:
                if t2[2] == t1[3] and ((t1[0], t2[0]), 
                                    (t1[1], t2[1]), 
                                    t1[2], 
                                    t2[3]) not in c.transitions:
                    c.add_transition((t1[0], t2[0]), 
                                    (t1[1], t2[1]), 
                                    t1[2], 
                                    t2[3],
                                    f.transitions[t1] + g.transitions[t2])
                    a.append((t1[1], t2[1]))

    for ff in f.final:
        for gf in g.final:
            if (ff, gf) in c.states:
                c.set_final((ff, gf))

    c.cleanup()
    
    return c

def linear_chain(syms):
    """
    Create a linear chain FST, encoding a string.
    syms is a list containing the symbols of the string.
    """
    f = FST()
    curr_state = 0
    f.set_initial(curr_state)
    for s in syms:
        next_state = curr_state + 1
        f.add_transition(curr_state, next_state, s, s, 0)
        curr_state = next_state
    f.set_final(curr_state)
    return f

def linear_chain_from_string(mystr, sep=''):
    """
    Create a linear chain FST, encoding a string.
    mystr is a string, and sep is the separator. If no
    separator is provided, the string is split into
    characters.
    """
    if sep == '':
        toks = list(mystr)
    else:
        toks = mystr.split(sep=sep)

    return linear_chain(toks)

# def main():

#     # Encode a string as an FST, using white space as separator
#     myfst1 = linear_chain_from_string("This is a test", ' ')

#     # Create an FST transition by transition
#     myfst2 = FST()
#     myfst2.add_transition('w0', 'w0', 'This', 'this', 1)
#     myfst2.add_transition('w0', 'w0', 'This', 'This', 0)
#     myfst2.add_transition('w0', 'w0', 'is', 'is', 1)
#     myfst2.add_transition('w0', 'w0', 'a', 'one', 1)
#     myfst2.add_transition('w0', 'w0', 'a', 'a', 0)
#     myfst2.add_transition('w0', 'w0', 'test', 'test', 0)

#     myfst2.set_initial('w0')
#     myfst2.set_final('w0')

#     # Compose the two FSTs
#     c = compose(myfst1, myfst2)

#     # Find the shortest paths 
#     cpaths = c.short_paths(10)
#     print(cpaths)
    
# if __name__ == '__main__':
#     main()



def generate_cmu_fst_pair(vocab='-',
                        word2arpabet='word2arpabet.fst',
                        arpabet2word='arpabet2word.fst',
                        cmu_dict='../../cmudict/cmudict.dict',
                        ):


    # initialize the arpabet to word FST
    p2w = FST()
    p2w.set_initial(1)
    p2w.set_final(1)

    # initilize the word to arpabet FST
    w2p = FST()
    w2p.set_initial(1)
    w2p.set_final(1)

    p2w_state_id = 2
    w2p_state_id = 2

    # get the vocabulary
    fd = {}
    if vocab != '-':
        with open(vocab, 'r', encoding='utf-8') as fp:
            for line in fp:
                toks = line.split()
                if int(toks[0]) > 1:
                    fd[toks[1]] = int(toks[0])

    # go through each entry in the CMU Pronunciation Dictionary
    # with open('cmudict.0.7a_SPHINX_40', 'r', encoding='utf-8') as fp:
    # with open('../SoundsLike/cmudict/cmudict.dict', 'r', encoding='utf-8') as fp:
    with open(cmu_dict, 'r', encoding='utf-8') as fp:
        for line in fp:

            line = line.lower()
            if re.match('^[a-z]', line):
                toks = line.split()
                word = re.sub('\([0-9]+\)$', '', toks.pop(0))

                if len(fd) > 0 and word not in fd:
                    continue

                toks2 = toks.copy()

                # build the word to arpabet FST
                from_st = 1
                to_st = 1
                first_sym = toks.pop(0)
                last_sym = None
                if len(toks) > 0:
                    to_st = w2p_state_id
                    w2p_state_id += 1
                    last_sym = toks.pop(-1)
                w2p.add_transition(from_st, to_st, word, first_sym)
                from_st = to_st
                for sym in toks:
                    to_st = w2p_state_id
                    w2p_state_id += 1
                    w2p.add_transition(from_st, to_st, EPS, sym)
                    from_st = to_st
                if last_sym is not None:
                    w2p.add_transition(from_st, 1, EPS, last_sym)
        
                # build the arpabet to word FST
                last_sym = toks2.pop()
                from_st = 1
                to_st = 1
                
                for sym in toks2:
                    to_st = p2w_state_id
                    p2w.add_transition(from_st, to_st, sym, EPS)
                    from_st = to_st
                    p2w_state_id += 1

                p2w.add_transition(from_st, 1, last_sym, word)

    print('done. Saving...')
    w2p.save(word2arpabet)
    p2w.save(arpabet2word)
    print('done')


def main(args):

    generate_cmu_fst_pair(vocab=args.vocab,
                        word2arpabet=args.word2arpabet,
                        arpabet2word=args.arapbet2word,
                        cmu_dict=args.cmu_dict,
                        )

    return 0


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Converts cmudict into a FST')
    parser.add_argument('vocab',help='vocab file or \'-\' for all words in cmu_dict')
    parser.add_argument('word2arpabet',help='filename for word2arpabet fst')
    parser.add_argument('arapbet2word',help='filename for arpabet2word fst')
    parser.add_argument('cmu_dict', help='location of cmu_dict')

    args = parser.parse_args()

    main(args)