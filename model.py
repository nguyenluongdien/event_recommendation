#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
import numpy as np
        
class Model:
	def __init__(self, threshold = 0.35, w0 = 0.69, w1 = 0.57, has_none=None, C=0.03, n_est=100):
		print C
		self.models = [			
			RandomForestClassifier(n_estimators=n_est),
			LogisticRegression(C=C, penalty='l1'),
		]
		self.has_none = has_none
		self.threshold = threshold
		self.w0 = w0
		self.w1 = w1
    
	def fit(self, X, Y):		
		self.models[0].fit(X, Y)			
		self.models[1].fit(X, Y)

	def analyze(self, X, Y):
		rez = self.models[0].predict_proba(X)[:, 1]		
		prop = [[p] for p in rez]		
		clf = SVC()
		clf.fit(prop, Y)
		support_vectors = clf.support_vectors_
		print(support_vectors)
		threshold = sum(support_vectors) * 1.0 / len(support_vectors)
		print(threshold)
		pass
	
	def replace(self, res):
		if res < self.threshold:
			return 0		
		else:
			return 1
        
	def test(self, X):		
		rez = self.models[0].predict_proba(X)[:, 1] * self.w0 
		rez += self.models[1].predict_proba(X)[:, 1] * self.w1
		#rez = self.models[0].predict_proba(X)[:, 1]
		#rez = self.models[1].predict_proba(X)[:, 1]

		rez = map(self.replace, rez)
        
		return rez
    
