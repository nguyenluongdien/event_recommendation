import pandas as pd
import csv

inp = open('data/events.csv')
rd = csv.reader(inp)

next(rd)
id1 = set()
for row in rd:
	id1.add(row[0])
inp.close()

inp = open('data/event_tfidf.csv')
rd = csv.reader(inp)

next(rd)
id2 = set()
for row in rd:
	id2.add(row[0])

missing = id1 - id2
print(len(id1))
print(len(id1.intersection(id2)))
print(missing)
