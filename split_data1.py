#!/usr/bin/env python2

import pandas as pd
import random
import math

'''
# Select data to make data set
data = pd.read_csv('tmp/user_event_full.csv', dtype = {'user_id': object})
data.fillna('', inplace = True)
#used_data = data[(data.attend != '') & (data.declined != '')]
used_data = data[(data.declined != '')]  
used_data.to_csv('tmp/user_event.csv', index = False)
'''

num_neg = 0
num_pos = 0

#########
# This function is implemented for balancing data, between interested and uninterested events
# input: dictionary of data with key is uid
def balanceData():	
	global train_test, num_neg, num_pos

	rm_amount = num_pos - num_neg
	uids = train_test.keys()
	while rm_amount > 0:
		idx = random.randrange(len(uids))
		uid = uids[idx]
		if len(train_test[uid]['interested']) == 0:
			del uids[idx]
			continue

		idx = random.randrange(len(train_test[uid]['interested']))
		del train_test[uid]['interested'][idx]
		rm_amount -= 1


data = pd.read_csv('tmp/user_event.csv', dtype = {'user_id': object})
data.fillna('', inplace = True)

# extract
dataset = {}
train_test = {}

for idx, row in data.iterrows():	
	uid = row['user_id']
	dataset[uid] = {'attend': [], 'maybe': [], 'declined': []}
	train_test[uid] = {'interested': [], 'uninterested': []}

	attend = row['attend'].split()	
	maybe = row['maybe'].split()
	declined = row['declined'].split()
	
	# assume first half event in each category (attend, maybe, declined) is existed in data,
	# second half is not existed and will be used for training and testing
	bound = int((len(attend) + 1) / 2)
	dataset[uid]['attend'] = attend[:bound]
	train_test[uid]['interested'] = attend[bound:]

	bound = int((len(maybe) + 1) / 2)
	dataset[uid]['maybe'] = maybe[:bound]
	train_test[uid]['interested'] += maybe[bound:]
	
	bound = int((len(declined) + 1) / 2)
	dataset[uid]['declined'] = declined[:bound]
	train_test[uid]['uninterested'] = declined[bound:]

	# count for amount of uninterested events in train_test dataset
	num_neg += len(train_test[uid]['uninterested'])
	# count for amount of interested events in train_test dataset
	num_pos += len(train_test[uid]['interested'])

#print('extract complete')

# Store dataset
oup = open('tmp/dataset.csv', 'w')
oup.write('user_id,attend,maybe,declined\n')

for user, event in dataset.iteritems():
	oup.write(user)
	oup.write(',')
	for eventId in event['attend'][:-1]:
		oup.write(eventId + " ")
	if (len(event['attend']) > 0): 
		oup.write(event['attend'][-1])
	oup.write(',')

	for eventId in event['maybe'][:-1]:
		oup.write(eventId + " ")
	if (len(event['maybe']) > 0): 
		oup.write(event['maybe'][-1])
	oup.write(',')

	for eventId in event['declined'][:-1]:
		oup.write(eventId + " ")
	if (len(event['declined']) > 0): 
		oup.write(event['declined'][-1])
	oup.write('\n')

oup.close()
#print('dataset stored')

#balanceData()
# select data for train set and test set
train_out = open('tmp/train.csv', 'w')
test_out = open('tmp/test.csv', 'w')
train_out.write('user_id,event_id,interested\n')
test_out.write('user_id,event_id,interested\n')

uids = train_test.keys()
# create pool of train_test data
pool = {'0': [], '1': []}
for uid, events in train_test.iteritems():
	for event in events['interested']:
		pool['1'].append([uid, event])
	for event in events['uninterested']:
		pool['0'].append([uid, event])
random.shuffle(pool['1'])
random.shuffle(pool['0'])

#train_amount = int((num_neg * 4 + 1) / 3)
train_amount = int(((len(pool['0']) + len(pool['1'])) * 2 + 1) / 3)
labels = pool.keys()
# generate train set first
while train_amount > 0:
	catg = random.randrange(2)
	label = labels[catg]
	if len(pool[label]) == 0:
		catg = (catg + 1) % 2
		label = labels[catg]
	
	idx = random.randrange(len(pool[label]))
	train_out.write(pool[label][idx][0] + ',')
	train_out.write(pool[label][idx][1] + ',')
	train_out.write(label + '\n')
	del pool[label][idx]
	train_amount -= 1
	
# the rest is test set
for label, cases in pool.iteritems():	
	for case in cases:
		test_out.write(case[0] + ',')
		test_out.write(case[1] + ',')
		test_out.write(label + '\n')
	
train_out.close()
test_out.close()

# random.shuffle(<object>): generate a random permutation
