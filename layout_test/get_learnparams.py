import numpy as np
import time
'''
后面的回溯过程不仅是字号组合的判断，还可以加入面积的约束
'''


def select_legalcombination(fontsize,weights,picnews_index,picnews_font):
    res=[]
    temp=[]
    flag=0
    #增加fontsize选取操作（固定间距采样）
    fontsize=generate_fontsize(fontsize)
    #print(fontsize)
    #print(picnews_index)
    #生成字号字典
    dict={}
    count=0
    for i in range(len(fontsize)+len(picnews_index)):
        for j in range(len(picnews_index)):
            if i==picnews_index[j]: #若是图片新闻块就跳过
                flag=1
                break
            else: flag=0
        if flag==1:
            continue
        else:
            fontsize[count]=sorted(fontsize[count]) #让字号按从小到大排序
            dict['block'+str(i+1)]=fontsize[count]
            #print(dict)
            count+=1
    print(dict)
    #这里的权重表示头条、二头条、三头条的区分(不含图片新闻)
    page_backtracking(0,dict,weights,picnews_index,picnews_font,temp,res)
    #print(res)
    return res

def generate_fontsize(fontsize):#字号采样（最好可以实现换行和不换行的情况，这样同版面对比比较明显）
    newfont=[]
    for i in range(len(fontsize)):
        temp=[fontsize[i][0]]
        flag=fontsize[i][0]
        fontsize[i]=sorted(fontsize[i][1::]) #从小到大排列
        for j in range(len(fontsize[i])):
            if abs(fontsize[i][j]-flag)>=3 and abs(fontsize[i][j]-temp[0])>=3: #字号隔3pt取一次
                flag=fontsize[i][j]
                temp.append(fontsize[i][j])
        newfont.append(temp)
    return newfont  

def page_backtracking(index,dict,weights,picnew_index,picnews_font,temp,res):
    if index==(len(weights)-len(picnew_index)): #即遍历完每一个集合s
        if sorted(temp,reverse=True)==temp and len(set(temp))==len(temp): #判断temp是否有序（从大到小),后面也可以加上level，只判断前三个权重值
            #这里的字号顺序按权重大小，需要根据新闻块顺序重新组合
            ft_range=np.ones(len(weights))*21   
            for j in range(len(weights)-len(picnew_index)):
                ft_range[weights[j]-1]=temp[j]#根据新闻块顺序排序
            res.append(np.array(ft_range))
        return
    weight=weights[index]
    fontsize=dict['block'+str(weight)] #需要根据权重提供的处理
    for i in range(0,len(fontsize)):
        temp.append(fontsize[i])
        page_backtracking(index+1,dict,weights,picnew_index,picnews_font,temp,res)
        temp.pop()

def main():
    #res=select_legalcombination([[55,50,58,62],[50,62,68,63],[35,38,56,40]],[2,3,4,1,5],[0,4],21) #2在第一位表示区块2是头条区域
    #fontsize=generate_fontsize([[57,50,62],[62,63,68],[35,38,40,56]])
    #print(fontsize)
    start=time.time()
    res=select_legalcombination([[48,35],[35,40],[20,29,34],[37,45,50],[17,23,28]],[1,5,2,4,6,3],[2],21)
    end=time.time()
    print(res)
    print('运行时间：',end-start)

if __name__ == '__main__':
    main()