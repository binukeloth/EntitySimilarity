'''
Created on Jan 18, 2017

@author: binu.k
'''
from __future__ import print_function

import editdistance
import operator
from scipy.stats.stats import pearsonr
from sklearn.cluster import AffinityPropagation
from sklearn.metrics.pairwise import cosine_similarity

import numpy as np
import pandas as pd

from binu.similarity.app.appconf import appConfig;

class App:
    def __init__(self, config):
        self.config = config
        print("Loading Data.......\t", end='')
        self.readData()
        print("Done")
        
        print("Clustering Names...\t", end='')
        self.groupSimilarEntities((self.data[1]).unique())
        self.appendGroupInfo()
        print("Done")
        
    def readData(self): 
        self.data = pd.read_csv(self.config['source'], header=None)
        
#         self.data = self.data.sort_values()
        
#     def levDistance(self, index1, index2):
#         i, j = int(index1[0]), int(index2[0])     # extract indices
#         return editdistance.eval(self.uniqNames[i], self.uniqNames[j])
        

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
            print("Entity '" + refEntity + "' not present !")
            return None
        
        categories = (self.data['gender']).unique()
        print(categories)
        
        entities = self.data.iloc[:,0].unique()
        initValue = [0] * len(entities)
        associationList = dict(zip(entities, initValue))
        
        for catg in categories:
            self.dataRef = self.data.loc[(self.data.iloc[:,0] == refEntity) & (self.data.iloc[:,1] == catg)].iloc[:,[2,3]]
            #print(self.dataRef.iloc[:,2].unique())
            for entity in entities:
                print("Running for " + catg + " & " + entity)
                
                if(entity == refEntity):
                    continue;
                
                print("Running for " + catg + " & " + entity)
                dataOther = self.data.loc[(self.data.iloc[:,0] == entity) & (self.data.iloc[:,1] == catg)].iloc[:,[2,3]]
    #             print(dataOther.iloc[:,2].unique())
#                 print(entity + ' has ' + dataOther.shape[0].__str__() + ' values')
                merge = pd.merge(self.dataRef, dataOther, left_on='group', right_on='group',
                                 how="outer", indicator=True, suffixes=('_ref', '_oth'))
               
                merge['cnt_ref'].fillna(0, inplace=True)
                merge['cnt_oth'].fillna(0, inplace=True)
                
    #             merge = merge.dropna(how='any')
#                 print(merge)
                
    #             association = cosine_similarity(merge.loc[:, '3_x'], merge.loc[:, '3_y'])
                association = pearsonr(merge.loc[:, 'cnt_ref'], merge.loc[:, 'cnt_oth'])
                associationList[entity] += association[0]
                print("Association between " + refEntity + " and " + entity + " is " + association[0].__str__())
                
#             print(associationList.sort_values(ascending=False)[:3])
        return associationList

    def showResult(self, scores):
        print("-----------------------------------------")
        print("Best Match   - " + scores[0][0].__str__() + " with " + str(round(scores[0][1], 4)))
        print("Second Match - " + scores[1][0].__str__() + " with " + str(round(scores[1][1], 4)))
        print("Third Match  - " + scores[2][0].__str__() + " with " + str(round(scores[2][1], 4)))
        print("-----------------------------------------")
        
        
if __name__ == '__main__':
    app = App(appConfig)
    
    repeat = 'y'
    while(repeat.lower() == 'y'):
        entity = raw_input('\n * Enter Reference state :')
        scores = app.findSimilarity(entity.upper())
        if(scores != None):
            sortedScores = sorted(scores.items(), key=operator.itemgetter(1), reverse=True)
            app.showResult(sortedScores)
        
        repeat = raw_input('\n\n * Do you want to continue? Press \'y\' to continue :')
    
#     list1 = app.findSimilarity(entity, 'M')
#     list2 = app.findSimilarity(entity, 'F')
#     
#     print((list1 + list2).sort_values(ascending=False)[:3])