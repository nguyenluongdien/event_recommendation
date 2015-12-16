import facebook
import requests
import csv

### Change access token (and possible keywords) before running
accessToken = 'CAAXYU3sVODIBACjHifndiII9mIOs6ZBVGtEIXo6jy6PgcxqONyR1RstgxgmuMBuZBjLilpwpic5zZBSJGjyFv2TRlZBzD00ju7TddJ7UAXWwJle3ZBVrIVWWnIJIhoxvCqmP2NZCWnbZBZBBC5R1xKhXzEL0j3Czr8ZCSBQ6YXi7UVffviI5WwdTF'

graph = facebook.GraphAPI(access_token = accessToken)#, version = '2.5')
placeId = set()

inp = open('data/events.csv')
rd = csv.reader(inp)
next(rd)

for row in rd:
	placeId.add(row[3])
placeId.discard('')
placeId = list(placeId)
inp.close()
print(len(placeId))

count = 0
out = open('data/places.csv', 'w')
out.write('place_id,name,city,country,lat,long\n')

i = 0
while i < len(placeId):
	ids = placeId[i:(i+49)]
	places = graph.request(path = 'v2.5/', args = {'ids': ids, 'fields': 'id,name,location'})
	
	while True:
		try:
			for place in places:
				out.write(places[place]['id'])
				out.write(',')
				out.write("\"" + places[place].get('name', '').encode('utf8') + "\"")
				out.write(',')
				location = places[place].get('location', None)
				if location is not None:
					out.write("\"" + location.get('city', '').encode('utf8') + "\"")
				out.write(',')
				if location is not None:
					out.write(location.get('country', ''))
				out.write(',')
				if location is not None:
					out.write(str(location.get('latitude', '')))
				out.write(',')
				if location is not None:
					out.write(str(location.get('longitude', '')))
				out.write('\n')			
				count += 1
			
			places = requests.get(places['paging']['next']).json()

		except KeyError:
			print(count)
			break
	
	i = i + 50

out.close()













