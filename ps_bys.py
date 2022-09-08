from sklearn import naive_bayes
from sklearn.model_selection import train_test_split
import numpy as np
import matplotlib.pyplot as plt
import pymysql
import pandas as pd
import math
import joblib
from pgmpy.models import BayesianNetwork
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error,accuracy_score,precision_score
from pgmpy.estimators import MaximumLikelihoodEstimator, BayesianEstimator

'''
朴素贝叶斯分类：朴素的认为各个特征相互独立
P(C)*P(F1|C)*P(F2|C)...P(Fn|C)
'''
def preprocess_data(data):
    width=32.4
    height=50.76
    pt=0.035 #单位为cm

    for i in range(len(data)):
        data['article_y'].iloc[i]=math.floor(data['article_y'].iloc[i]*height)
        data['article_h'].iloc[i]=math.floor(data['article_h'].iloc[i]*height)
        data['article_x'].iloc[i]=math.floor(data['article_x'].iloc[i]*width)
        data['article_w'].iloc[i]=math.floor(data['article_w'].iloc[i]*width)
        data['text_char_count'].iloc[i]=math.floor(data['text_char_count'].iloc[i]*0.1)
        data['text_char_count_ratio'].iloc[i]=round(data['text_char_count_ratio'].iloc[i]*100)
    data['article_y']=data['article_y'].astype("int")
    data['article_h']=data['article_h'].astype("int")
    data['article_x']=data['article_x'].astype("int")
    data['article_w']=data['article_w'].astype("int")
    data['text_char_count_ratio']=data['text_char_count_ratio'].astype("int")
    return data

def read_hisframe():
    db = pymysql.connect(host="121.196.99.106",port=3306,user="root",password="zzysky123",database="rawnewsdata",charset="utf8")
    cursor = db.cursor()
    #图片新闻
    sql = "select article_id,pageid,article_h,article_x,article_y,article_w,atitle_char_count,picture_count,text_char_count,text_char_count_ratio,style_category from headpages_style \
        where picture_count>0 and ispicnews is not NULL and style_category!='NULL';"
    #无图文章
    sql1 = "select article_id,pageid,article_h,article_x,article_y,article_w,atitle_char_count,picture_count,text_char_count,text_char_count_ratio,style_category from headpages_style \
        where picture_count=0 and ispicnews is NULL and style_category!='NULL';"
    #有图文章
    sql2 = "select article_id,pageid,article_h,article_x,article_y,article_w,atitle_char_count,picture_count,text_char_count,text_char_count_ratio,style_category from headpages_style \
        where picture_count>0 and ispicnews is NULL and style_category!='NULL';"
    data_picnews = pd.read_sql(sql, db)
    data_nopicnews = pd.read_sql(sql1, db)
    data_havepicnews = pd.read_sql(sql2, db)

    data_picnews=preprocess_data(data_picnews)
    data_nopicnews=preprocess_data(data_nopicnews)
    data_havepicnews=preprocess_data(data_havepicnews)
    #print('476:',data.iloc[100,:])
    #print('特征：',data_picnews.columns)
    feature_picnews=data_picnews.dropna().iloc[:,np.arange(3,6)]
    label_picnews=data_picnews.dropna().iloc[:,-1]
    feature_nopicnews=data_nopicnews.dropna().iloc[:,np.arange(3,6)]
    label_nopicnews=data_nopicnews.dropna().iloc[:,-1]
    feature_havepicnews=data_havepicnews.dropna().iloc[:,np.arange(3,6)]
    label_havepicnews=data_havepicnews.dropna().iloc[:,-1]

    db.close()
    return feature_picnews,label_picnews,feature_nopicnews,label_nopicnews,feature_havepicnews,label_havepicnews


#为数据集分类
def newsclass(piccount,ispicnews):
    feature_picnews,label_picnews,feature_nopicnews,label_nopicnews,feature_havepicnews,label_havepicnews=read_hisframe()
    if piccount==0:
        X_train,y_train=feature_nopicnews,label_nopicnews
    elif piccount>0 and ispicnews==1:
        X_train,y_train=feature_picnews,label_picnews
    elif piccount>0 and ispicnews!=1:
        X_train,y_train=feature_havepicnews,label_havepicnews
    return X_train,y_train


#最近邻模型，这里k相当于1,且输入特征为一维（后续可试试多维结果）
def knn_model(inputdata,traindata):
    #print('输入',inputdata)
    matrixtemp = (traindata - inputdata)
    #print('matrixtemp:',matrixtemp)
    matrixtemp2 = np.square(matrixtemp)
    distance = np.sqrt(np.sum(matrixtemp2)) #求预测点到各个点的距离,axis=1
    #print('distance:',distance)
    #sortindex = np.argsort(distance)
    sortindex = np.argsort(matrixtemp)
    #print('sortindex:',sortindex)
    return traindata[sortindex[0]]

def knn_changedata(inputdata,traindata):
    if inputdata in traindata:
        return inputdata
    elif inputdata not in traindata:
        inputdata=knn_model(inputdata,traindata)
    return inputdata

def GaussianNB(X_train,y_train):
    
    cls=naive_bayes.GaussianNB()
    cls.fit(X_train,y_train)
    #print('类别：',np.unique(y_train))
    '''
    xtest1=[]
    for i in range(len(xtest)):
        article_x_temp=knn_changedata(xtest[i][0],X_train.iloc[:,0].values)
        article_y_temp=knn_changedata(xtest[i][1],X_train.iloc[:,1].values)
        article_w_temp=knn_changedata(xtest[i][2],X_train.iloc[:,2].values)
        atitle_char_count_temp=knn_changedata(xtest[i][3],X_train.iloc[:,3].values)
        text_char_count_temp=knn_changedata(xtest[i][5],X_train.iloc[:,5].values)
        text_char_count_ratio_temp=knn_changedata(xtest[i][6],X_train.iloc[:,6].values)
        xtest1.append([article_x_temp,article_y_temp,article_w_temp,atitle_char_count_temp,xtest[i][4],text_char_count_temp,text_char_count_ratio_temp])
        print("**xtest1***",xtest1)
    '''
    joblib.dump(cls, './layout_test/model1/havepicnews_nb.model')
    #nb = joblib.load('nopic_nb.model')
    '''
    label=cls.predict(xtest)
    print(cls.predict_proba(xtest)) #显示概率
    return label
    '''
    
def load_data():
    feature_picnews,label_picnews,feature_nopicnews,label_nopicnews,feature_havepicnews,label_havepicnews=read_hisframe()
    #print(feature_nopicnews)
    # return train_test_split(feature_havepicnews,label_havepicnews,test_size=0.35,random_state=0)
    return feature_havepicnews,label_havepicnews

def bysnetwork(xtrain,xtest,ytrain,ytest):
    model=BayesianNetwork([
    ('article_x','style_category'),
    ('article_y','style_category'),
    ('article_w','style_category'),
    #('atitle_char_count','style_category'),
    #('text_char_count','style_category'),
    #('picture_count','style_category'),

    ])  #贝叶斯网络关系
    
    #参数估计器：贝叶斯估计器、EM、最大似然估计
    columns=['article_x','article_y','article_w']
    xtrain=xtrain[columns]
    xtest=xtest[columns]
    xtrain['style_category']=ytrain
    print('xtrain:',xtrain)
    print('xtest',xtest)
    model.fit(xtrain,estimator=BayesianEstimator) 
    y_prob = model.predict(xtest)
    pre=precision_score(ytest,y_prob)
    print("模型精度为：",pre)
    


#用高斯分类器来查看效果
def test_GaussianNB(*data):
    X_train,X_test,y_train,y_test=data
    cls=naive_bayes.GaussianNB()
    cls.fit(X_train,y_train)
    print('类别：',np.unique(y_train))
    label=cls.predict(X_test)
    label1=cls.predict_proba(X_test) #得到每个类别的概率对数值
    print(X_test.iloc[0:30])
    for i in range(len(label)):
        if label[i]!=y_test.iloc[i]: #显示识别错误的类别
            #print('序列号：',y_test.index[i])
            print('序列号：',X_test.iloc[i])
            print('predict:',label[i])
            print('test_real:',y_test.iloc[i])
            print('pre_prob:',label1[i])
        else:
            print('pre_prob:',label1[i])
  
    print(cls.get_params())
    #print('pre_prob:',label1)
    print("training score:%.2f"%(cls.score(X_train,y_train)))
    print("testing score:%.2f"%(cls.score(X_test,y_test)))

'''
#测试多项式贝叶斯分类器
def test_MultinomialNB(*data):
    X_train,X_test,y_train,y_test=data
    cls=naive_bayes.MultinomialNB()
    cls.fit(X_train,y_train)
    print("training score:%.2f"%(cls.score(X_train,y_train)))
    print("testing score:%.2f"%(cls.score(X_test,y_test)))
#检验不同alpha值对于分类结果的影响
def test_MultinomialNB_alpha(*data):
    X_train,X_test,y_train,y_test=data
    alphas=np.logspace(-2,5,num=200)
    training_score=[]
    testing_score=[]
    for alpha in alphas:
        cls=naive_bayes.MultinomialNB(alpha=alpha)
        cls.fit(X_train,y_train)
        training_score.append(cls.score(X_train,y_train))
        testing_score.append(cls.score(X_test,y_test))

    #绘图
    fig=plt.figure()
    ax=fig.add_subplot(1,1,1)
    ax.plot(alphas,training_score,label="training score")
    ax.plot(alphas,testing_score,label="testing score")
    ax.set_xlabel('alpha')
    ax.set_ylabel('score')
    ax.set_title("MultinomoalNB")
    ax.set_xscale("log")
    plt.show()
 #查看伯努利分类器效果   
def test_BernoulliNB(*data):
    X_train,X_test,y_train,y_test=data
    cls=naive_bayes.BernoulliNB()
    cls.fit(X_train,y_train)
    print("training score:%.2f"%(cls.score(X_train,y_train)))
    print("testing score:%.2f"%(cls.score(X_test,y_test)))

## 查看不同alpha值的影响
def test_BernoulliNB_alpha(*data):
    X_train,X_test,y_train,y_test=data
    alphas=np.logspace(-2,5,num=200)
    training_score=[]
    testing_score=[]
    for alpha in alphas:
        cls=naive_bayes.BernoulliNB(alpha=alpha)
        cls.fit(X_train,y_train)
        training_score.append(cls.score(X_train,y_train))
        testing_score.append(cls.score(X_test,y_test))

    #绘图
    fig=plt.figure()
    ax=fig.add_subplot(1,1,1)
    ax.plot(alphas,training_score,label="training score")
    ax.plot(alphas,testing_score,label="testing score")
    ax.set_xlabel('alpha')
    ax.set_ylabel('score')
    ax.set_title("BerbuonlliNB")
    ax.set_xscale("log")
    plt.show()
 ##查看不同阙值的影响
def test_BernoulliNB_binarize(*data):
    X_train,X_test,y_train,y_test=data
    min_x=min(np.min(X_train.ravel()),np.min(X_test.ravel()))-0.1
    max_x=max(np.max(X_train.ravel()),np.max(X_test.ravel()))-0.1
    binarizes=np.linspace(min_x,max_x,endpoint=True,num=100)
    training_score=[]
    testing_score=[]
    for binarize in binarizes:
        cls=naive_bayes.BernoulliNB(binarize=binarize)
        cls.fit(X_train,y_train)
        training_score.append(cls.score(X_train,y_train))
        testing_score.append(cls.score(X_test,y_test))
    ##绘图
    fig=plt.figure()
    ax=fig.add_subplot(1,1,1)
    ax.plot(binarizes,training_score,label="training score")
    ax.plot(binarizes,testing_score,label="testing score")
    ax.set_xlabel('binarize')
    ax.set_ylabel('score')
    ax.set_title("BerbuonlliNB")
    plt.show()
'''
if __name__=="__main__":
    #show_digits()
     X_train,y_train=load_data()
     #bysnetwork(X_train,X_test,y_train,y_test)
     #print(X_train)
     #print(y_train)
     GaussianNB(X_train,y_train)
    #  test_GaussianNB(X_train,X_test,y_train,y_test)
     #test_BernoulliNB(X_train,X_test,y_train,y_test)
     #test_MultinomialNB(X_train,X_test,y_train,y_test)
     #test_MultinomialNB_alpha(X_train,X_test,y_train,y_test)
     #test_BernoulliNB_alpha(X_train,X_test,y_train,y_test)
     #test_BernoulliNB_binarize(X_train,X_test,y_train,y_test)
