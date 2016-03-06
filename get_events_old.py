import facebook
import requests
import csv
import pandas as pd

# excepted events
alrEvent = pd.read_csv('crawled_data/events.csv', dtype = {'event_id': object})
alrEvent = list(alrEvent['event_id'])
# All garbage
garbage = pd.read_csv('crawled_data/garbage.csv', dtype = {'event_id': object})
garbage = list(garbage['event_id'])

alrEvent = set(alrEvent + garbage)

### Change access token (and possible keywords) before running
accessToken = 'CAAXYU3sVODIBACjHifndiII9mIOs6ZBVGtEIXo6jy6PgcxqONyR1RstgxgmuMBuZBjLilpwpic5zZBSJGjyFv2TRlZBzD00ju7TddJ7UAXWwJle3ZBVrIVWWnIJIhoxvCqmP2NZCWnbZBZBBC5R1xKhXzEL0j3Czr8ZCSBQ6YXi7UVffviI5WwdTF'

graph = facebook.GraphAPI(access_token = accessToken)#, version = '2.5')
events = graph.request(path = 'v2.5/search', args = {'q': 'Thanh pho Ho Chi Minh', 'type': 'event', 'fields': 'id,owner,name,description,start_time,place,\
	attending.summary(true),maybe.summary(true),declined.summary(true)'})

count = 0
event_out = open('crawled_data/tmp_events.csv', 'w')
attend_out = open('crawled_data/tmp_attendees.csv', 'w')
#user_out = open('tmp_users.csv', 'w')
event_name = open('crawled_data/tmp_event_name.csv', 'w')

#write header
event_out.write('event_id,owner,start_time,place_id\n')
attend_out.write('event_id,attend,maybe,declined\n')
#user_out.write('user_id,user_name\n')
event_name.write('event_id,name\n')

while True:
	try:
		for event in events['data']:	
			# check if event had been already crawled
			if event['id'] in alrEvent:
				continue

			alrEvent.add(event['id'])
			########## write information of event
			event_out.write(event['id']) # event_id
			event_out.write(',')
			event_out.write(event['owner']['id']) # owner
			event_out.write(',')					
			event_out.write(event['start_time']) # start_time
			event_out.write(',')							
			
			place = event.get('place', None)
			if place is not None:			
				event_out.write(str(place.get('id', ''))) # place_id						
			event_out.write('\n')	

			######### write events' name
			event_name.write(event['id']) # event_id
			event_name.write(',')
			event_name.write(event['name'].encode('utf8')) # event_name								
			event_name.write('\n')		
			
			########## write event's attendees
			attend_out.write(event['id']) # event_id
			attend_out.write(',')
			
			attending = event['attending']
			maybe = event['maybe']
			declined = event['declined']
			
			while True:
				try:
					for user in attending['data'][:-1]: # iterate list except last
						attend_out.write(user['id'] + ' ')
						#user_out.write((user['id'] + ',' + user['name'] + '\n').encode('utf8'))
					if len(attending['data']) > 0:
						attend_out.write(attending['data'][-1]['id'])						
						#user_out.write((attending['data'][-1]['id'] + ',' + attending['data'][-1]['name'] + '\n').encode('utf8'))

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
						#user_out.write((user['id'] + ',' + user['name'] + '\n').encode('utf8'))
					if len(maybe['data']) > 0:
						attend_out.write(maybe['data'][-1]['id'])			
						#user_out.write((maybe['data'][-1]['id'] + ',' + maybe['data'][-1]['name'] + '\n').encode('utf8'))

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
						#user_out.write((user['id'] + ',' + user['name'] + '\n').encode('utf8'))
					if len(declined['data']) > 0:
						attend_out.write(declined['data'][-1]['id'])			
						#user_out.write((declined['data'][-1]['id'] + ',' + declined['data'][-1]['name'] + '\n').encode('utf8'))

					tmp = declined['paging'].get('next', None)
					if tmp is not None:
						attend_out.write(' ')
					declined = requests.get(declined['paging']['next']).json()
				except KeyError:
					break
			attend_out.write('\n')
			
			######### write description
			tmp_out = open('descriptions/' + event['id'], 'w')
			tmp_out.write(event['description'].encode('utf8'))
			tmp_out.close()
			
			count = count + 1
			print(count)
		events = requests.get(events['paging']['next']).json()		
	except KeyError:
		print(count)
		break

event_out.close()
attend_out.close()
#user_out.close()
event_name.close()

'''
HCMC | Saigon | TPHCM | Ho Chi Minh City | Sai gon
id,user_id,name,description,start_time,end_time,city,country,latitude,longitude

"latitude": 10.776423824576,
          "longitude": 106.70331625206,
"latitude": 10.7694,
          "longitude": 106.682,'''
