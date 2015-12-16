#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Due to the fact that crawled data has many garbage events, 
# the purpose of this script is removing the garbage from data

import pandas as pd
import os
import csv

# Collect all filenames
path = 'descriptions/'
filenames = []
for f in os.listdir(path):
	filenames.append(f)
filenames = set(filenames)

# All garbage
garbage = pd.read_csv('data/garbage.csv', dtype = {'event_id': object})
garbage = set(list(garbage['event_id']))

deleted = list(filenames.intersection(garbage))
filenames = filenames - garbage
print(len(filenames))

for f in deleted:
	os.remove(path + f)
	print('removed {}'.format(f))

# Clean events.csv
events = pd.read_csv('data/events.csv', dtype = {'event_id': object, 'owner': object, 'place_id': object})
events = events[events.event_id.isin(filenames)]
events.to_csv('data/used_events.csv', index = False)
'''
# Clean attendees.csv
attendees = pd.read_csv('data/attendees.csv', dtype = {'event_id': object})
attendees = attendees[attendees.event_id.isin(filenames)]
attendees.to_csv('data/used_attendees.csv', index = False)

# Clean event_name.csv
inp = open('data/event_name.csv')
rd = csv.reader(inp)
oup = open('data/used_event_name.csv', 'w')
wt = csv.writer(oup, delimiter = ',')

wt.writerow(next(rd)) # writer header
i = 0
for row in rd:
	if str(row[0]) in filenames:
		wt.writerow(row)
		i += 1

print(i)
inp.close()
oup.close()
'''


