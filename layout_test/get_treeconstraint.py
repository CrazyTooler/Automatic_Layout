'''
通过包含拓扑结构约束的字符串返回各个新闻块面积约束关系
字符串形如：C71(R38()(R64()(R77()())))(R58()()),前序遍历字符串
'''
import numpy as np
import pandas as pd

class Stack:
    """模拟栈"""
    def __init__(self):
        self.items = [] #数组
    def isEmpty(self):
        return len(self.items)==0 
    def push(self, item):
        self.items.append(item)
    def pop(self):
        return self.items.pop() 
    def remove(self,index):
        return self.items.pop(index) 
    def peek(self):
        if not self.isEmpty():
            return self.items[len(self.items)-1]
    def size(self):
        return len(self.items)

#只读取纵向分割操作下的约束
def read_tree(treestr):
    s1=Stack()#只记录中间节点
    s2=Stack()#存放字符串
    i=0
    count=0 #记录叶子节点
    his_leaves={} #记录一个中间节点下所有的叶子节点
    right_treenode={}#记录每棵子树下右子树的开始节点
    his_leaves_level={} #记录中间节点下的直系叶子节点

    temp=97  #加入小写字母ascii码防止键值重复
    while i<len(treestr):
        if treestr[i].isalpha():
            s2.push(treestr[i:i+3])
            s1.push(treestr[i:i+3]+chr(temp))
            his_leaves[treestr[i:i+3]+chr(temp)]=[]   #创建每个中间节点对应的叶子集合
            his_leaves_level[treestr[i:i+3]+chr(temp)]=[]

            i=i+3
            temp=temp+1
        if treestr[i]=='(': 
            s2.push(treestr[i])
            i=i+1
        elif treestr[i]==')': 
            if s2.peek()=='(': #判断括号是否是连在一起的
                s2.pop()
                his_leaves_level[s1.peek()].append(count+1)
                for j in range(s1.size()):
                    his_leaves[s1.items[j]].append(count+1)
                count+=1
            elif s2.peek!='(':
                s2.pop()#一般为中间节点的值
                s1.pop()
                s2.pop()#一般为'('
            i=i+1 
    #print(count)
    print(his_leaves)
    print(his_leaves_level)
    #####遍历叶子字典记录横向分割的位置
    s3=Stack() #记录纵向切割的节点
    for k,v in his_leaves.items():
        if not s3.isEmpty():
            if his_leaves[s3.peek()][0]==v[0]: #表示该节点左子树不是叶子节点
                right_treenode[s3.peek()]=his_leaves[s3.peek()][len(v)]
                s3.pop()
            else: #表示该节点左子树为叶子节点
                right_treenode[s3.peek()]=his_leaves[s3.peek()][0]+1
                s3.pop()
        #if k.startswith('C'): #找出纵向分割的节点
        if len(v)<3: #二分为叶子节点
            right_treenode[k]=v[1]
        elif len(v)>=3:
            s3.push(k)
    print(right_treenode)
    return his_leaves,right_treenode

######生成约束字典##########
def get_sepindex(treelist,seppoint):
    for i in range(0,len(treelist)):
        if treelist[i]==seppoint:
            return i

def generate_linear_constraint(his_leaves,right_treenode,root):  
    div_eq=[]  #存储纵向分割的约束
    dict_temp={}
    root_rightindex=right_treenode[root]
    for k,v in his_leaves.items():
        #if k.startswith('C'):
            dict_temp['id']=k
            dict_temp['ratio']=int(k[1:3])
            index=get_sepindex(his_leaves[k],right_treenode[k])
            dict_temp['num']=his_leaves[k][0:index]
            dict_temp['denum']=his_leaves[k][index::]
            minindex=min(dict_temp['denum'])
            '''
            if root_rightindex>minindex:
                dict_temp['tree_pos']='left'
            elif root_rightindex==minindex:
                dict_temp['tree_pos']='root'
            else:
                dict_temp['tree_pos']='right'
                '''
        #if  dict_temp:
            div_eq.append(dict_temp) 
            dict_temp={}
    return div_eq

########根据约束计算每个新闻块的面积及高度#######################
def aisinb(s,num,his_leaves):  #得到节点下已计算区域的高度、面积信息
    val=0
    for i in range(s.size()):
        if his_leaves[s.items[i][0]]==num:
            val=s.items[i][1]
            s.remove(i) 
            break
    return val

#求解每个中间节点下所有新闻块的面积（莫名其妙就求出来了，改进的地方较多）
def calculate_col_S(div_eq,bw,S,his_leaves): #这里的div_eq根据左右子树分为两部分（除去根节点）
    i=len(div_eq)-1
    used=np.zeros(len(S)+1)  #记录各新闻块面积是否已经计算
    s=Stack()  #存储面积已经计算好的节点
    res={}
    real_y=[] #存储每个新闻块的真实高度
    while i>=0:  #从后往前计算
        left=div_eq[i]['num']
        right=div_eq[i]['denum']
        bh_l=0
        bh_r=0
        for j in range(len(left)):
            if used[left[j]]==1:
                bh_l=aisinb(s,left,his_leaves)
                break
            if used[left[j]]==0:
                bh_l=bh_l+(S[left[j]-1]/bw[left[j]-1])
                used[left[j]]=1

        for k in range(len(right)):
            if used[right[k]]==1:
                bh_r=aisinb(s,right,his_leaves)
                break
            if used[right[k]]==0:
                bh_r=bh_r+(S[right[k]-1]/bw[right[k]-1])
                used[right[k]]=1

        if div_eq[i]['id'].startswith('C'):
            bh=max(bh_l,bh_r)
        elif div_eq[i]['id'].startswith('R'):
            bh=bh_l+bh_r
        s.push([div_eq[i]['id'],bh])
        res[div_eq[i]['id']]=bh
        i-=1
    print(real_y)
    return res

################求出可行解,sumS为纸张面积#########################################
#先判断是否为可行解，若不是则计算差距,若候选集和都不满足则挑选差距最小的组合进行修改
def pagesolver(frame_constraint,S,sumS,sumbh,bw):
    if np.sum(S)>sumS: #后面可以给定一个误差阈值
        print('S>sumS')
        return False
    root=frame_constraint[0:3]+'a'  #头节点
    his_leaves,right_treenode=read_tree(frame_constraint)
    div_eq=generate_linear_constraint(his_leaves,right_treenode,root)
    print(div_eq)
    res=calculate_col_S(div_eq,bw,S,his_leaves)
    print(res)
    sumh=res[root] #即头节点的总体高度
    real_h=sumbh
    print('sumh',sumh)
    print('realh',real_h) #且留白高度始终在底部
    if sumh>real_h:
        return False
    return True


def main():
    layoutstr=['C68(R31()(R21()(C31()())))(R62()())','C68(R30()(C50(R40()(C30()()))(C20()())))(R50(C10()())())','C68(R31()(R21()(C31()())))(R62()())','C71(R30()(R40()(R50(C30()())())))(R56()())','C25(R54()())(R48()(R68()(R88()())))','C71(R38()(R67()()))(R68()())','C71(R37()(R62()(R81()())))()','C71(R39()(R66()(R79()())))(R72()())','C50()()','R50(C31()())(C52()())']
    '''
    for i in range(len(layoutstr)):
        root=layoutstr[i][0:3]+'a'
        his_leaves,right_treenode=read_tree(layoutstr[i])
        div_eq=generate_linear_constraint(his_leaves,right_treenode,root)
        print(div_eq)
        print('-------------------')
    S=[30948.588000000003, 20159.172000000002, 5650.3224, 21745.856000000003, 16623.516000000003, 9222.796]
    
    root=layoutstr[0][0:3]+'a'
    his_leaves,right_treenode=read_tree(layoutstr[0])
    div_eq=generate_linear_constraint(his_leaves,right_treenode,root)
    print(div_eq)'''
    '''
    bw=[210.32000000000002, 210.32000000000002, 61.28, 139.04000000000002, 93.68, 93.68]
    S=[30948.588000000003, 20159.172000000002, 5901.264, 20042.616000000005, 21738.444000000003, 8468.672]
    #res=calculate_col_S(div_eq,bw,S,his_leaves)
    #print(res)
    r=pagesolver(layoutstr[0],S,131749.55199999997,403,bw)
    print(r)
    '''
    #test='C70(R31()(R42()(C33(R21()())())))(R51()())'
    test='C70(R31()(R45(C32(R67()(C32()()))())()))(R60()())'
    bw=[30,20,10,10,10,30,10,10] 
    S=[600,200,120,150,300,300,200,200] #高度为20,10,12,15,30,10,20,20
    r=pagesolver(test,S,2400,60,bw)
    print(r)



if __name__ == '__main__':
    main()