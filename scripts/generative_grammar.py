import pickle
import argparse
import os
import sys
from fst import fst, cmudict2fst



def convert(vector):
	ret_vector = []

	for item in vector:
		if item == '-':
			 ret_vector.append(-1)
		elif item == '+':
			ret_vector.append(1)
		elif item == '0':
			ret_vector.append(1000)
		elif item == u'±':
			ret_vector.append(0)
		else:
			raise NotImplementedError(f'Uknown token: {item}')

	return ret_vector

def cost_fn(vector_1, vector_2):

	dist = 0.0

	for a, b in zip(vector_1, vector_2):
		if a == 0 or b == 0:
			continue

		diff = a - b
		diff = diff ** 2
		dist += diff

	dist = dist ** (0.5)

	return dist


def swapping_fst():
	with open('../data/generative_lookup_dict.pkl','rb') as f:
		vectors = pickle.load(f)

	# b -> [1, 0, 1, 0 ]

	flower_fst = fst.FST()
	for symbol_1, vector_1 in vectors.items():
		for symbol_2, vector_2 in vectors.items():
			flower_fst.add_transition('w0','w0', symbol_1, symbol_2, cost_fn(vector_1, vector_2))

	flower_fst.set_initial('w0')
	flower_fst.set_final('w0')

	return flower_fst


def arpabet_2_word_fst():

	pkl_file = './fst/fst_cache/arpabet2word.fst'


	if os.path.isfile(pkl_file):
		return fst.load(pkl_file)
	else:
		print(f'Could not find .fst file {pkl_file!r}')
		print(f'generating \'arpabet2word.fst\' and \'word2arpabet.fst\' inside of \'./fst/fst_cache\'')
		cmudict2fst.generate_cmu_fst_pair(vocab='-',
										 word2arpabet='./fst/fst_cache/word2arpabet.fst',
										 arpabet2word='./fst/fst_cache/arpabet2word.fst',
										 cmu_dict='../cmudict/cmudict.dict')

		return fst.load(pkl_file)


def word_2_arpabet_fst():

	pkl_file = './fst/fst_cache/word2arpabet.fst'

	if os.path.isfile(pkl_file):
		return fst.load(pkl_file)
	else:
		print(f'Could not find .fst file {pkl_file!r}')
		print(f'generating \'arpabet2word.fst\' and \'word2arpabet.fst\' inside of \'./fst/fst_cache\'')
		cmudict2fst.generate_cmu_fst_pair(vocab='-',
										 word2arpabet='./fst/fst_cache/word2arpabet.fst',
										 arpabet2word='./fst/fst_cache/arpabet2word.fst',
										 cmu_dict='../cmudict/cmudict.dict')

		return fst.load(pkl_file)





def build_vectors(arpabet_features_file='../data/arpabet_features.csv', save_location='../data/generative_lookup_dict.pkl'):
	file_lines = []
	with open(arpabet_features_file,'r') as f:
		file_lines = f.readlines()

	header = file_lines[1].strip().replace('"','').split(',')

	vectors = {}
	for line in file_lines[2:]:

		# Get rid of new line and extraneous quotes, format into list
		v_list = line.strip().replace('"','').split(',')

		ipa_symbol = v_list[1]

		# lower-case the ARPABET symobl
		arpabet_symbol = v_list[2].lower()

		# Convert the features into some math vector
		vector = convert(v_list[3:])

		# Save vectors in a dictionary for lookup later

		# Ignoring ipa for now until we decide how to deal with stress
		#vectors[ipa_symbol] = vector

		vectors[arpabet_symbol] = vector

		# want to be compatible with lexical stress and assuming
		# stress doesn't effect feature representation
		low_stress = arpabet_symbol + '0'
		high_stress = arpabet_symbol + '1'

		vectors[low_stress] = vector
		vectors[high_stress] = vector

	# save off conversion as a pickle file


	with open(save_location,'wb') as f:
		pickle.dump(vectors,f,protocol=pickle.HIGHEST_PROTOCOL)

	return vectors


def main(args):


	if args.output != '':
		if os.path.isfile(args.output) and not args.overwrite:
			print(f'{args.output!r} already exists. Use --overwrite to ovewrite')
			sys.exit(1)

	save_loc = args.output if args.output != '' else '../data/generative_lookup_dict.pkl'
	features = args.features if args.features != '' else '../data/arpabet_features.csv'

	build_vectors(arpabet_features_file=features, save_location=save_loc)

	return 0
	 



if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Converts Generative Grammar file into vectors')
	parser.add_argument('--features',dest='features',help='arpabet feature value table', default='')
	parser.add_argument('--output',dest='output',default='../data/generative_lookup_dict.pkl',help='output for feature vectors')
	parser.add_argument('--overwrite',dest='overwrite',action='store_true',default=False,help='overwrite existing file')



	args = parser.parse_args()

	main(args)