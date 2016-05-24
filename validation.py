import random
from dateutil.parser import parse

import pandas as pd
import numpy as np

from model import Model
import formula

events = pd.read_csv('data/events.csv', dtype = {'event_id': object, 'owner': object, 'place_id': object})
events.fillna('', inplace = True)
places = pd.read_csv('data/places.csv', dtype = {'place_id': object})
places.fillna('', inplace = True)
event_tfidf = pd.read_csv('data/event_tfidf.csv', dtype = {'event_id': object})
user_event = pd.read_csv('tmp/dataset.csv', dtype = {'user_id': object})
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
        score.append(formula.cos_sim(vec_e, vec_ie))

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
        score.append(formula.cos_sim(vec_e, vec_he))

    feature[0] = min(score)
    feature[1] = max(score)
    feature[2] = sum(score) / len(hated)

    return feature

# Compute distance(miles) between current event and user's interested events (in user's history)
def get_distances(uid, eid):
    u_his = user_event[user_event.user_id == uid]
    interested = u_his.at[u_his.index[0], 'attend'].split() + u_his.at[u_his.index[0], 'maybe'].split()
    score = [0]
    
    feature = [0, 0]
    if (len(interested) == 0):
        return feature

    # get coordinate of eid
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
    feature[0] = max(score)
    feature[1] = sum(score) / len(interested)

    return feature

# Calculate day of week feature, owner-related feature
def get_dOW_owner(uid, eid):
    u_his = user_event[user_event.user_id == uid]
    interested = u_his.at[u_his.index[0], 'attend'].split() + u_his.at[u_his.index[0], 'maybe'].split()
    hated = u_his.at[u_his.index[0], 'declined'].split()

    feature = [0, 0, 0, 0]

    # get owner and day of week(DOW) of eid
    e = events[events.event_id == eid]
    o = e.at[e.index[0], 'owner']
    DOW = e.at[e.index[0], 'start_time']
    DOW = parse(DOW).weekday()
    
    # get interested events
    i_e = events[events.event_id.isin(interested)]
    # get hated events
    h_e = events[events.event_id.isin(hated)]

    # feature for interested events
    dayOfWeek = [0] * 7
    owner = {}
    for idx, event in i_e.iterrows():		
        utc = event['start_time']
        dayOfWeek[parse(utc).weekday()] += 1
        oid = event['owner']
        if oid not in owner:
            owner[oid] = 0
        owner[oid] += 1
        
    if (sum(dayOfWeek) != 0):
        feature[0] = float(dayOfWeek[DOW]) / sum(dayOfWeek)
    if o in owner:
        total = 0
        for key, val in owner.iteritems():
            total += val
        feature[2] = float(owner[o]) / total

    # feature for hated events
    dayOfWeek = [0] * 7
    owner = {}
    for idx, event in h_e.iterrows():		
        utc = event['start_time']
        dayOfWeek[parse(utc).weekday()] += 1
        oid = event['owner']
        if oid not in owner:
            owner[oid] = 0
        owner[oid] += 1
        
    if (sum(dayOfWeek) != 0):
        feature[1] = float(dayOfWeek[DOW]) / sum(dayOfWeek)
    if o in owner:
        total = 0
        for key, val in owner.iteritems():
            total += val
        feature[3] = float(owner[o]) / total

    return feature
    
    
# Generate feature
def process_event(uid, eid):			
	
    interested_feat = get_interested_sim(uid, eid)
    hated_feat = get_hated_sim(uid, eid)
    dist_feat = get_distances(uid, eid)
    dow_owner_feat = get_dOW_owner(uid, eid)
    features = interested_feat + hated_feat + dist_feat + dow_owner_feat

    important_feats = [1, 2, 4, 5, 7, 9, 10, 11, 12]
    #features = [features[i] for i in important_feats]
    
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

def run_validation(judged_class = 0, epoch = 10):
    data = get_data('tmp/train.csv')    
    idx = range(len(data['X']))
    leng = len(data['X']) * 2 / 3 + 1
    while (epoch > 0):
        random.shuffle(idx)        
        test = {'X': [], 'Y': []}
        train = {'X': [], 'Y': []}

        test['X'] = [data['X'][i] for i in idx[leng:]]
        test['Y'] = [data['Y'][i] for i in idx[leng:]]
        train['X'] = [data['X'][i] for i in idx[:leng]]
        train['Y'] = [data['Y'][i] for i in idx[:leng]]

        C = 0.03
        #C = 0.3
        m1 = Model(judged_class = judged_class, C = C) 
        m1.fit(train['X'], train['Y'])
        m1.analyze_threshold(test['X'], test['Y'])
        epoch = epoch - 1        

def frange(start, stop, step):
    r = start
    while r < stop:
        yield r
        r += step
'''
# Visualize weights effect
out_stats = open('stats.txt', 'a')
run_statistics()
out_stats.close()
'''
#run_full()
#analyze(judged_class = 1)
#run_validation()
run_validation(judged_class = 1)


'''
features:
0 - min among similarities of interested events
1 - max among similarities of interested events
2 - avg of similarities of interested events
3 - min among similarities of hated events
4 - max among similarities of hated avents
5 - avg of similarities of hated events
6 - max among distances of interested events
7 - avg of distances of interested events
8 - day of week similarity with interested events
9 - day of week similarity with hated events
10 - owner similarity with interested events
11 - owner similarity with hated events

features: max_i_sim, avg_i_sim, max_h_sim, avg_h_sim, max_dist, dow_i,
dow_h, owner_i, owner_h
'''










    
