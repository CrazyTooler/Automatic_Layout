from __future__ import print_function
from ortools.sat.python import cp_model
from sqlalchemy import null
#import layout_test.tex2ortools
import tex2ortools
import time


def main(frame_cond:tex2ortools.Frame_cond,frame_data:list,s:list,h:list):
    """以frame_cond为矩形约束，文章大小列表articles的条件下，进行矩形划分，以sum((w/h-0.618)**2)为目标函数"""
    #建立模型
    # print('-------------start-----------')
    model = cp_model.CpModel()
    n = frame_cond.count  #新闻块数量
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
        
        ends_x.append(end_x)
        ends_y.append(end_y)
        frames_x.append(frame_x)
        frames_y.append(frame_y)
        frames_w.append(frame_w)
        frames_h.append(frame_h)
        frames_v.append(frame_v)
        articles.append(article)
        ###1
    
    #增加约束（article）
    for i in range(len(s)):
        model.Add(articles[i] == int(s[i]))
    ############################################################
    #增加约束（frame）
    #x和w固定
    for i in range(len(frame_data)):
        model.Add(frames_x[i] == int(frame_data[i][0]*1000))
    for i in range(len(frame_data)):
        model.Add(frames_w[i] == int(frame_data[i][2]*1000))
    for i in range(len(frame_data)):
        model.Add(frames_h[i] == int(h[i])) #固定h值，只求y


    #增加y和h的约束
    for i in frame_cond.y_equal_0:
        model.Add(frames_y[i] == 0)
    for i,j in frame_cond.y_equal_y:
        model.Add(frames_y[i] == frames_y[j])
    for i,j in frame_cond.yh_equal_y:
        model.Add(frames_y[i] + frames_h[i] == frames_y[j])
    for i in frame_cond.yh_equal_100:
        model.Add(frames_y[i] + frames_h[i] == 1000)
    model.Add(frames_h[0]== int(frame_data[0][3]*1000)) #固定报头高度

    ################################################################
    #通用约束
    for i in range(n):
        model.AddMultiplicationEquality(frames_v[i],[frames_w[i],frames_h[i]]) #w*h=v
        model.Add(frames_v[i] >= articles[i])

    #####################
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
    s=[170000, 142800, 170000, 68200, 161000, 160000, 105600]
    h=[170,210,250,370,370,500,330]
    ret = main(frame_cond, d,s,h)
    print(ret)#[x,y,w,h],obj
    end = time.time()
    print('running time',end - start)