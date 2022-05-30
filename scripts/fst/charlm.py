import fst
import math
import sys
from collections import Counter, defaultdict
import random

# Get the command line parameters:
# the order, the training file, and the output language model file
if len(sys.argv) != 4:
    print("Usage:", sys.argv[0], "order input_file output_file")
    sys.exit(1)

# order is the size of the ngrams (e.g. 2 for bigrams, 3 for trigrams, and so on.)
order = int(sys.argv[1])

# the length of the history, or context
histlen = order - 1

# the number of times we have each context in the training set
histfreq = Counter()

# the number of times we have each ngram in the training set
ngramfreq = defaultdict(Counter)

# open the training file, and go through it line by line
print("Building character LM...")
with open(sys.argv[2], 'r', encoding='utf-8') as fp:
    # each line is a string
    for line in fp:
        # we will use the | character as a special character, so it appears in 
        # the string, just replace it with /
        line = line.strip().replace('|', '/')

        # add as many <s> padding symbols to the string as needed,
        # and add the </s> end of string symbol
        #
        # list(line) makes a list with the characters of line
        # ['<s>'] * histlen makes a list that contains <s> histlen times
        # adding two lists just puts them together into one list
        curr_string = (['<s>'] * histlen) + list(line) + ['</s>']

        # now we go through each ngram in the current string
        for i in range((histlen), len(curr_string)):
            # the history, or the context, is the substring made of
            # the previous histlen characters
            hist = '|'.join(curr_string[i - histlen:i])

            # here's the count we are interested in:
            # after context hist, we see the current character and count it
            ngramfreq[hist][curr_string[i]] += 1

            # and we increase the count of how many times we saw this context,
            # since this will be the denominator when we compute P(curr_string[i]|hist)
            histfreq[hist] += 1

# now we have all the parameters of the character ngram model
print("Done")

print("Encoding LM as FST")

# create an FST
lm = fst.FST()

# the initial state is where we have only the <s> padding symbols,
# and we are ready for the first character in the string
lm.set_initial('|'.join(['<s>'] * histlen))

# the final state
lm.set_final('</s>')

# go through all the contexts in our count of contexts in the training set
for ctxt in histfreq:
    # go through all the symbols that have follow that context
    for sym in ngramfreq[ctxt]:
        # we need a transition from state ctxt to state newctxt,
        # which reflects that we just saw sym as input
        #
        # if a bigram model, newctxt is just the current input symbol,
        # but with larger ngrams, newctxt is the entire new context
        if order > 2:
            newctxt = ctxt[(ctxt.find('|') + 1):] + '|' + sym
        else:
            newctxt = sym
        if sym == '</s>':
            newctxt = sym

        # create the transition from ctxt to newctxt, with symbol sym
        # and set the weight according to the counts from the training set
        lm.add_transition(ctxt, newctxt, sym, sym, -math.log(ngramfreq[ctxt][sym]/histfreq[ctxt]))

print("Done")

# now we can save the FST
lm.save(sys.argv[3])
