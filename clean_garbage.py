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

# find . -type f ! -name "*.*" -exec mv {} {}.txt \;
# find -type f -name '*.txt' | while read f; do mv "$f" "${f%.txt}"; done
# find -type f -name '*.txt' -print0 | while read -d $'\0' f; do mv "$f" "${f%.txt}"; done

"""
import pandas as pd
threshold = '2015-12-23T06:00:00+0700'
event_name = pd.read_csv('data/event_name.csv', names = ['event_id', 'name', 'extra'], dtype = {'event_id': object})
events = pd.read_csv('data/events.csv')
event_name = event_name.drop([0])
event_name.index = range(len(event_name))
event_name['start_time'] = events['start_time']
event_name = event_name[event_name.start_time > threshold]
event_name.sort_values(by = 'start_time', ascending = False, inplace = True)
event_name.drop(['extra'], axis = 1, inplace = True)
event_name.to_csv('event_name_new.csv', index = False)
"""

