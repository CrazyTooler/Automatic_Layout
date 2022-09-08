import pymysql
import pandas as pd
import numpy as np
from pgmpy.models import BayesianNetwork
from pgmpy.estimators import MaximumLikelihoodEstimator
from pgmpy.readwrite import BIFWriter, BIFReader

def get_feature(article_num): 
    db = pymysql.connect(host="121.196.99.106",port=3306,user="root",password="zzysky123",database="rawnewsdata",charset="utf8")
    cursor = db.cursor()
    sql = "select pageid,article_w,atitle_char_count,text_char_count,subtitle_area_count, picture_count,picture_area,article_area,page_article_count,text_char_count_ratio,ispicnews,ishead,ishead_zuoshang from headpages_style order by pageid;"
    data = pd.read_sql(sql, db).fillna(0)
    db.close()
    ##############################################
    # article_num = 5
    data = data[data['page_article_count'] == article_num]
    data_pageid_sum = data.groupby('pageid').sum()
    ##############################################
    ##############################################
    x1 = data.loc[data['ishead']==1].loc[:,['atitle_char_count','text_char_count_ratio','subtitle_area_count','picture_count','article_w']]
    x2 = data.loc[data['ishead_zuoshang']==1].loc[:,['atitle_char_count','text_char_count_ratio','subtitle_area_count','picture_count','article_w']]
    x1.iloc[:,0] /= np.array(data_pageid_sum.loc[:,'atitle_char_count'])+0.0001
    x1.iloc[:,2] /= np.array(data_pageid_sum.loc[:,'subtitle_area_count'])+0.0001
    x1.iloc[:,3] /= np.array(data_pageid_sum.loc[:,'picture_count'])+0.0001
    x2.iloc[:,0] /= np.array(data_pageid_sum.loc[:,'atitle_char_count'])+0.0001
    x2.iloc[:,2] /= np.array(data_pageid_sum.loc[:,'subtitle_area_count'])+0.0001
    x2.iloc[:,3] /= np.array(data_pageid_sum.loc[:,'picture_count'])+0.0001
    return x1,x2

def get_boundaries(raw, tiers):
    boundaries = [[] for i in range(raw.shape[1])]
    vrange =  np.max(raw, axis=0) - np.min(raw, axis=0)
    for i in range(raw.shape[1]):
        ti = tiers[i]
        vlength = vrange[i] / ti + 0.001
        vleft = np.min(raw, axis=0)[i] - 0.001
        for j in range(ti):
            boundaries[i].append((vleft, vleft + vlength))
            vleft += vlength
    return boundaries

def re_label(raw, boundaries, tiers):
    for i in range(raw.shape[0]):
        for j in range(raw.shape[1]):
            for k in range(tiers[j]):
                if boundaries[j][k][0] <= raw.iloc[i,j] < boundaries[j][k][1]:
                    raw.iloc[i,j] = k
                    break
                elif k == tiers[j] - 1:
                    raw.iloc[i,j] = k // 2
    raw = pd.DataFrame(raw,dtype=int)
    return raw

if __name__ == '__main__':
    for article_num in range(6,3,-1):
        #traindata#################################
        x1,x2 = get_feature(article_num)
        tiers = [4,5,2,2,3]#atitle_char_count,text_char_count_ratio,subtitle_area_count,picture_count,article_w
        state_names = {}
        for node,t in zip(x1.columns,tiers):
            state_names[node] = list(range(t))
        x = x2
        boundaries = get_boundaries(x, tiers)
        boundaries[-1] = [(0,0.35),(0.65,0.8),(0.9,1.05)]
        data = re_label(x, boundaries, tiers)
        #fitdata#################################
        train_data = data
        model = BayesianNetwork([('atitle_char_count', 'article_w'), 
                        ('text_char_count_ratio', 'article_w'), 
                        ('subtitle_area_count', 'article_w'), 
                        ('picture_count','article_w')])
        model.fit(train_data, state_names=state_names)
        writer = BIFWriter(model)
        writer.write_bif(filename=f'./prefer_model/head_width/prefer_articlewidth_n={article_num}.bif')
        # #testdata#############################
        # test_data = data.iloc[[-1],:]
        # test_data = test_data.drop('article_w', axis=1)
        # #prefer#####################
        # model = BIFReader(f'./prefer_model/head_width/prefer_articlewidth_n={article_num}.bif').get_model(int)
        # pred_data = model.predict(test_data).loc[:,'article_w'].to_list()
        # print(pred_data)