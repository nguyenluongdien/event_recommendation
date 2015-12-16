#!/usr/bin/env python2

import facebook
import requests
import csv
import json
import pandas as pd

### Change access token (and possible keywords) before running
accessToken = 'CAAXYU3sVODIBACjHifndiII9mIOs6ZBVGtEIXo6jy6PgcxqONyR1RstgxgmuMBuZBjLilpwpic5zZBSJGjyFv2TRlZBzD00ju7TddJ7UAXWwJle3ZBVrIVWWnIJIhoxvCqmP2NZCWnbZBZBBC5R1xKhXzEL0j3Czr8ZCSBQ6YXi7UVffviI5WwdTF'

graph = facebook.GraphAPI(access_token = accessToken)#, version = '2.5')

eventId = pd.read_csv('Archive/events.csv', dtype = {'eventId': object})
eventId = set(list(eventId['eventId']))

alrEvent = pd.read_csv('data/events.csv', dtype = {'event_id': object})
alrEvent = set(list(alrEvent['event_id']))

# extra
tmp = pd.read_csv('crawled_data/events.csv', dtype = {'event_id': object})
tmp = set(list(tmp['event_id']))
alrEvent = alrEvent.union(tmp)

print(len(alrEvent))
print(len(eventId))
eventId = list(eventId - alrEvent)
print(len(eventId))

count = 0
event_out = open('crawled_data/tmp_events.csv', 'w')
attend_out = open('crawled_data/tmp_attendees.csv', 'w')
event_name = open('crawled_data/tmp_event_name.csv', 'w')

#write header
event_out.write('event_id,owner,start_time,place_id\n')
attend_out.write('event_id,attend,maybe,declined\n')
event_name.write('event_id,name\n')
	
i = 0
while i < len(eventId):
	ids = eventId[i:(i+49)]

	events = graph.request(path = 'v2.5/', args = {'ids': ids, 'fields': 'id,owner,name,description,start_time,place,attending.summary(true),maybe.summary(true),declined.summary(true)'})

	while True:
		try:
			for event in events:	
				print(event)
				########## write information of event
				event_out.write(events[event]['id']) # event_id
				event_out.write(',')
				event_out.write(events[event]['owner']['id']) # owner
				event_out.write(',')
				event_out.write(events[event]['start_time']) # start_time
				event_out.write(',')			
			
				place = events[event].get('place', None)
				if place is not None:			
					event_out.write(str(place.get('id', ''))) # place_id													
				event_out.write('\n')

				######### write events' name
				event_name.write(events[event]['id']) # event_id
				event_name.write(',')
				event_name.write(events[event]['name'].encode('utf8')) # event_name								
				event_name.write('\n')		
			
				########## write event's attendees
				attend_out.write(events[event]['id']) # event_id
				attend_out.write(',')
			
				attending = events[event]['attending']
				maybe = events[event]['maybe']
				declined = events[event]['declined']
			
				while True:
					try:
						for user in attending['data'][:-1]: # iterate list except last
							attend_out.write(user['id'] + ' ')
						if len(attending['data']) > 0:
							attend_out.write(attending['data'][-1]['id'])						

						tmp = attending['paging'].get('next', None)
						if tmp is not None:
							attend_out.write(' ')
						attending = requests.get(attending['paging']['next']).json()
					except KeyError:
						break
				attend_out.write(',')
			
				while True:
					try:
						for user in maybe['data'][:-1]:
							attend_out.write(user['id'] + ' ')
						if len(maybe['data']) > 0:
							attend_out.write(maybe['data'][-1]['id'])			

						tmp = maybe['paging'].get('next', None)
						if tmp is not None:
							attend_out.write(' ')
						maybe = requests.get(maybe['paging']['next']).json()
					except KeyError:
						break
				attend_out.write(',')
			
				while True:
					try:
						for user in declined['data'][:-1]:
							attend_out.write(user['id'] + ' ')
						if len(declined['data']) > 0:
							attend_out.write(declined['data'][-1]['id'])			

						tmp = declined['paging'].get('next', None)
						if tmp is not None:
							attend_out.write(' ')
						declined = requests.get(declined['paging']['next']).json()
					except KeyError:
						break
				attend_out.write('\n')

				######### write description
				tmp_out = open('descriptions/' + event, 'w')
				tmp_out.write(events[event]['description'].encode('utf8'))
				tmp_out.close()
			
				count = count + 1
				print(count)
			events = requests.get(events['paging']['next']).json()		
		except KeyError:
			print(count)
			break
	i = i + 50

event_out.close()
attend_out.close()
event_name.close()
