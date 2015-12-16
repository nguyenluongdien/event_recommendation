#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import math
import os
import numpy as np
import re

top_n = 100

# Create collection of documents
# input: path (string), filenames (list)
# output: documents (dict)
def collectData(path, filenames):
	documents = {}
	#prog = re.compile('[~!@#$%^&*()_+`1234567890\-=\[\]\\{}|;\':\",./<>?–]') # regular expression of special characters
	prog = re.compile('[!@#$%^&*()+=_,./;\'<>?:\"{}\[\]1234567890]') # regular expression of special characters
	for name in filenames:
		f = open(path + name)
		documents[name] = f.read()
		documents[name] = prog.sub('', documents[name].lower())
		f.close()

	return documents

# Create vocabulary from collection
# input: documents (dict)
# output: vocabulary (list)
def createVocabulary(documents):
	vocabulary = []

	for doc_id, doc in documents.iteritems():	
		words = doc.split()
		vocabulary = vocabulary + words
	
	# remove stopwords, special characters, number
	f = open('tmp/stopwords.txt')
	stopwords = f.read().splitlines()
	f.close()	
	
	vocabulary = list(set(vocabulary) - set(stopwords))
	
	return vocabulary

# Calculate IDF
# input: documents (dict), vocabulary (list)
# output: IDF (list)
# len(vocabulary) >> len(doc.split())!!!
def IDF(documents, vocabulary):
	IDF_vect = [0] * len(vocabulary)
	N = len(documents)

	for i in range(len(vocabulary)):        
		df = 0
		for doc_id, doc in documents.iteritems():
			words = doc.split()
			if (vocabulary[i] in words):
				df = df + 1
        
		IDF_value = math.log(N / df)       
		IDF_vect[i] = IDF_value		

	return IDF_vect

# Calculate TF for document
# input: document (string), vocabulary (list)
def TF(document, vocabulary):	
	"""
	TF_vector = [0] * len(vocabulary)
    
	words = document.split()    
	words_unique = list(set(words))

	for i in range(len(words_unique)):        
		if (words_unique[i] not in vocabulary):
			continue
	
		index = vocabulary.index(words_unique[i])       
		num_word = words.count(words_unique[i])       
		TF_vector[index] = float(num_word) / len(words)

	return TF_vector
	"""
	result = {}
	result['TF'] = [0] * len(vocabulary)
	idx = []
	
	words = document.split()    
	words_unique = list(set(words))

	for i in range(len(words_unique)):        
		if (words_unique[i] not in vocabulary):
			continue
	
		index = vocabulary.index(words_unique[i])       
		num_word = words.count(words_unique[i])       
		result['TF'][index] = float(num_word) / len(words)
		idx.append(words.index(words_unique[i]))

	idx.sort()
	result['terms'] = [words[i] for i in idx]

	return result


# Convert collection of documents in path to tfidf
# input: path (string)
# output: TFIDFs (dict)
def convert2TFIDF(path):
	filenames = []
	for f in os.listdir(path):
		filenames.append(f)		

	documents = collectData(path, filenames)
	vocabulary = createVocabulary(documents)
	IDF_vect = IDF(documents, vocabulary)

	# Select top terms
	indices = np.argsort(IDF_vect)[:top_n]
	top_IDF_vect = [IDF_vect[i] for i in indices]
	top_vocabulary = [vocabulary[i] for i in indices]
	out = open('data/vocabulary.txt', 'w')
	out.write(', '.join(top_vocabulary))
	out.close()
	print('preparing complete')

	####### Write key terms of documents
	out_tmp = open('data/event_desc.csv', 'w')
	out_tmp.write('event_id,terms\n')
	
	TFIDFs = {}
	for doc_id, doc in documents.iteritems():
		TFIDF_vect = [0] * len(top_vocabulary)
		calc_result = TF(doc, top_vocabulary)
		TF_vect = calc_result['TF']
		terms = calc_result['terms']
		out_tmp.write(doc_id)
		out_tmp.write(',')
		out_tmp.write('\"' + ' '.join(terms) + '\"')
		out_tmp.write('\n')
		#TF_vect = TF(doc, top_vocabulary)
		for i in range(len(TF_vect)):
			TFIDF_vect[i] = TF_vect[i] * top_IDF_vect[i]
		
		TFIDFs[doc_id] = TFIDF_vect
	print('calculating complete')
	out_tmp.close()

	return TFIDFs

#####################################
#####################################
TF_IDFs = convert2TFIDF('descriptions/')
out = open('data/event_tfidf.csv', 'w')
out.write('event_id')
for i in range(top_n):
	out.write(',f_' + str(i))

out.write('\n')

# Write feature
for eid, record in TF_IDFs.iteritems():
	out.write(eid)
	out.write(',')
	out.write(','.join(map(str, record)))
	out.write('\n')

out.close()





































