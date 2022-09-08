from numpy.core.fromnumeric import argmax, around
import pymysql
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
from sklearn.model_selection import train_test_split

'''
统计栏宽的范围，利用正态分布模型选择合适的栏数
ps:后面可以加上对于一个版面新闻块宽度相同的分栏文章的栏数相同  
或者后面微调时再通过空白区域改变                                                                                                          
'''
#坐标字符串转为数组
def coord_strtolist(str):
    if str=='[]':
        return np.array([])
    else:
        new_str=str.replace('[','').replace(']','').split(',')
        #print(len(new_str))
        list_num=int(len(new_str)/4)
        new_list=[]
        for i in range(list_num):
            temp=new_str[i*4:i*4+4]
            temp=[float(x) for x in temp]
            new_list.append(temp)
        return new_list

def read_textcoord():
    db = pymysql.connect(host="121.196.99.106",port=3306,user="root",password="zzysky123",database="rawnewsdata",charset="utf8")
    cursor = db.cursor()
    sql = "select article_id,article_x,article_w,pageid,iscolumn,text_area_coord from headpages_style \
        where ispicnews is NULL and style_category!='NULL' and iscolumn=1;"
    data = pd.read_sql(sql, db)
    db.close()
    return data

def read_column_width(text_area_coord,text_font_size):  #根据坐标求栏宽以及一栏字数
    text_area_coord=coord_strtolist(text_area_coord)
    text_width=[text_area_coord[i][2] for i in range(len(text_area_coord))]
    #print(text_width)
    column_width=sorted(text_width)[len(text_width)//2] #一篇分栏文章中的栏宽（取中位数）
    #一栏的字数
    pt=0.35
    width=324 #纸张宽度，单位为毫米
    height=507.6
    column_text_count=(column_width*width)//(text_font_size*pt) #这里字号为9pt
    return column_width,column_text_count

#针对分栏文章类型
def get_column_num(bw,fontsize,colsep):
    data=read_textcoord()
    #print(data)
    sum_column_width=[] #一栏的宽度集合
    sum_column_text_count=[] #一栏的字数集合
    #plt.figure(1)
    for i in range(len(data)):
        column_width,column_text_count=read_column_width(data.iloc[i,5],fontsize)
        sum_column_width.append(round(column_width))
        sum_column_text_count.append(column_text_count)
        #plt.scatter(column_text_count,data.iloc[i,2])
    #plt.show()
    #print('栏宽集合',sum_column_width)
    #print(sum_column_text_count)
    df_column_text_count=pd.DataFrame(sum_column_text_count)
    df_column_text_width=pd.DataFrame(sum_column_width)
    '''
    df_column=pd.DataFrame(sum_column_width)
    df_column_text_count=pd.DataFrame(sum_column_text_count)
    #可以加一个异常值检测并删除
    print(df_column.describe())
    print(df_column_text_count.describe())
    '''

    mode_text_count=df_column_text_count.mode().values[0][0] #一栏字数的众数
    #print(mode_text_count)
    max_text_count=np.max(sum_column_text_count) #最大值
    min_text_count=np.min(sum_column_text_count) #最小值
    #print(max_text_count)
    #print(min_text_count)
    

    #判断栏数范围
    pt=0.35
    mode_ocw=mode_text_count*fontsize*pt #以字数的众数计算栏宽
    #print(mode_ocw)
    mode_col_num=round((bw+colsep)/(mode_ocw+colsep))#栏数  ##################
    #print(mode_col_num)

    max_ocw=max_text_count*fontsize*pt #以字数的最大数计算栏宽
    #print(max_ocw)
    max_col_num=math.floor((bw+colsep)/(max_ocw+colsep))  #一栏最大字数对应的栏数
    if max_col_num==0:
        return 1
    realmax_col_text_count=round(((bw-(max_col_num-1)*colsep)/max_col_num)/(fontsize*pt)) #真实栏宽所占字数

    min_ocw=min_text_count*fontsize*pt #以字数的最小数计算栏宽
    min_col_num=math.floor((bw+colsep)/(min_ocw+colsep))  #一栏最小字数对应的栏数
    #print(min_col_num)

    colnum_range=np.arange(max_col_num,min_col_num+1)  #栏数范围
    #print(colnum_range)

    if realmax_col_text_count>max_ocw and len(colnum_range)!=1: #该情况为在最大栏数下的字数已经超出了最大字数
        del colnum_range[-1]
    
    for i in range(len(colnum_range)):
        if colnum_range[i]==mode_col_num:
            real_col_num=mode_col_num
            #print(mode_col_num)
            break
        real_col_num=colnum_range[i]
    
    return real_col_num

#正态分布概率模型 
def normfun(bw,fontsize,colsep):
    data=read_textcoord()
    sum_column_width=[] #一栏的宽度集合
    sum_column_text_count=[] #一栏的字数集合
    #plt.figure(1)
    for i in range(len(data)):
        column_width,column_text_count=read_column_width(data.iloc[i,5],fontsize)
        '''
        if column_text_count!=16:
            col=round((bw+colsep)/(column_text_count*fontsize*0.35+colsep))
            print('colnum:',col)
            print('article_w:',data.iloc[i,2]*324)
            print('column_text_count:',column_text_count)
            print('################')
            '''
        sum_column_width.append(column_width)
        sum_column_text_count.append(column_text_count)
        #plt.scatter(column_text_count,data.iloc[i,2])
    #plt.show()
    #print('栏宽集合',sum_column_width)
    #print(sum_column_text_count)
    df_column_text_count=pd.DataFrame(sum_column_text_count) #一栏的字数
    df_column_text_width=pd.DataFrame(sum_column_width) #一栏的宽度
    #print(df_column_text_count)
    #print(df_column_text_width)
    mu=round(df_column_text_count.mean().values[0]) #平均值
    sigma=df_column_text_count.std().values[0] #标准差
    #print(mu)
    #print(sigma)

    
    plt.figure(1)
    df_column_text_count.hist(bins=30,alpha = 0.5)
    df_column_text_count.plot(kind = 'kde', secondary_y=True)
    pdf = np.exp(-((df_column_text_count.values - mu)**2)/(2*sigma**2)) / (sigma * np.sqrt(2*np.pi))
    plt.scatter(df_column_text_count.values, pdf) 
    plt.show()
    

    pdf_list=[]
    pt=0.35
    for i in range(1,7):#
        occ_test=(bw-(colsep*(i-1)))//(i*fontsize*pt)#一栏字数 
        #print('occ:',occ_test)
        ocw_test=occ_test*fontsize*pt #一栏宽度（按照字数）
        #print('col_num:',i)
        pdf = np.exp(-((occ_test - mu)**2)/(2*sigma**2)) / (sigma * np.sqrt(2*np.pi))
        #print('pdf:',pdf)
        #print('************************')
        pdf_list.append(pdf)
    maxpdf=max(pdf_list)
    index=argmax(pdf_list) #也可以选择概率大于10^(-3)的前两个列数为候选（后面再修改）
    realcolnum=index+1
    print(realcolnum)
    return realcolnum



def main():
    data=get_column_num(224,9,5)
    print(data)
    normfun(224,9,5)                                                                                                                                                                                                                                                


if __name__=="__main__":
    main()