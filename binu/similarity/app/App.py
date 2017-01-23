'''
Created on Jan 18, 2017

@author: binu.k
'''
from __future__ import print_function

import editdistance
import string
import operator
import warnings
import sys,argparse
from scipy.stats.stats import pearsonr
from sklearn.metrics.pairwise import cosine_similarity 
from sklearn.cluster import AffinityPropagation

import numpy as np
import pandas as pd

from binu.similarity.app.appconf import techConfig;
from binu.similarity.metric import MetricFactory

# warnings.filterwarnings("ignore",category=DeprecationWarning)

class App:
    def __init__(self, filename):
        print("Loading Data.......")
        self.readData(filename)
        print("\tInput File        : " + filename)
        print("\tNumber of records : " + str(self.data.shape[0]))
        print("\tNumber of states  : " + str(self.stateData.shape[0]))
        print("Loading Data.......\tCompleted")
        
        print("Clustering Names...\t", end='')
        self.groupSimilarEntities((self.data[1]).unique())
        self.appendGroupInfo()
        self.updateCount();
        print("Completed")
        
    def readData(self, filename):
        self.data = pd.read_csv(filename, header=None)
        self.stateData = self.data.iloc[:,[0,3]].groupby(by=[0]).sum().reset_index();
        
    def getSimilarityMatrix(self, uniqNames):
        similarityMatrix = -1 * np.array([[editdistance.eval(w1, w2) for w1 in uniqNames] for w2 in uniqNames])
        return similarityMatrix

    def groupSimilarEntities(self, refCatgories):
        self.groupInfo = pd.DataFrame();
#         groupInfo.columns = list('name', 'label')
        for catg in refCatgories:
            names = self.data.loc[(self.data.iloc[:,1] == catg)][2]
            uniqNames = names.unique();
#             print(uniqNames)
            similarityMatrix = self.getSimilarityMatrix(uniqNames)
            
            affprop = AffinityPropagation(affinity="precomputed", damping=0.5)
            affprop.fit(similarityMatrix)
            self.groupInfo = self.groupInfo.append(pd.DataFrame({0: catg, 1 : uniqNames, 
                                                        2 : affprop.labels_}),ignore_index=True)
            
    def sumAll(self, x):
        return pd.Series(dict(cnt = x['cnt'].sum(), name = "%s" % ', '.join(x['name'])))
     
    def appendGroupInfo(self):
        self.data = self.data.merge(self.groupInfo, how='left', left_on = [1,2], right_on=[0,1], suffixes=('_org', '_grp'))
        self.data = self.data.loc[:, ['0_org','1_org', '2_org', 3, '2_grp']]
        self.data.columns = ['state', 'gender', 'name', 'cnt', 'group']
        self.data = self.data.groupby(by=['state', 'gender','group']).apply(self.sumAll).reset_index()
#         print(self.data.head(50))
        
    def findSimilarity(self, refEntity):
        if((self.data.iloc[:,0] == refEntity).sum() == 0 ):
            print("\tEntity '" + refEntity + "' not present !")
            return None
        
        categories = (self.data['gender']).unique()
        entities = self.data.iloc[:,0].unique()
        initValue = [0] * len(entities)
        associationList = dict(zip(entities, initValue))
        columnsList = ['group', 'cnt', 'ratio']
        refMetric = 'ratio_ref'
        othMetric = 'ratio_oth'
        
        m = MetricFactory.getMetric(techConfig['similarity'])
        
        for catg in categories:
            self.dataRef = self.data.loc[(self.data.iloc[:,0] == refEntity) 
                                    & (self.data.iloc[:,1] == catg)].loc[:,columnsList]
            for entity in entities:
                if(entity == refEntity):
                    continue;
                
                dataOther = self.data.loc[(self.data.iloc[:,0] == entity) 
                                    & (self.data.iloc[:,1] == catg)].loc[:,columnsList]
                refCatgCount = dataOther.loc[:,'cnt'].sum()
                totalCount = self.stateData.loc[self.stateData.iloc[:,0] == entity].iat[0, 1]
                merge = pd.merge(self.dataRef, dataOther, left_on='group', right_on='group',
                                 how="outer", indicator=True, suffixes=('_ref', '_oth'))
               
                merge[refMetric].fillna(0, inplace=True)
                merge[othMetric].fillna(0, inplace=True)
                
                association = m.value(merge.loc[:, refMetric], merge.loc[:, othMetric])
                associationList[entity] += (association * refCatgCount / totalCount)
#                 print("Association between " + refEntity + " and " + entity + " is " + str(association))
                
        return associationList
    
    def updateCount(self):
        df = self.data.loc[:,['state', 'gender', 'cnt']]
        summarydf = df.groupby(['state', 'gender']).sum().reset_index()
        
        self.data = self.data.merge(summarydf,on=['state', 'gender'], suffixes=['', 'right'])
        self.data['ratio'] = self.data['cnt'] / self.data['cntright']

    def showResult(self, scores):
        print("\t-----------------------------------------")
        print("\tBest Match   - " + str(scores[0][0]) + " with " + str(round(scores[0][1], 4)))
        print("\tSecond Match - " + str(scores[1][0]) + " with " + str(round(scores[1][1], 4)))
        print("\tThird Match  - " + str(scores[2][0]) + " with " + str(round(scores[2][1], 4)))
        print("\t-----------------------------------------")
        
def readInput(cmdArgs):
    parser = argparse.ArgumentParser(description='Application to compute similarity')
    parser.add_argument('-i','--input', help='Input file name',required=True)
    parser.add_argument('-s','--states',help='State Names', required=True)
    args = parser.parse_args()
    
    return args.input, args.states

if __name__ == '__main__':
    filename,states = readInput(sys.argv)
    app = App(filename)
    entityList = string.split(states, sep=",")
    
    for entity in entityList:
        print("Finding similar states to '" + entity + "'")
        scores = app.findSimilarity(entity.upper())
        scores = scores
        if(scores != None):
            sortedScores = sorted(scores.items(), key=operator.itemgetter(1), reverse=True)
            app.showResult(sortedScores)
        print("Similarities.....\tCompleted ")