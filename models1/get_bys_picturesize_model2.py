import pymysql
import pandas as pd
import numpy as np
from pgmpy.models import BayesianNetwork
from pgmpy.estimators import MaximumLikelihoodEstimator
from pgmpy.readwrite import BIFWriter, BIFReader

def newsTypewithPic(data):
    if data['ispicnews'] == 0 and data['ishead_zuoshang']==0:
        return 0 
    elif data['ispicnews'] == 0 and data['ishead_zuoshang']==1:
        return 1
    elif data['ispicnews'] == 1 and data['ishead_zuoshang']==0:
        return 2
    else:
        return 3

def getAccuracy(y1,y2):
    n = len(y1)
    m = 0
    for i in range(n):
        if y1[i] == y2[i]:
            m += 1
    return m/n

def get_error(y,y_):
    tr = y[(y>0) & (y_>0)]
    pr = y_[(y>0) & (y_>0)]
    # print(np.abs(tr-pr) / tr)
    return np.mean(np.abs(tr-pr) / tr)

def get_feature(article_num): 

    db = pymysql.connect(host="121.196.99.106",port=3306,user="root",password="zzysky123",database="rawnewsdata",charset="utf8")
    cursor = db.cursor()
    sql = "select pageid,article_w,atitle_char_count,text_char_count,subtitle_area_count, picture_count,picture_area,article_area,page_article_count,text_char_count_ratio,ispicnews,ishead,ishead_zuoshang from headpages_style order by pageid;"
    data = pd.read_sql(sql, db).fillna(0)
    db.close()
    ##############################################
    # article_num = 6
    data = data[data['page_article_count'] == article_num]
    data_pageid_sum = data.groupby('pageid').sum()
    # print(data_pageid_sum)
    data = data[data['picture_count'] >= 1]
    #################
    data.loc[:,'allpic_num'] = 1
    for ridx in data_pageid_sum.index:
        data.loc[data['pageid']==ridx,'atitle_char_count'] = data[data['pageid']==ridx]['atitle_char_count'] / data_pageid_sum.loc[ridx,'atitle_char_count']
        data.loc[data['pageid']==ridx,'allpic_num'] = data_pageid_sum.loc[ridx,'picture_count']
    data.loc[:,'newstype'] = data.apply(newsTypewithPic, axis=1)
    ##############################################
    ##############################################
    # print(data)
    x = data.loc[:,['atitle_char_count', 'subtitle_area_count', 'text_char_count_ratio','newstype','picture_area','allpic_num','picture_count']]
    return x

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
        x = get_feature(article_num)
        y = pd.DataFrame(x,copy=True)
        tiers = [5,3,3,4,3,5,5]#atitle_char_count,subtitle_area_count,text_char_count_ratio,newstype,picture_area,allpic_num,picture_count
        state_names = {}
        for node,t in zip(x.columns,tiers):
            state_names[node] = list(range(t))
        boundaries = get_boundaries(x, tiers)
        boundaries[1] = [(-0.5,0.5),(0.5,1.5),(1.5,2.5)]
        boundaries[3] = [(-0.5,0.5),(0.5,1.5),(1.5,2.5),(2.5,3.5)]
        boundaries[5] = [(-0.5,0.5),(0.5,1.5),(1.5,2.5),(2.5,3.5),(4.5,4.5)]
        boundaries[6] = [(-0.5,0.5),(0.5,1.5),(1.5,2.5),(2.5,3.5),(4.5,4.5)]
        preds = [y.iloc[:,4][(boundaries[4][i][0] <= y['picture_area']) & (boundaries[4][i][1] > y['picture_area'])].mean() if not y.iloc[:,4][(boundaries[4][0][0] <= y['picture_area']) & (boundaries[4][0][1] > y['picture_area'])].empty else 0.1 for i in range(3)]
        preds = np.array(preds)
        data = re_label(x, boundaries, tiers)
        #fitdata#################################
        train_data = data
        model = BayesianNetwork([('atitle_char_count', 'picture_area'), 
                        ('text_char_count_ratio', 'picture_area'), 
                        ('subtitle_area_count', 'picture_area'), 
                        ('newstype', 'picture_area'),
                        ('allpic_num', 'picture_area'),
                        ('picture_count','picture_area')])
        model.fit(train_data, state_names=state_names)
        writer = BIFWriter(model)
        writer.write_bif(filename=f'./prefer_model/picture_size/prefer_picturesize_n={article_num}.bif')
        with open(f'./prefer_model/picture_size/preds_n={article_num}.txt', encoding='utf-8', mode='w') as f:
            for el in preds:
                f.write(str(el)+'\n')
        # # # #testdata#############################
        # test_data = data.iloc[-1:,:]
        # test_data = test_data.drop('picture_area', axis=1)
        # # #prefer#####################
        # model = BIFReader(f'./prefer_model/picture_size/prefer_picturesize_n={article_num}.bif').get_model(int)
        # pred_data = model.predict(test_data).loc[:,'picture_area'].to_list()
        # yy = preds[pred_data]
        # yy_ = y.iloc[-1:,4].to_numpy()
        # print(yy)
        # print(yy_)