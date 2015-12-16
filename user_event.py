#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import pandas as pd

user_event = {}
attendee = pd.read_csv('data/attendees.csv', dtype = {'event_id': object})
event = pd.read_csv('data/events.csv')
attendee.fillna('', inplace = True)

# append start_time column to attendee dataframe
attendee['start_time'] = event['start_time']
# sort
attendee.sort_values(by = 'start_time', ascending = True, inplace = True)

# extract
for idx, event in attendee.iterrows():
	userId = event['attend'].split()
	for user in userId:
		if user not in user_event:
			user_event[user] = {'attend': [], 'maybe': [], 'declined': []}
		user_event[user]['attend'].append(event['event_id'])
	userId = event['maybe'].split()
	for user in userId:
		if user not in user_event:
			user_event[user] = {'attend': [], 'maybe': [], 'declined': []}
		user_event[user]['maybe'].append(event['event_id'])
	userId = event['declined'].split()
	for user in userId:
		if user not in user_event:
			user_event[user] = {'attend': [], 'maybe': [], 'declined': []}
		user_event[user]['declined'].append(event['event_id'])

print('extract complete')
oup = open('tmp/user_event_full.csv', 'w')
oup.write('user_id,attend,maybe,declined\n')

for user,event in user_event.iteritems():
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
print('write complete')






		
