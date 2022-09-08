import pymysql
import pandas as pd
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import MinMaxScaler
from joblib import dump, load
import time



def getShape(s):
    ret = ""
    for ch in s:
        if ch not in '0123456789':
            ret += ch
    return ret

def get_test_feature(articles_num):
    db = pymysql.connect(host="121.196.99.106",port=3306,user="root",password="zzysky123",database="rawnewsdata",charset="utf8")
    cursor = db.cursor()
    sql = f"select pageid,text_char_count,text_char_count_ratio,atitle_char_count,picture_count,subtitle_area_count,page_article_count,page_structure from headpages_style \
        WHERE page_article_count={articles_num} && page_structure is not null order by pageid;"
    data = pd.read_sql(sql, db)
    fea = np.array(data)[:,[1,3,4,5]]
    # print(np.max(fea, axis=0))
    # print(np.min(fea, axis=0))
    with open(f'./prefer_model/paper_structure/max_n={articles_num}.txt', encoding='utf-8', mode='w') as f:
            for el in np.max(fea, axis=0).flat:
                f.write(str(el)+'\n')
    with open(f'./prefer_model/paper_structure/min_n={articles_num}.txt', encoding='utf-8', mode='w') as f:
            for el in np.min(fea, axis=0):
                f.write(str(el)+'\n')
    scaler = MinMaxScaler()
    scaler.fit(fea)
    s_data = scaler.transform(fea)
    page_str = np.array(data)[:,7]
    area_cof = np.array([0.5,0.3,0.15,0.05])##text_char_count,atitle_char_count,picture_count,subtitle_area_count
    area_cof = np.array([0.55,0.28,0.12,0.05])
    area_data = np.dot(s_data, area_cof).reshape(-1,articles_num)
    X = np.sort(area_data)
    y = []
    for i in range(0,len(fea),articles_num):
        y.append(getShape(page_str[i]))
    ############################
    Y = np.array(y)
    return X,Y

def main():
    for article_count in range(6,3,-1):
        #traindata#################################
        X,y = get_test_feature(article_count)
        # #fitdata#################################
        k = min(15, X.shape[0]-1)
        knn = KNeighborsClassifier(n_neighbors=k, weights='distance')
        knn.fit(X, y)
        dump(knn, f'./prefer_model/paper_structure/prefer_Struc_n={article_count}.joblib')
        with open(f'./prefer_model/paper_structure/y_n={article_count}.txt', encoding='utf-8', mode='w') as f:
            for el in y.flat:
                f.write(el+'\n')
        # #testdata#############################
        # X_test = X[-1,:].reshape(1,-1)
        # print(X_test)
        #prefer#####################
        # knn = load(f'./prefer_model/paper_structure/prefer_Struc_n={article_count}.joblib')
        # a, b = knn.kneighbors(X_test, return_distance=True)
        # y_train = np.loadtxt(f'./prefer_model/paper_structure/y_n={article_count}.txt', dtype=str)
        # thepreds = y_train[tuple(b)]
        # print(thepreds)
        # break

if __name__ == '__main__':
    s = time.time()
    main()
    print(time.time()-s)