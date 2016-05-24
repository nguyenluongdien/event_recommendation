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
	category = {0: 'attend', 1: 'maybe'} # constant dictionary
	global train_test, num_neg, num_pos

	rm_amount = num_pos - num_neg
	uids = train_test.keys()
	while rm_amount > 0:
		idx = random.randrange(len(uids))
		uid = uids[idx]
		catg = random.randrange(2)
		if len(train_test[uid][category[catg]]) == 0:
			catg = (catg + 1) % 2
		if len(train_test[uid][category[catg]]) == 0:
			del uids[idx]
			continue
		catg = category[catg]

		idx = random.randrange(len(train_test[uid][catg]))
		del train_test[uid][catg][idx]
		rm_amount -= 1


data = pd.read_csv('tmp/user_event.csv', dtype = {'user_id': object})
data.fillna('', inplace = True)

# extract
dataset = {}
train_test = {}

for idx, row in data.iterrows():	
	uid = row['user_id']
	dataset[uid] = {'attend': [], 'maybe': [], 'declined': []}
	train_test[uid] = {'attend': [], 'maybe': [], 'declined': []}

	attend = row['attend'].split()	
	maybe = row['maybe'].split()
	declined = row['declined'].split()
	
	# assume first half event in each category (attend, maybe, declined) is existed in data,
	# second half is not existed and will be used for training and testing
	bound = int((len(attend) + 1) / 2)
	dataset[uid]['attend'] = attend[:bound]
	train_test[uid]['attend'] = attend[bound:]

	bound = int((len(maybe) + 1) / 2)
	dataset[uid]['maybe'] = maybe[:bound]
	train_test[uid]['maybe'] = maybe[bound:]
	
	bound = int((len(declined) + 1) / 2)
	dataset[uid]['declined'] = declined[:bound]
	train_test[uid]['declined'] = declined[bound:]

	# count for amount of uninterested events in train_test dataset
	num_neg += len(train_test[uid]['declined'])
	# count for amount of interested events in train_test dataset
	num_pos += len(train_test[uid]['attend']) + len(train_test[uid]['maybe'])

#print('extract complete')

# Store dataset
oup = open('tmp/dataset.csv', 'w')
oup.write('user_id,attend,maybe,declined\n')

for user, event in dataset.iteritems():
	oup.write(user)
	oup.write(',')
	oup.write(' '.join(event['attend']))
	oup.write(',')

	oup.write(' '.join(event['maybe']))
	oup.write(',')

	oup.write(' '.join(event['declined']))
	oup.write('\n')

oup.close()
#print('dataset stored')

#balanceData()
# select data for train set and test set
train_out = open('tmp/train.csv', 'w')
test_out = open('tmp/test.csv', 'w')
train_out.write('user_id,event_id,interested\n')
test_out.write('user_id,event_id,interested\n')

for uid, event in train_test.iteritems():
	N = len(event['attend']) + len(event['maybe']) + len(event['declined']) # total number
	train_amount = int((N * 2 + 1) / 3)
	eids = [event['attend'] + event['maybe'], event['declined']]	
	#label = ['1', '1', '0'] # 1: interested, 0: not interested
	label = ['1', '0'] # 2 classes

	while train_amount > 0:
		i = random.randrange(len(eids))
		if (len(eids[i]) == 0):
			del eids[i]
			del label[i]
			continue

		j = random.randrange(len(eids[i])) # exclusive, oppose with randint (inclusive)
		train_out.write(uid + ',')
		train_out.write(eids[i][j] + ',')
		train_out.write(label[i] + '\n')
		del eids[i][j]
		train_amount = train_amount - 1
	
	for i in range(len(eids)):
		for j in range(len(eids[i])):
			test_out.write(uid + ',')
			test_out.write(eids[i][j] + ',')
			test_out.write(label[i] + '\n')
	
train_out.close()
test_out.close()

# random.shuffle(<object>): generate a random permutation
