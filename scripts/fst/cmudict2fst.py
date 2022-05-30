#!/usr/bin/env python3

from fst import fst
# import fst
import re




def generate_cmu_fst_pair(vocab='-',
                        word2arpabet='word2arpabet.fst',
                        arpabet2word='arpabet2word.fst',
                        cmu_dict='../../cmudict/cmudict.dict',
                        ):


    # initialize the arpabet to word FST
    p2w = fst.FST()
    p2w.set_initial(1)
    p2w.set_final(1)

    # initilize the word to arpabet FST
    w2p = fst.FST()
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
                    w2p.add_transition(from_st, to_st, fst.EPS, sym)
                    from_st = to_st
                if last_sym is not None:
                    w2p.add_transition(from_st, 1, fst.EPS, last_sym)
        
                # build the arpabet to word FST
                last_sym = toks2.pop()
                from_st = 1
                to_st = 1
                
                for sym in toks2:
                    to_st = p2w_state_id
                    p2w.add_transition(from_st, to_st, sym, fst.EPS)
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