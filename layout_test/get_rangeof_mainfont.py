import pymysql
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split #随机划分训练集和验证集
import math
from sklearn.metrics import mean_squared_error
from sklearn import metrics
import matplotlib.pyplot as plt
from sklearn.neighbors import KernelDensity
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import LeaveOneOut
import csv
import codecs
'''
测试：已知特征 为新闻块（x,y,w）,按篇对历史数据进行kmeans聚类。比对类别标签与聚类标签的相似性。
'''
def writetocsv(fpath,data):
    f=codecs.open(fpath,'w','utf8')
    writer = csv.writer(f)
    for i in data:
            writer.writerow(i)
    f.close()


def preprocess_data(data):  
    width=32.4  
    height=50.76  
    pt=0.035 #单位为cm

    for i in range(len(data)):
        data['article_y'].iloc[i]=math.floor(data['article_y'].iloc[i]*height)
        data['article_h'].iloc[i]=math.floor(data['article_h'].iloc[i]*height)
        data['article_x'].iloc[i]=math.floor(data['article_x'].iloc[i]*width)
        data['article_w'].iloc[i]=math.floor(data['article_w'].iloc[i]*width)
        if data['title_style'].iloc[i]==0:#横标题
            data['maintitle_charsize'].iloc[i]=math.floor((data['maintitle_charsize'].iloc[i]*height)/pt) #单位转化为pt
        elif data['title_style'].iloc[i]==1: #竖标题
            data['maintitle_charsize'].iloc[i]=math.floor((data['maintitle_charsize'].iloc[i]*width)/pt)
        #data['text_char_count'].iloc[i]=math.floor(data['text_char_count'].iloc[i]*0.1)
        data['text_char_count_ratio'].iloc[i]=round(data['text_char_count_ratio'].iloc[i]*100) #将比例保留两位小数乘以100
    data=data[data['maintitle_charsize']<80]  #清洗数据（删除不合理的字号）
    data['article_y']=data['article_y'].astype("int") #转换类型为int
    data['article_h']=data['article_h'].astype("int")
    data['article_x']=data['article_x'].astype("int")
    data['article_w']=data['article_w'].astype("int")
    data['maintitle_charsize']=data['maintitle_charsize'].astype("int")
    data['text_char_count_ratio']=data['text_char_count_ratio'].astype("int")
    return data

#已知特征包括新闻块(x,y,w,h),主标题字数、副标题行数、正文字数、正文字数所占全文比例
def read_hisframe():
    db = pymysql.connect(host="121.196.99.106",port=3306,user="root",password="zzysky123",database="rawnewsdata",charset="utf8")
    cursor = db.cursor()
    #图片新闻
    sql = "select article_id,pageid,title_style,maintitle_charsize,article_h,article_x,article_y,article_w,atitle_char_count,subtitle_area_count,text_char_count,text_char_count_ratio,style_category from headpages_style \
        where picture_count>0 and ispicnews is not NULL and style_category!='NULL';"
    #无图文章
    sql1 = "select article_id,pageid,title_style,maintitle_charsize,article_h,article_x,article_y,article_w,atitle_char_count,subtitle_area_count,text_char_count,text_char_count_ratio,style_category from headpages_style \
        where picture_count=0 and ispicnews is NULL and style_category!='NULL';"
    #有图文章
    sql2 = "select article_id,pageid,title_style,maintitle_charsize,pic1_size,article_h,article_x,article_y,article_w,atitle_char_count,subtitle_area_count,text_char_count,text_char_count_ratio,picture_count,style_category from headpages_style \
        where picture_count>0 and ispicnews is NULL and style_category!='NULL';"
    data_picnews = pd.read_sql(sql, db)
    data_nopicnews = pd.read_sql(sql1, db)
    data_havepicnews = pd.read_sql(sql2, db)

    data_picnews=preprocess_data(data_picnews)
    data_nopicnews=preprocess_data(data_nopicnews)
    data_havepicnews=preprocess_data(data_havepicnews)
    #print('476:',data.iloc[100,:])
    #print('特征：',data_picnews.columns)
    feature_picnews=data_picnews.dropna().iloc[:,np.arange(4,12)]
    label_picnews=data_picnews.dropna().iloc[:,[0,1,3,-1]]
    feature_nopicnews=data_nopicnews.dropna().iloc[:,np.arange(4,12)]
    label_nopicnews=data_nopicnews.dropna().iloc[:,[0,1,3,-1]]
    feature_havepicnews=data_havepicnews.dropna().iloc[:,np.arange(5,14)]          
    label_havepicnews=data_havepicnews.dropna().iloc[:,[0,1,3,4,-1]]

    cursor.close()
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

#分割训练集和测试集   
def load_data():
    feature_picnews,label_picnews,feature_nopicnews,label_nopicnews,feature_havepicnews,label_havepicnews=read_hisframe()
    #print(feature_nopicnews)
    #return train_test_split(feature_nopicnews,label_nopicnews,test_size=0.1,random_state=0)
    return feature_nopicnews,label_nopicnews

#特征为新闻块（x,y,w)  
def kmeans_model(train_feat,train_label,k):
    samples=train_feat
    
    scaler=StandardScaler()#标准化
    samples = scaler.fit_transform(samples)
    
    #k=10#聚类类别初始值
    #k=12  #################################k的取值待测试
    kmeans=KMeans(n_clusters=k,random_state=100,init='k-means++') #初始聚类中心采用kmeans++算法
    kmeans.fit(samples)
    #print("距离：",kmeans.inertia_)
    #print('训练数据集个数：',len(train_feat))
    #sse.append(sum(np.min(cdist(samples,kmean.cluster_centers_,'euclidean'),axis=1)))
    print("聚类中心：",kmeans.cluster_centers_)#这里显示的为标准化后的数据
    jl_center=np.rint(scaler.inverse_transform(kmeans.cluster_centers_)) #逆标准化并进行四舍五入取整
    print('标准化复原的聚类中心：',jl_center)
    #writetocsv('./layout_test/km_center.csv',kmeans.cluster_centers_) #将聚类中心存储到csv文件中
    labels1=kmeans.predict(samples)
    #print(labels1)

    a_label=[[] for i in range(k)]  
    a_feature=[[] for i in range(k)]
    for i in range(len(labels1)):
        a_label[labels1[i]].append(train_label.iloc[i]) #数据的未知特征
        a_feature[labels1[i]].append(train_feat.iloc[i]) #数据的已知特征
    #print(a_feature[5])
    #print('训练：',a_label[5])
    print('轮廓系数：',metrics.silhouette_score(samples,labels1)) #轮廓系数，越接近1越好
    return a_feature,a_label


#############kde核密度估计#######################
def get_bindwidth(x_feature):#运用网格搜索法获得最优带宽
    bandwidths=10**np.linspace(-1,1,50)
    grid=GridSearchCV(KernelDensity(kernel='gaussian'),{'bandwidth':bandwidths},cv=LeaveOneOut())
    grid.fit(x_feature[:,None])
    return grid.best_params_['bandwidth']


#一维核密度估计,核函数为高斯核函数
def kde_desity(x_feature): #x_feature为未知特征
    pd1=pd.DataFrame(x_feature)
    #print(pd1)
    pd1['maintitle_charsize']=pd1['maintitle_charsize'].astype("int")
    X1=pd1['maintitle_charsize'].values

    bandwidths=get_bindwidth(X1)
    kde = KernelDensity(kernel='gaussian', bandwidth=bandwidths) #之后每个类的带宽都需要更改
    kde.fit(X1[:,None])
    X2=np.linspace(min(X1),max(X1),100)[:, None]
    #注意score与score_samples的区别，score是计算在该模型下总的概率密度的对数值，score_samples返回概率密度的对数值
    log_prob=kde.score_samples(X2)
    #print(log_prob)
    #print(np.exp(log_prob))
    #取概率为前k个的未知特征
    label_sort=np.argsort(-log_prob) #从大到小排序
    #print(label_sort)
    maxprob=max(log_prob)
    medianprob=np.median(log_prob)
    select_index=label_sort[0:round(0.5*len(label_sort))] #取概率为前1/2的字号
    fontsize_set=[]
    for i in range(len(select_index)):
        temp=np.around(X2[select_index].reshape(1,-1)[0][i])
        if temp not in fontsize_set:
            fontsize_set.append(temp) #不重复的取整后的字号集合
    #print(fontsize_set)
    '''
    plt.figure()
    plt.plot(X2,np.exp(log_prob))
    plt.hist(X1,density=true,bins=30)
    plt.show()
    '''
    return fontsize_set
    



def main():
    conn = pymysql.connect(host="121.196.99.106",port=3306,user="root",password="zzysky123",database="rawnewsdata",charset="utf8")
    xtrain,ytrain=newsclass(0,0)
    mean=np.mean(xtrain,axis=0)
    std=np.std(xtrain,axis=0)

    print(mean)
    print(std)
    #a_feature,a_label=kmeans_model(xtrain,ytrain,13)
    
    #print(a_feature[0])
    #print(a_label[0])
    '''
    sfont=[]
    for i in range(13):
        fontset=kde_desity(a_label[i])
        sfont.append(fontset)
    writetocsv('./layout_test/font_set.csv',sfont)
    '''


        

if __name__=='__main__':
    main()
