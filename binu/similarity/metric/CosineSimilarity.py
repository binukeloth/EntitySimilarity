'''
Created on Jan 22, 2017

@author: binu.k
'''

from scipy.spatial.distance import cosine

from binu.similarity.metric.SimilarityMetric import SimilarityMetric

class CosineSimilarity(SimilarityMetric):

    def __init__(self):
        pass
    
    def value(self, list1, list2):
        return (1 - cosine(list1, list2))