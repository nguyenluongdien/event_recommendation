import random
from dateutil.parser import parse
import time

import pandas as pd
import numpy as np

from model import Model
import formula

events = pd.read_csv('data/events.csv', dtype = {'event_id': object, 'owner': object, 'place_id': object})
events.fillna('', inplace = True)
places = pd.read_csv('data/places.csv', dtype = {'place_id': object})
places.fillna('', inplace = True)
event_tfidf = pd.read_csv('data/event_tfidf.csv', dtype = {'event_id': object})
user_event = pd.read_csv('tmp/user_event.csv', dtype = {'user_id': object})
user_event.fillna('', inplace = True)
    
# Compute similarity of current event and user's interested events (in user's history)
def get_interested_sim(uid, eid):
	u_his = user_event[user_event.user_id == uid]	
	interested = u_his.at[u_his.index[0], 'attend'].split() + u_his.at[u_his.index[0], 'maybe'].split()
	score = []
	
	feature = [0, 0, 0]
	if (len(interested) == 0):
		return feature

	# get tf-idf vector of eid
	e = event_tfidf[event_tfidf.event_id == eid]
	vec_e = list(e.ix[e.index[0], 1:])
	
	# get tf-idf vector of interested events
	i_e = event_tfidf[event_tfidf.event_id.isin(interested)]

	for i in range(len(i_e.index)):		
		vec_ie = list(i_e.ix[i_e.index[i], 1:])
		score.append(formula.cos_sim(vec_e[:50], vec_ie[:50]))

	feature[0] = min(score)
	feature[1] = max(score)
	feature[2] = sum(score) / len(interested)

	return feature

# Compute similarity of current event and user's declined events (in user's history)
def get_hated_sim(uid, eid):
	u_his = user_event[user_event.user_id == uid]
	hated = u_his.at[u_his.index[0], 'declined'].split()
	score = []

	feature = [0, 0, 0]
	if (len(hated) == 0):
		return feature
	
	# get tf-idf vector of eid
	e = event_tfidf[event_tfidf.event_id == eid]
	vec_e = list(e.ix[e.index[0], 1:])

	# get tf-idf vector of hated events
	h_e = event_tfidf[event_tfidf.event_id.isin(hated)]

	for i in range(len(h_e)):		
		vec_he = list(h_e.ix[h_e.index[i], 1:])
		score.append(formula.cos_sim(vec_e[:50], vec_he[:50]))

	feature[0] = min(score)
	feature[1] = max(score)
	feature[2] = sum(score) / len(hated)

	return feature

# Compute distance(miles) between current event and user's interested events (in user's history)
def get_distances(uid, eid):
	u_his = user_event[user_event.user_id == uid]
	interested = u_his.at[u_his.index[0], 'attend'].split() + u_his.at[u_his.index[0], 'maybe'].split()
	score = [0]
	
	feature = [0, 0, 0]
	if (len(interested) == 0):
		return feature

	# get tf-idf vector of eid
	e = events[events.event_id == eid]
	place_id = e.at[e.index[0], 'place_id']	
	if (place_id == ''):
		return feature
	place = places[places.place_id == place_id]
	if (len(place) == 0):
		return feature		

	coor = list(place.ix[place.index[0], 4:])
	if ('' in coor):
		return feature

	# get historic places
	e = events[events.event_id.isin(interested)]
	e_places = e[e.place_id != '']
	place_ids = set(list(e['place_id']))
	hist_places = places[places.place_id.isin(place_ids)]
	if (len(hist_places) == 0):
		return feature

	for idx, place in hist_places.iterrows():		
		coor1 = [place['lat'], place['long']]		
		#print(coor1)
		if ('' in coor1):
			continue
		score.append(formula.distance_on_unit_sphere(coor[0], coor[1], coor1[0], coor1[1]))

	#print([uid, eid, score])
	feature[0] = min(score)
	feature[1] = max(score)
	feature[2] = sum(score) / len(interested)

	return feature

# Generate feature
def process_event(uid, eid):			
	
	interested_feat = get_interested_sim(uid, eid)
	hated_feat = get_hated_sim(uid, eid)
	dist_feat = get_distances(uid, eid)
	features = interested_feat + hated_feat + dist_feat
	#print(features)
	
	return features
    
# Get data from file
def get_data(filename):	
	dataset = pd.read_csv(filename, dtype = {'user_id': object, 'event_id': object})

	data = {'X': [], 'Y': []}
	for idx, record in dataset.iterrows():
		uid = record['user_id']
		eid = record['event_id']
		feature = process_event(uid, eid)

		data['X'].append(feature)
		data['Y'].append(record[-1])        	
        	
	return data

def run_full():
	train = get_data('tmp/train.csv')
	test = get_data('tmp/test.csv')    	
    
	w = [True] * len(train['X'][0])
	C = 0.03
    #C = 0.3
	m1 = Model(has_none=w, C=C)
	m1.fit(train['X'], train['Y'])
	results = m1.test(test['X'])	
	
	error = 0
	tp = 0
	fp = 0
	tn = 0
	fn = 0

	for i in range(len(results)):
		if results[i] != test['Y'][i]:			
			error += 1
			if results[i] == 1:
				fp += 1
			else:
				fn += 1
		elif results[i] == 1:
			tp += 1
		else:
			tn += 1

	print('tp = {}, fp = {}, tn = {}, fn = {}'.format(tp, fp, tn, fn))
	print('error rate: {}'.format(float(error) / len(results)))
	print('precision: {}'.format(float(tp) / (tp + fp)))
	print('recall: {}'.format(float(tp) / (tp + fn)))
	print('specificity: {}'.format(float(fp) / (fp + tn)))


##################################
# test cases
#print(get_interested_sim('10153097450077085', '411662922360897'))
#print(get_hated_sim('10153097450077085', '411662922360897'))
#print(get_distances('10153097450077085', '411662922360897'))
#print(process_event('10153097450077085', '411662922360897'))

run_full()











    
