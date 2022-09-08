from __future__ import print_function
from numpy import argmin
from ortools.sat.python import cp_model
from sqlalchemy import null
import layout_test.tex2ortools
# import tex2ortools
import time
from PIL import Image
import os
import numpy as np


#读取报花库图片信息
def read_picinfo(image_name,bh_path):
    im = Image.open(bh_path+'\\'+image_name)#返回一个Image对象
    #图片尺寸大小单位转化：实际尺寸(英寸)=像素/分辨率; 1英寸=2.54厘米
    idpi=im.info['dpi'][0]#图片分辨率
    iw=(im.size[0]/idpi)*25.4#图片宽度(mm)
    ih=(im.size[1]/idpi)*25.4#图片高度(mm)
    ir=iw/ih
    iname=image_name.split('.')[0]
    idict=dict({'name':iname,'width':iw,'height':ih,'ratio':ir}) #图片属性信息（可加入图片语义信息）
    return idict

#最近邻选择要插入的报花图片（高度eh大于7才插入报花图片）
def select_pic(image_dict,ew,eh):
    er=ew/eh
    dis=[]
    for i in range(len(image_dict)):
        dis.append(abs(image_dict[i]['ratio']-er)) #找出和留白区域比例最接近的报花
    index=argmin(dis)
    return image_dict[index]
    
#建立关于报花图片高度的高斯分布(无法放到目标函数中，故改为绝对值函数)
def gauss_bh(image,rho,ew,eh):
    pr=image['ratio']
    ph=ew/pr
    pro=np.exp(-((eh - ph)**2)/(2*rho**2)) / (rho * np.sqrt(2*np.pi))
    return pro

def main(frame_cond:layout_test.tex2ortools.Frame_cond,frame_data:list,s:list):
    """以frame_cond为矩形约束，文章大小列表articles的条件下，进行矩形划分，以sum((w/h-0.618)**2)为目标函数"""
    #建立模型
    # print('-------------start-----------')
    model = cp_model.CpModel()
    n = frame_cond.count  #新闻块数量
    print("n:",n)
    #创建变量
    #frame变量
    frames_x = []#x坐标
    frames_y = []#y坐标
    frames_w = []#w宽度
    frames_h = []#h高度
    frames_v = []#v面积
    ends_x = []#x+w
    ends_y = []#x+h
    ###新闻块真实面积和留白面积
    articles=[]
    objs = []
    
    ##########
    #article变量
    #pass
    for i in range(n):
        end_x = model.NewIntVar(0,1000,'end_frame_%d' % i)
        end_y = model.NewIntVar(0,1000,'end_frame_%d' % i)
        frame_x = model.NewIntVar(0,1000,'frame_%d_x' % i)
        frame_y = model.NewIntVar(0,1000,'frame_%d_y' % i)
        frame_w = model.NewIntVar(0,1000,'frame_%d_w' % i)#矩形宽度范围
        frame_h = model.NewIntVar(0,1000,'frame_%d_h' % i)#矩形高度范围
        frame_v = model.NewIntVar(0,1000000,'frame_%d_v' % i)#矩形面积范围
        ###1
        article=model.NewIntVar(0,1000000,'article_%d' % i)
        obj = model.NewIntVar(0,1000000,'obj_%d' % i)
        
        
        
        ends_x.append(end_x)
        ends_y.append(end_y)
        frames_x.append(frame_x)
        frames_y.append(frame_y)
        frames_w.append(frame_w)
        frames_h.append(frame_h)
        frames_v.append(frame_v)
        ###1
        articles.append(article)
        objs.append(obj)
        
        
    max_hs=model.NewIntVar(0,1000,'max_hs')
    #增加约束（article）
    #pass
    ############################################################
    #增加约束（frame）
    #x和w固定
    for i in range(len(frame_data)):
        model.Add(frames_x[i] == int(frame_data[i][0]*1000))
    for i in range(len(frame_data)):
        model.Add(frames_w[i] == int(frame_data[i][2]*1000))

    #增加y和h的约束
    for i in frame_cond.y_equal_0:
        model.Add(frames_y[i] == 0)
    for i,j in frame_cond.y_equal_y:
        model.Add(frames_y[i] == frames_y[j])
    for i,j in frame_cond.h_equal_h:
        model.Add(frames_h[i] == frames_h[j])
    for i,j in frame_cond.yh_equal_y:
        model.Add(frames_y[i] + frames_h[i] == frames_y[j])
    for i in frame_cond.yh_equal_100:
        model.Add(frames_y[i] + frames_h[i] == 1000)
    model.Add(frames_h[0]== int(frame_data[0][3]*1000)) #固定报头高度

    ################################################################
    model.AddAllowedAssignments(articles,s)#即新闻块面积在s集合中进行采样
    #通用约束
    for i in range(n):
        model.AddMultiplicationEquality(frames_v[i],[frames_w[i],frames_h[i]]) #w*h=v
        model.Add(frames_v[i] >= articles[i])
        model.Add(objs[i]==frames_v[i]-articles[i])  #每块新闻块的留白区间
        
    ######增加报花的相关约束
    
    #读取报花信息（报花信息过多时，可以先聚类再读取比例信息）
    bh_path=os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "./bh_image/"))
    pathDir=os.listdir(bh_path) #读取图片文件夹下所有图片名称 
    sdict=[]
    for i in pathDir:
        t=read_picinfo(i,bh_path)
        ratio=t['ratio']
        sdict.append(int(round(ratio*100,0)))  #扩大两倍
    print(sdict)
    

    ###############创建变量##########################
    bh_inters1=[] #中间变量
    bh_inters2=[]
    bh_lists=[]
    temp1=[]
    temp2=[]
    h_bools={}
    #bh_init_ratios=[]
    ####创建二维数组变量
    for i in range(n):
        for j in range(len(sdict)):
            bh_list=model.NewIntVar(-1000000000,1000000000,'bh_list_%d_%d' % (i,j))
            temp1.append(bh_list)
            bh_inter1=model.NewIntVar(-1000000000,1000000000,'bh_inter1_%d_%d' % (i,j))
            temp2.append(bh_inter1)
        bh_inters1.append(temp2)
        bh_lists.append(temp1)
        temp1=[]
        temp2=[]
    
    ehs = [] #留白高度
    ews = [] #留白宽度
    ers=[] #留白区域比例
    bh_ratios=[] #报花集合中图片的比例
    ews_inter=[] #宽度*100的中间变量
    ehs_inter=[]
    ers_inter=[]
    objs_inter=[]

    eh_bools={}
    obj_bools={}
    
    max_hs=model.NewIntVar(0,1000000,'max_hs')
    for i in range(n):
        bh_inter2=model.NewIntVar(0,100000000,'bh_inter2_%d' % i)
        bh_inters2.append(bh_inter2) 
        eh = model.NewIntVar(0,100000,'e_%d_h' % i)
        ew = model.NewIntVar(0,100000,'e_%d_w' % i)
        bh_ratio=model.NewIntVar(0,100000,'bh_%d_ratio' % i) 
        er=model.NewIntVar(0,1000000000,'er_%d' % i)
        ew_inter= model.NewIntVar(0,1000000,'ew_inter_%d' % i)
        eh_inter= model.NewIntVar(0,1000000000,'eh_inter_%d' % i)
        er_inter= model.NewIntVar(0,1000000000,'er_inter_%d' % i)
        obj_inter=model.NewIntVar(0,1000000,'obj_inter_%d' % i)
        eh_bools[i]=model.NewBoolVar('eh_bool_%d'%i) #布尔变量，表示条件
        obj_bools[i]=model.NewBoolVar('obj_bool_%d'%i) #布尔变量，表示条件

        ews.append(ew)
        ehs.append(eh)
        bh_ratios.append(bh_ratio)
        ers.append(er)
        ews_inter.append(ew_inter)
        ehs_inter.append(eh_inter)
        ers_inter.append(er_inter)
        objs_inter.append(obj_inter)
    
    ################添加报花约束###################
    for i in range(n):
        model.AddDivisionEquality(ehs[i],objs[i],frames_w[i]) #留白高度,ehs可能为0  
        model.Add(ews[i]==frames_w[i]-31)  #留白宽度为方框宽度减去左右间距10mm
        model.Add(ews_inter[i]==ews[i]*100) #宽度扩充100倍，相当于比例扩充100倍
        
        model.Add(ehs[i]>=40).OnlyEnforceIf(eh_bools[i])  #限定留白高度插入报花图片的阈值13mm
        model.Add(ehs[i]<40).OnlyEnforceIf(eh_bools[i].Not())
        
        model.Add(ehs_inter[i]==ehs[i]).OnlyEnforceIf(eh_bools[i])
        model.Add(ehs_inter[i]==1000000000).OnlyEnforceIf(eh_bools[i].Not()) #保证高度不为0,防止除法出错
        
        model.AddDivisionEquality(ers[i],ews_inter[i],ehs_inter[i]) #计算留白比例（扩充100倍）

        model.Add(ers_inter[i]==ers[i]).OnlyEnforceIf(eh_bools[i])
        model.Add(ers_inter[i]==10000).OnlyEnforceIf(eh_bools[i].Not())
        
        #model.Add(bh_inters1[i]==ers_inter[i]-sdict[i])
        for j in range(len(sdict)):    #计算图片库比例与留白区域比例的差值
            
            h_bools[i,j]=model.NewBoolVar('h_bool_%d%d'%(i,j))
            model.Add(sdict[j]>ers_inter[i]).OnlyEnforceIf(h_bools[i,j])
            model.Add(sdict[j]<=ers_inter[i]).OnlyEnforceIf(h_bools[i,j].Not())
            
            model.Add(bh_inters1[i][j]==sdict[j]-ers_inter[i]).OnlyEnforceIf(h_bools[i,j])
            model.Add(bh_inters1[i][j]==ers_inter[i]-sdict[j]).OnlyEnforceIf(h_bools[i,j].Not())
            
        model.AddMinEquality(bh_inters2[i],bh_inters1[i])  #在报花库中选择比例差距最小的
        ######
        
        model.Add(bh_ratios[i]==bh_inters2[i]).OnlyEnforceIf(eh_bools[i])
        model.Add(bh_ratios[i]==0).OnlyEnforceIf(eh_bools[i].Not())
        
    model.AddMaxEquality(max_hs,bh_ratios) #一组布局数据中最大的比例差值
    
    '''
    for i in range(n-1):
        model.Add(9*frames_v[i] >= 10*articles[i]) #新闻块留白空间限制,加入可能会使求解器无解
    '''
    #####################
    #目标函数(中间约束)
    coe=[10**i for i in range(n-1,-1,-1)]  #留白面积权重初始设置
    model.Minimize(cp_model._ScalProd(objs,coe)+100*max_hs) #给每个新闻块留白面积前乘以权重+1000*max_hs
    #model.Minimize(max_hs)
    #创建求解器并求解  
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    ret = [[] for i in range(n)]
    if status == cp_model.OPTIMAL:
        # print('Maximum of objective function: %i' % solver.ObjectiveValue())
        ret.append(solver.ObjectiveValue())
        for i in range(n):
            ret[i] = [solver.Value(frames_x[i]),solver.Value(frames_y[i]),solver.Value(frames_w[i]),solver.Value(frames_h[i])]
        ret.append([solver.Value(articles[i]) for i in range(n)]) #返回选择的面积组合
        #ret.append([solver.Value(objs[i]) for i in range(n)])
        #ret.append([solver.Value(ehs[i]) for i in range(n)])
        #ret.append([solver.Value(ers_inter[i]) for i in range(n)])
        #ret.append([solver.Value(ehs_inter[i]) for i in range(n)])
        #ret.append([[solver.Value(bh_inters1[i][j]) for j in range(len(sdict))]for i in range(n)])
        #ret.append([solver.Value(bh_ratios[i]) for i in range(n)])
        #ret.append(solver.Value(max_hs))
        #print(ret)
        #print('============================')
        return ret,n
    else:
        # print("no optimal solution")
        return None,n
    
def solver_layout(d,s):
    frame_cond = layout_test.tex2ortools.main(d)
    ret,n = main(frame_cond, d,s)
    if ret==None:
        return null,-1
    real_frame=[]
    index=-1
    for i in range(n):
        temp=[ret[i][j]*0.001 for j in range(4)]
        real_frame.append(temp) #被调整后的布局结构
    for i in range(len(s)):
        if s[i]==ret[-1]:
            index=i #最优面积组合的下标
            break
    return real_frame,index


if __name__ == '__main__':
    start = time.time()
    
    #d = ['73_6_4_14', [[0.0, 0.0, 0.0, 0.0, 0.3, 0.7, 0.7], [0.0, 0.1, 0.26, 0.42, 0.26, 0.1, 0.27], [1.0, 0.7, 0.3, 0.3, 0.4, 0.3, 0.3], [0.1, 0.16, 0.16, 0.58, 0.74, 0.17, 0.73]], (1, 3, 5, 4, 2, 6), [2398, 1310, 1155, 914, 1370, 933]]
    d=[[0.0, 0.83, 1.0, 0.17], [0.0, 0.52, 0.68, 0.31], [0.0, 0.31, 0.68, 0.21], [0.0, 0.0, 0.22, 0.31], [0.22, 0.0, 0.46, 0.31], [0.68, 0.21, 0.32, 0.62], [0.68, 0.0, 0.32, 0.21]]
    #d=[[0.0, 0.83, 1.0, 0.17], [0.0, 0.52, 0.67, 0.31], [0.0, 0.29, 0.67, 0.23], [0.0, 0.0, 0.28, 0.29], [0.28, 0.0, 0.39, 0.29], [0.67, 0.19, 0.33, 0.64], [0.67, 0.0, 0.33, 0.19]]
    frame_cond = tex2ortools.main(d)
    for key,value in frame_cond.__dict__.items():
        print(key,' ',value)
    s=[[170000,142800,149600,68200,161000,160000,67200],[170000,142800,170000,68200,161000,160000,112000],[170000,142800,170000,68200,161000,160000,105600]]
    ret = main(frame_cond, d,s)
    print(ret)#[x,y,w,h],obj
    
    end = time.time()
    print('running time',end - start)