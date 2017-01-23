'''
Created on Jan 22, 2017

@author: binu.k
'''

from scipy.stats.stats import pearsonr
from binu.similarity.metric.SimilarityMetric import SimilarityMetric

class PearsonCorrMetric(SimilarityMetric):
    def __init__(self):
        pass
    
    def value(self, list1, list2):
        return pearsonr(list1, list2)[0]