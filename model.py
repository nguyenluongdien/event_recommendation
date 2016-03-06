#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
import numpy as np
        
class Model:
	def __init__(self, judged_class = 0, threshold = 0.6, w0 = 0.69, w1 = 0.57, C=0.03, n_est=100):
		print C
		self.models = [			
			RandomForestClassifier(n_estimators=n_est),
			LogisticRegression(C=C, penalty='l1'),
		]
		self.judged_class = judged_class
		self.threshold = threshold
		self.w0 = w0
		self.w1 = w1
    
	def fit(self, X, Y):		
		self.models[0].fit(X, Y)			
		self.models[1].fit(X, Y)

	def analyze_threshold(self, X, Y):
		rez = self.models[0].predict_proba(X)[:, self.judged_class]		
		prop = [[p] for p in rez]		
		clf = SVC()
		clf.fit(prop, Y)
		support_vectors = clf.support_vectors_		
		threshold = sum(support_vectors) * 1.0 / len(support_vectors)
		print(threshold)
		print(self.models[0].feature_importances_)
		pass
	
	def replace(self, res):
		if res < self.threshold:
			return (self.judged_class + 1) % 2	
		else:
			return self.judged_class

	def replace1(self, res):
		if res[0] < res[1]:
			return 1
		else:
			return 0
        
	def test(self, X):		
		rez = self.models[0].predict_proba(X)[:, self.judged_class] * self.w0 
		rez += self.models[1].predict_proba(X)[:, self.judged_class] * self.w1
		rez = map(self.replace, rez)

		#rez = self.models[0].predict_proba(X) * self.w0
		#rez += self.models[1].predict_proba(X) * self.w1
		#rez = map(self.replace1, rez)
        
		return rez
    
