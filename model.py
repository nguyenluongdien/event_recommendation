#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import numpy as np
        
class Model:
	def __init__(self, has_none=None, C=0.03, n_est=100):
		print C
		self.models = [			
			RandomForestClassifier(n_estimators=n_est),
			LogisticRegression(C=C, penalty='l1')
		]
		self.has_none = has_none
    
	def fit(self, X, Y):		
		self.models[0].fit(X, Y)	
		self.models[1].fit(X, Y)
	
	def replace(self, res):
		if res < 0.5:
			return 0		
		else:
			return 1
        
	def test(self, X):		
		rez = self.models[0].predict_proba(X)[:, 1] * 0.69     
		rez += self.models[1].predict_proba(X)[:, 1] * 0.57

		rez = map(self.replace, rez)
        
		return rez
    
