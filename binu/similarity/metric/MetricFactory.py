'''
Created on Jan 22, 2017

@author: binu.k
'''
from binu.similarity.metric.PearsonCorrMetric import PearsonCorrMetric
from binu.similarity.metric.CosineSimilarity import CosineSimilarity

def getMetric(name):
        if(name == "pearson"):
            return PearsonCorrMetric()
        if(name == "cosine"):
            return CosineSimilarity()
        else:
            print('Error : Unknown metric - ' + name)