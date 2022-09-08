import math
class Frame_cond:
    """矩形约束对象，用于描述ortools需要添加的矩形约束"""
    def __init__(self) -> None:
        self.x_equal_0 = []
        self.y_equal_0 = []
        self.x_equal_x = []
        self.y_equal_y = []
        self.w_equal_w = []
        self.h_equal_h = []
        self.xw_equal_x = []
        self.yh_equal_y = []
        self.xw_equal_100 = []
        self.yh_equal_100 = []
        self.count = 0
    def output__(self):
        print(self.__dict__)
def f2int(a):
    return int(round(a*100,0))

def get_wh_eq(x_eq:list,wh:list):
    """输入x或y坐标相同的序号1维列表，输出宽度w相同的序号2维列表"""
    w_eq = []
    w_tmp = []#用于x,y坐标对应的不同w,h值
    for i in x_eq:
        if wh[i] not in w_tmp:
            w_tmp.append(wh[i])#第一次出现新元素则1放入列表中，2增加新的序号列表
            w_eq.append([i,])
        else:
            for j in w_eq:
                if wh[j[0]] == wh[i]:#将序号放到w,h值相同的列表中
                    j.append(i)
                    break
    return w_eq

def test():
    pass

def main(frame:list):
    """将矩形参数列表转化为矩形约束对象"""
    #创建frame_cond约束实例
    frame_cond = Frame_cond()
    #矩形分布参数
    # x = [0.00,0.00,0.00,0.00,0.25,0.25,0.25,0.25,0.50,0.50,0.60,0.65,0.70,0.75,0.80]
    # y = [0.84,0.56,0.28,0.00,0.63,0.42,0.21,0.00,0.42,0.00,0.00,0.42,0.00,0.42,0.00]
    # w = [1.00,0.25,0.25,0.25,0.25,0.25,0.25,0.25,0.15,0.10,0.10,0.10,0.10,0.25,0.20]
    # h = [0.16,0.28,0.28,0.28,0.21,0.21,0.21,0.21,0.42,0.42,0.42,0.42,0.42,0.42,0.42]
    x = [frame[i][0] for i in range(len(frame))]
    y = [frame[i][1] for i in range(len(frame))]
    w = [frame[i][2] for i in range(len(frame))]
    h = [frame[i][3] for i in range(len(frame))]
    n = len(x)
    frame_cond.count = n
    #print(y)
    #转化为整数列表
    x = list(map(f2int,x))
    y = list(map(f2int,y))
    w = list(map(f2int,w))
    h = list(map(f2int,h))

    ####

    x_and_w = [x[i] + w[i] for i in range(n)]
    y_and_h = [y[i] + h[i] for i in range(n)]
    #print('y_and_h:',y_and_h)
    ##找出所有的竖线|---x与x_and_w中的不同值个数
    vertical = []
    for i in range(n):
        if x[i] not in vertical:
            vertical.append(x[i])
        if x_and_w[i] not in vertical:
            vertical.append(x_and_w[i])
    vertical.sort()
    # print(vertical)

    ##转化成关于x与w的约束
    ###1.寻找x_i==0以及x_i==x_j约束
    vx = [[] for i in range(len(vertical))]#用于存储每一根竖线上的x坐标
    for i in range(len(vertical)):#遍历每一根竖线，寻找相同的x坐标
        for j in range(n):
            if x[j] == vertical[i]:
                vx[i].append(j)
    # print(vx)
    # print('----x_i=0------')
    for i in range(len(vertical)):
        if i == 0:
            for j in vx[i]:
                # print('x_%i = 0' % j)
                frame_cond.x_equal_0.append(j)
            # print('----x_i=x_j------')
        elif len(vx[i]) >= 2:
            for j in range(1,len(vx[i])):
                # print('x_%i = x_%i ' % (vx[i][j-1],vx[i][j]) ) 
                frame_cond.x_equal_x.append((vx[i][j-1],vx[i][j]))
    ##2.寻找w_i==w_j约束 (and x_i == x_j)
    # print('----w_i=w_j------')
    for i in range(len(vertical)):
        if len(vx[i]) >= 2:
            w_eq = get_wh_eq(vx[i],w)
            for j in w_eq:
                if len(j) >= 2:
                    for k in range(1,len(j)):
                        # print('w_%i = w_%i ' % (j[k-1],j[k]) )
                        frame_cond.w_equal_w.append((j[k-1],j[k]))  
    ###3.寻找x_i+w_i=x_j的约束(给个误差)
    # print('----x_i+w_i=x_j------')
    for i in range(n):#遍历每一个x_and_w
        for j in vx:#寻找每一竖线的x坐标,取第一个：x_i + w_i == x_j
            if (len(j) > 0 and x_and_w[i] == x[j[0]]) or (len(j) > 0 and abs(x_and_w[i]-x[j[0]])<=1): ######
                # print('x_%i + w_%i = x_%i' % (i,i,j[0]))
                frame_cond.xw_equal_x.append((i,j[0]))
                break
        
    ###4.寻找x_i+w_i=100的约束
    # print('-----x_i+w_i=100-----')
    for i in range(n):
        if x_and_w[i] == 100 or x_and_w[i]==99: #增加四舍五入小数时的误差
            # print('x_%i + w_%i = 100' % (i,i))
            frame_cond.xw_equal_100.append(i)
    ##########################################
    ##找出所有的横线——---y与y_and_h中的不同值个数
    horizontal = []
    for i in range(n):
        if y[i] not in horizontal:
            horizontal.append(y[i])
        if y_and_h[i] not in horizontal:
            horizontal.append(y_and_h[i])
    horizontal.sort()
    # print(y)
    # print(y_and_h)
    # print('horizontal---',horizontal)
    ##转化成关于y与h的约束
    ###1.寻找y_i==0以及y_i==y_j约束
    hy = [[] for i in range(len(horizontal))]#用于存储每一根heng线上的y坐标
    for i in range(len(horizontal)):#遍历每一根heng线，寻找相同的y坐标
        for j in range(n):
            if y[j] == horizontal[i]:
                hy[i].append(j)
    # print('hy---',hy)
    # print('----y_i=0------')
    for i in range(len(horizontal)):
        if i == 0:
            for j in hy[i]:
                # print('y_%i = 0' % j)
                frame_cond.y_equal_0.append(j)
            # print('----y_i=y_j------')
        elif len(hy[i]) >= 2:
            for j in range(1,len(hy[i])):
                # print('y_%i = y_%i ' % (hy[i][j-1],hy[i][j]) ) 
                frame_cond.y_equal_y.append((hy[i][j-1],hy[i][j]))

    ##2.寻找h_i==h_j约束 (and y_i == y_j)
    # print('----h_i=h_j------')
    for i in range(len(horizontal)):
        if len(hy[i]) >= 2:
            w_eq = get_wh_eq(hy[i],h)
            for j in w_eq:
                if len(j) >= 2:
                    for k in range(1,len(j)):
                        # print('h_%i = h_%i ' % (j[k-1],j[k]) )  
                        frame_cond.h_equal_h.append((j[k-1],j[k]))
    ###3.寻找y_i+h_i=y_j的约束
    # print('----y_i+h_i=y_j------')
    for i in range(n):#遍历每一个x_and_w
        for j in hy:#寻找每一竖线的x坐标,取第一个：x_i + w_i == x_j
            if (len(j) > 0 and y_and_h[i] == y[j[0]]) or (len(j) > 0 and abs(y_and_h[i]-y[j[0]])<=1):
                # print('y_%i + h_%i = y_%i' % (i,i,j[0]))
                frame_cond.yh_equal_y.append((i,j[0]))
                break
        
    ###4.寻找y_i+h_i=100的约束
    # print('-----y_i+h_i=100-----')
    for i in range(n):
        if y_and_h[i] == 100 or y_and_h==99:
            # print('y_%i + h_%i = 100' % (i,i))
            frame_cond.yh_equal_100.append(i)
    return frame_cond

if __name__ == '__main__':
    #frame=[[0.0, 0.8300000000000001, 1.0, 0.17], [0.0, 0.52, 0.68, 0.31], [0.0, 0.31, 0.68, 0.21], [0.0, 0.0, 0.22, 0.31], [0.22, 0.0, 0.46, 0.31], [0.68, 0.21, 0.32, 0.62], [0.68, 0.0, 0.32, 0.21]]
    #frame=[[0.0, 0.83, 1.0, 0.17], [0.0, 0.52, 0.67, 0.31], [0.0, 0.29, 0.67, 0.23], [0.0, 0.0, 0.28, 0.29], [0.28, 0.0, 0.39, 0.29], [0.67, 0.19, 0.33, 0.64], [0.67, 0.0, 0.33, 0.19]]
    frame=[[0.0, 0.83, 1.0, 0.17], [0.0, 0.51, 0.72, 0.32], [0.0, 0.30, 0.72, 0.22], [0.72, 0.30, 0.28, 0.53], [0.0, 0.13, 0.54, 0.16], [0.54, 0.13, 0.46, 0.16], [0.0, 0, 1.0, 0.13]]
    frame_cond = main(frame)
    for key,value in frame_cond.__dict__.items():
        print(key,' ',value)
    