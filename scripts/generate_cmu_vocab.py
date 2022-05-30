import re

vocab = {}

with open('../cmudict/cmudict.dict','r') as cmudict:
	for line in cmudict:
		toks = line.split()
		word = re.sub('\([0-9]+\)$', '', toks.pop(0))
		vocab[word] = list(word)

with open('../data/cmuvocab.ssv','w') as vocab_file:
	for word, spelling in vocab.items():
		vocab_file.write(f'{word} {" ".join(spelling)}\n')
