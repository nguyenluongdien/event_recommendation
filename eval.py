import numpy as np
from formula import cos_sim

def apk(actual, predicted, k=10):    
    if len(predicted)>k:
        predicted = predicted[:k]

    score = 0.0
    num_hits = 0.0

    for i,p in enumerate(predicted):
        if p in actual and p not in predicted[:i]:
            num_hits += 1.0
            score += num_hits / (i+1.0)
    # the case when actual list have nothing (no positive)
    if min(len(actual), k) == 0:
        if len(predicted) == 0:
            return 1
        return 0	
    
    return score / min(len(actual), k)

def mapk(actual, predicted, k=200):    
    return np.mean([apk(a,p,k) for a,p in zip(actual, predicted)])

def dissimilarity(predicted, k=10):
    if len(predicted) <= 1:
        return 0
    if len(predicted)>k:
        predicted = predicted[:k]

    score = 0.0
    for i in range(len(predicted) - 1):
        for j in range(i+1, len(predicted)):
            score += (1 - cos_sim(predicted[i], predicted[j]))
    
    return score / (len(predicted) * (len(predicted) - 1) / 2)


#test cases
#a = [[1, 2], [3, 4], [0, 0]]
#b = [[1, 2], [0, 0]]
#print(dissimilarity(a))
#print(dissimilarity(b))
        

