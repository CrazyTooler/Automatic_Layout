import joblib
import os
import csv
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import math

import layout_test.learn_column_width
import layout_test.param_cal
import layout_test.cal_area as lca
import csv
import layout_test.get_rangeof_mainfont
import layout_test.get_learnparams as lg


current_path = os.path.abspath(__file__)#绝对路径
father_path = os.path.abspath(os.path.dirname(current_path) + os.path.sep + ".")

subfontsize=21 #副标题字号,单位为pt
mfs=9 #正文字号,单位为pt
mlh=10 #正文行距,单位为pt
colsep=5 #栏间距,单位为pt
vspace=[3,3,5] #标题间距,单位为pt

def readcsv(filename):
    res=[]
    f = csv.reader(open(filename,'r'))
    for i in f:
        temp=[float(j) for j in i]
        res.append(temp)
    return res

def read_mean_std(xtest):
    #为了使训练数据和预测数据的标准化规则相同
    mean=np.array([14.129117,8.480896,21.147563,15.935441,17.994730,0.653491,934.138340,20.973650])
    std=np.array([7.393989,10.757078,13.665372,7.349351,5.974912,0.600689,358.162627,7.892682])
    samples=(np.array(xtest)-mean)/std
    return samples

#通过计算与聚类中心的距离进行
def get_fontset(piccount,ispicnews,xtest):
    '''
    init_data1,init_data2=layout_test.get_rangeof_mainfont.newsclass(piccount,ispicnews) #可以直接算标准化的参数加快运行速度
    scaler=StandardScaler().fit(init_data1)#生成标准化规则(即实时数据标准化规则与训练数据标准化规则相同)
    samples = scaler.transform([xtest])#标准化
    '''
    samples=read_mean_std(xtest)
    #print(samples)
    res=pd.read_csv('./layout_test/km_center.csv',names=['h','x','y','w','ac','sc','tc','tcr'])
    #print(res)
    xz=res-samples
    xz1=xz.mul(xz)
    dist=[]
    for i in range(len(xz1)):
        dist.append(xz1.iloc[i].sum())  #计算数据到各聚类中心的欧氏距离
    label=np.argmin(dist)
    res=readcsv('./layout_test/font_set.csv')
    return res[label]

#############根据新闻块宽度以及候选字号判断换行情况以及压缩系数#####################

#若字号偏大则在一定范围内找到满足条件的字号
def change_param_in_range(fontsize,bw,title_charnum,scale_thresh):
    #在一定范围内改变字号
    pt=0.35
    max_range=20
    for i in range(max_range): #
        fontsize=fontsize-1
        font_scale_width=fontsize*scale_thresh*pt #一个字的宽度
        ol_maxcount=math.floor(bw/font_scale_width) #一行的最大字数
        sum_linenum=math.ceil(title_charnum/ol_maxcount)  #在已知一行最大字数下的最小行数
        if sum_linenum==2:
            final_fontsize=fontsize
            ol_count=math.ceil(title_charnum/2) #一行字数，这里设定换行位置在中间
            scale_coe=(bw/ol_count)/(fontsize*pt)
            if scale_coe>1:
                scale_coe=1
            break
    return final_fontsize,scale_coe

#换行条件：判断该横标题在最小缩放系数下是否超过区块宽度，若超过则换行，若两行也超过则微调字号
def get_hfontsize_and_hscalecoe(fontsize,bw,title_charnum,scale_thresh):
    Max_line_num=2 #限定最大行数为2
    is_changeline=-1
    pt=0.35 #单位mm
    fontsize=float(fontsize)
    font_scale_width=fontsize*scale_thresh*pt #一个字的宽度
    ol_maxcount=math.floor(bw/font_scale_width) #一行的最大字数
    sum_font_width=font_scale_width*title_charnum #总的标题宽度
    sum_linenum=math.ceil(title_charnum/ol_maxcount)  #在已知一行最大字数下的最小行数
    if sum_linenum>Max_line_num:
        #改变字号直到变为2行
        final_fontsize,scale_coe=change_param_in_range(fontsize,bw,title_charnum,0.6)
        is_changeline=1
    elif sum_linenum==2:
        #需换行,缩放比例待确定(缩放比例可能会随着换行位置改变)
        final_fontsize=fontsize
        ol_count=math.ceil(title_charnum/2) #一行字数，这里设定换行位置在中间
        scale_coe=(bw/ol_count)/(fontsize*pt)
        is_changeline=1
        if scale_coe>1:
            scale_coe=1
    elif sum_linenum==1:
        #无需换行，但缩放比例待确定
        is_changeline=0
        final_fontsize=fontsize
        scale_coe=(bw/title_charnum)/(fontsize*pt) #这里fontsize单位为cm或mm
        if scale_coe>1:
            scale_coe=1
    return final_fontsize,scale_coe,is_changeline


#由于竖标题字号的判断写在面积判断里，这里不赘述，后面可以移过来
#判断该竖标题的字号与缩放系数（需要标题高度和文章高度）
#换行条件：判断该竖标题在最小缩放系数下是否超过正文的高度，若超过则换行，若两行也超过则微调字号(一般不会)
def get_vfontsize_and_vscalecoe(fontsize,bw,title_charnum,count_subtitle,para_char,scale_thresh):
    #根据标题高度判断是否换行
    pt=0.35
    #计算竖标题的宽度(假设不换行的情况下)
    vth=(title_charnum*fontsize+26)*pt #该字号下的标题高度
    if count_subtitle==0:
        tw=(fontsize+8)*pt
    else:
        tw=(fontsize+subfontsize*count_subtitle+8*count_subtitle+8)*pt
    #####计算正文高度#########
    ohc=round((bw-tw)/(mfs*pt)) #一行的字数(采用四舍五入)
    hc=[] #计算每段所占行数
    for i in para_char:
        t=math.ceil(i/ohc)
        hc.append(t)
    sumhc=np.sum(np.array(hc))#计算总行数
    mh=sumhc*mlh*1.3*pt#文本高度
    vth1=(vth-9.1)*scale_thresh+10.1 #压缩后的标题高度，单位mm(计算公式实验得来的，么依据,后面改，埋坑ing)
    if vth1>=mh: #换行情况
        #tw=(fontsize+8)*2*pt
        tw=tw+(fontsize+8)*pt
        ischangeline=1
        scalecoe=1
        #加入换行后的压缩系数的计算,暂时设置为1
    else:  #求压缩系数
        ischangeline=0
        maxscalecoe=(mh)/vth  #标题最大压缩系数
        if maxscalecoe>1:
            scalecoe=1
        else:
            scalecoe=maxscalecoe
    return tw,fontsize,scalecoe,ischangeline  #字号，压缩系数，是否换行

#朴素贝叶斯模型
def nb_model(countpic,ispicnews,xtest):
    #获取朴素贝叶斯分类模型(这样可以加快运行速度)
    if countpic==0:
        nb = joblib.load(father_path+'\\model1\\nopicnews_nb.model')
    elif countpic>0 and ispicnews==0:
        nb = joblib.load(father_path+'\\model1\\havepicnews_nb.model')
    elif countpic>0 and ispicnews==1:
        nb = joblib.load(father_path+'\\model1\\picnews_nb.model')
    label=nb.predict(xtest) #返回样式结构的种类
    label_prob=nb.predict_proba(xtest)
    return label[0] #暂时只返回一个样式种类

#根据求出的样式参数改变样式texcode
def cal_style_param(bw,colnum,texcode,maintitle_fontsize,title_charnum,title_style,count_subtitle,para_char):
    flag=0
    tw=0
    scale_coe=1
    #栏数
    if colnum>1: #说明该样式为分栏样式
        new_col_num=layout_test.learn_column_width.get_column_num(bw,9,5) #正文字号、栏间距
        if new_col_num==1: #该宽度不适合分栏
            #new_style=''  #使样式为空，也可以加一个兜底的样式
            new_style=texcode.replace('\end{multicols}','').replace('\\begin{multicols}{2}','').replace('\\vspace{-\\baselineskip}','').replace('\\vspace{-1em}','')
        else:
            new_style=layout_test.param_cal.change_column_num(texcode,str(new_col_num))  #获得加入优化栏数的样式code
            # print(new_style)
    else:
        new_col_num=1
        new_style=texcode
    #标题字号以及压缩系数的改变
    if title_style==0: #横标题字号与压缩系数的获取
        final_fontsize,scale_coe,is_changeline=get_hfontsize_and_hscalecoe(maintitle_fontsize,bw,title_charnum,0.6)
        #print(final_fontsize,scale_coe,is_changeline)
        final_fontsize=round(int(final_fontsize))
        new_style=layout_test.param_cal.change_htitle_size(new_style,str(final_fontsize))
        new_style=layout_test.param_cal.change_scale_coe(new_style,str(scale_coe),title_style)
        if is_changeline==1:
            flag=1
    elif title_style==1: #竖标题字号与压缩系数的获取
        tw,final_fontsize,scale_coe,is_changeline=get_vfontsize_and_vscalecoe(maintitle_fontsize,bw,title_charnum,count_subtitle,para_char,0.6)
        new_style=layout_test.param_cal.change_vtitle_size(new_style,str(maintitle_fontsize))
        if is_changeline==1:
            flag=1
        #print(new_style)
        # 竖标题样式的改变写在了面积计算的函数里
        #new_style=param_cal.change_scale_coe(new_style,str(scale_coe),title_style)
    return tw,scale_coe,new_col_num,new_style,flag

###根据样式种类、新闻素材信息计算新闻块面积
def calcu_s(style_cat,style,bw,bh,count_subtitle,sub_title,para_char,count_title_char,pic_count,pic,ischangeline,title,vspace,mt_fontsize,subt_fontsize,mtfs,mtlh,colnum,colsep,tw,scalecoe):
    S=0
    if style_cat=='ht_np_nc':
        S=lca.ht_np_nc(bw,count_subtitle,sub_title,para_char,ischangeline,vspace,mt_fontsize,subt_fontsize,mtfs,mtlh)
    if style_cat=='ht_np_c':
        S=lca.ht_np_c(bw,count_subtitle,sub_title,para_char,ischangeline,vspace,mt_fontsize,subt_fontsize,colnum,colsep,mtfs,mtlh)
    if style_cat=='vwt_np_nc':
        S=lca.vwt_np_nc(bw,count_title_char,para_char,ischangeline,tw,scalecoe,mt_fontsize,mtfs,mtlh)
    if style_cat=='picnews_vertical':
        S=lca.picnews_vertical_nc(style,bw,bh,pic_count)
    if style_cat=='picnews_horizontal':
        S=lca.picnews_ht_horizontal_nc(style,bw,bh,pic_count,pic,para_char,title,mtfs,mtlh)
    if style_cat=='ht_tp_nc' or style_cat=='ht_bp_nc':
        S=lca.ht_tbp_nc(bw,count_subtitle,sub_title,para_char,pic_count,pic,ischangeline,vspace,mt_fontsize,subt_fontsize,mtfs,mtlh)
    if style_cat=='ht_tp_c' or style_cat=='ht_bp_c':
        S=lca.ht_tbp_c(bw,count_subtitle,sub_title,para_char,pic_count,pic,ischangeline,vspace,mt_fontsize,subt_fontsize,colnum,colsep,mtfs,mtlh)
    if style_cat=='ht_ltcp_c' or style_cat=='ht_rbcp_c':
        S=lca.ht_tbcp_c(bw,count_subtitle,sub_title,para_char,pic_count,pic,ischangeline,vspace,mt_fontsize,subt_fontsize,colnum,colsep,mtfs,mtlh)
    return S

#前两篇按照从左到右，从上到下的规则，后面的根据推断模型进行预测,还要看宽度(两栏宽度为分界)
def get_weights(article_num,x_list,y_list,width_list,label,ispicnews):
    print(y_list)
    max_y=max(y_list)
    weights=np.ones(article_num)*(-1)
    x_sort=np.sort(list(set(x_list))) #从小到大排列
    y_sort=np.sort(list(set(y_list))) #只固定y值最高的新闻块
    print(x_sort)
    print(y_sort)
    #以下判断只适用于版面二分割的情况
    for i in range(article_num):
        if ispicnews[i]==0:
            #头条的选择
            if y_list[i]==max_y and x_list[i]==0 and width_list[i]>35:
                weights[0]=int(i+1)
            elif y_list[i]==max_y and x_list[i]==0 and width_list[i]<=35 and label[i]=="vwt_np_nc": #如果x只有一种值
                weights[0]=int(i+1)
            #二头条的选择
            if len(x_sort)>1:
                if weights[0]==-1: #即在(0,0)处没有符合头条的新闻块
                    if y_list[i]==max_y and x_list[i]!=0 and width_list[i]>35:
                        weights[0]=int(i+1)
                    elif y_list[i]==max_y and x_list[i]!=0 and width_list[i]<=35 and label[i]=="vwt_np_nc":
                        weights[0]=int(i+1)
                else:
                    if y_list[i]==max_y and x_list[i]!=0 and width_list[i]>35:
                        weights[1]=int(i+1)
                    elif y_list[i]==max_y and x_list[i]!=0 and width_list[i]<=35 and label[i]=="vwt_np_nc":
                        weights[1]=int(i+1)
    return weights

def get_ft_combination(article_num,frame,width,height,count_title_char,para_char,text_count_sum,count_sub_title,ispicnews,label):
    ft_list=[]
    ft_ave_dict={}
    real_weights=[]
    ft_ave_list=[]
    x_list=[math.floor(frame[i][0]) for i in range(article_num)]
    y_list=[math.floor(frame[i][1])+math.floor(frame[i][3]) for i in range(article_num)]
    width_list=[math.floor(frame[i][2]) for i in range(article_num)]
    weights=get_weights(article_num,x_list,y_list,width_list,label,ispicnews) #初始化权重 
    print("初始固定权重：",weights)
    picnewsfont=21 #图片新闻字号
    index=[]#记录图片新闻的下标
    for i  in range(article_num):
        if ispicnews[i]==1:
            #ft_list.append(np.array([21])) #图片新闻的字号是固定的
            index.append(i)  #记录图片新闻的下标
            continue
        xtest=[math.floor(frame[i][3]*0.01*height),math.floor(frame[i][0]*0.01*width),math.floor(height-(frame[i][1]*0.01*height+frame[i][3]*0.01*height)),math.floor(frame[i][2]*0.01*width),count_title_char[i],count_sub_title[i],math.floor(np.sum(para_char[i])),round((np.sum(para_char[i])/text_count_sum)*100)]
        #print(xtest)
        temp=get_fontset(0,0,xtest) #这里用到的数据只有无图的文章
        real_weights.append(i+1)
        ft_ave=sum(temp)/len(temp)  #字号候选集合的平均数
        #ft_ave=temp[0] #字号根据概率大小排列，排序概率最大的字号获得权重
        #ft_ave=min(temp)
        ft_ave_list.append(ft_ave)
        ft_list.append(temp)
    #print(ft_list)
    #根据字号平均值给新闻块排序
    for i in range(len(real_weights)):
        if real_weights[i] not in weights:
            ft_ave_dict[real_weights[i]]=ft_ave_list[i]
    ft_ave_dict=sorted(ft_ave_dict.items(),key=lambda item:item[1],reverse=True)
    #print(ft_ave_dict)
    
    for i in range(len(ft_ave_dict)):
        weights[i+(len(real_weights)-len(ft_ave_dict))]=int(ft_ave_dict[i][0])
    
    for i in range(len(index)):
        weights[article_num-len(index)+i]=int(index[i]+1)
    #ft_ave_arg=np.argsort(ft_ave_list)[::-1] #从大到小排序的下标号
    #print("字号集合平均值系数排列",ft_ave_arg)
    weights=[int(weights[i]) for i in range(len(weights))]
    print("权重",weights)
    ft_combination=lg.select_legalcombination(ft_list,weights,index,picnewsfont) #输出的为一个二维数组，每一个数组对应新闻的组合字号
    return weights,ft_combination

def get_ft_combination_test(article_num,xtest,ispicnews,label):
    ft_list=[]
    ft_ave_list=[]
    weights=[] 
    picnewsfont=21
    index=[]#记录图片新闻的下标
    for i  in range(article_num):
        if ispicnews[i]==1:
            #ft_list.append(np.array([21])) #图片新闻的字号是固定的
            index.append(i)  #记录图片新闻的下标
            continue
        #print(xtest)
        temp=get_fontset(0,0,xtest[i]) #这里用到的数据只有无图的文章
        #ft_ave=sum(temp)/len(temp)  #字号候选集合的平均数
        ft_ave=temp[0] #字号根据概率大小排列，排序概率最大的字号获得权重
        #ft_ave=min(temp)
        ft_ave_list.append(ft_ave)
        weights.append(i+1)
        ft_list.append(temp)
    #print(ft_list)
    #根据字号平均值给新闻块排序
    ft_ave_arg=np.argsort(ft_ave_list)[::-1] #从大到小排序的下标号
    print("字号集合平均值系数排列",ft_ave_arg)
    weights=[weights[j] for j in ft_ave_arg]
    for i in index:
        weights.append(i+1) 
    ft_combination=lg.select_legalcombination(ft_list,weights,index,picnewsfont) #输出的为一个二维数组，每一个数组对应新闻的组合字号
    return weights,ft_combination

def search_dict(dict,id,mt_font): #查找字典中是否有相同字号
    flag=0
    S=-1
    '''
    for i in range(len(dict)):
        if dict[i]['id']==id and dict[i]['mt']==mt_font:
            flag=1
            S=dict[i]['S']
            break
        '''
    if str(id)+'-'+str(mt_font) in dict:
        flag=1
        S= dict[str(id)+'-'+str(mt_font)]
    return flag,S

def get_s_combination(label,data,style,init_colnum,bw,bh,count_subtitle,sub_title,para_char,count_title_char,pic_count,pic,title,mt_fontsize,dict):
    S_list=[]
    for i in range(len(label)):
        if data[i][4]=="horizontal":
            title_style=0
        elif data[i][4]=="vertical":
            title_style=1
        #if temp2!='': #若分栏文章栏目为1，则新闻块不适合分栏
        flag1,S=search_dict(dict,i,mt_fontsize[i])
        if flag1==1:
            S_list.append(S)
            continue
        elif flag1==0:
            tw,scale_coe,temp1,temp2,flag=cal_style_param(bw[i],init_colnum[i],style[i],mt_fontsize[i],count_title_char[i],title_style,count_subtitle[i],para_char[i])  
            if temp1==1:
                colsep1=0
            else:
                colsep1=colsep
            S=calcu_s(label[i],style[i],bw[i],bh[i],count_subtitle[i],sub_title[i],para_char[i],count_title_char[i],pic_count[i],pic[i],flag,title[i],vspace,mt_fontsize[i],subfontsize,mfs,mlh,temp1,colsep1,tw,scale_coe)
            #temp={'id':i,'mt':mt_fontsize[i],'S':S}
            #dict.append(temp)
            dict[str(i)+'-'+str(mt_fontsize[i])]=S
            #print(S)
            S_list.append(S)
    #print(dict)
    return S_list 


def main():
    #xtest=[10,0,28,9,12,0,620,10]
    #label=get_fontset(0,0,xtest)
    #print(label)
    #xtest=[[0,33,22]]
    #label2=nb_model(1,0,xtest)
    #print(label2)
    get_weights(5,[0,0,0,30,30],[100,50,30,100,40],[],[])
    
    

if __name__ == '__main__':
    main()