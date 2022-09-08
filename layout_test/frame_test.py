import numpy as np
import time

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
    return res

def find_last_element(lastele,s,his_leaves):
    node_length=1
    node_id=''
    for i in range(s.size()):
        if lastele in his_leaves[s.items[i][0]]:
            node_length=len(his_leaves[s.items[i][0]])
            node_id=s.items[i][0]
            s.remove(i)
            return True,node_length,node_id
    return False,node_length,node_id

def adjust_y(nodelist,s,his_leaves,div_eq,used,C_bh,real_y,dict_pre):
    j=0
    sumh_l=0 
    flag_l,nodelen_l,nodeid_l=find_last_element(nodelist[-1],s,his_leaves) #需要改变高度的新闻块集合
    while j<(len(nodelist)-nodelen_l):
        if used[nodelist[j]]==1:
            a,b,c=find_last_element(nodelist[j],s,his_leaves)
            sumh_l=sumh_l+C_bh[c]
            j=j+b
        elif used[nodelist[j]]==0:
            sumh_l=sumh_l+real_y[nodelist[j]-1]
            used[nodelist[j]]=1
            j=j+1
    h_rest=C_bh[div_eq['id']]-sumh_l  #记录sumh
    #print('sumh_l:',sumh_l)
    if flag_l==False: #即底部新闻块为1
        real_y[nodelist[-1]-1]=h_rest
        dict_pre[nodelist[-1]]=sumh_l
    else: #组合型
        for k in range(len(his_leaves[nodeid_l])):
            if his_leaves[nodeid_l][k] in dict_pre:
                real_y[his_leaves[nodeid_l][k]-1]=h_rest-dict_pre[his_leaves[nodeid_l][k]]

def test1(div_eq,his_leaves,C_bh,bw,S):    #还未考虑到横向分割的布局
    i=len(div_eq)-1
    used=np.zeros(len(S)+1)  #记录各新闻块面积是否已经计算
    s=Stack()  #存储面积已经计算好的节点
    dict_pre={}
    real_y=[S[i]/bw[i] for i in range(len(S))] #存储每个新闻块的初始高度
    print('初始y:',real_y)
    while i>=0:  #从后往前计算
        if div_eq[i]['id'].startswith('C'):
            left=div_eq[i]['num']
            right=div_eq[i]['denum']
            adjust_y(left,s,his_leaves,div_eq[i],used,C_bh,real_y,dict_pre)
            adjust_y(right,s,his_leaves,div_eq[i],used,C_bh,real_y,dict_pre)
            s.push([div_eq[i]['id']])
        i=i-1
    print('调整y：',real_y)
    print(dict_pre)
            

def change_frame(frame_list,S,bw_list,height):
    #frame_list里一维数据的顺序为[x,y,w,h],这里height为减去报尾高度后的高度
    real_h=[S[i]/bw_list[i] for i in range(len(S))]  #每个新闻块的真实高度
    print(real_h)
    for j in range(len(frame_list)):
        y_pre=frame_list[j][1]*height
        h_pre=frame_list[j][3]*height
        frame_list[j][3]=real_h[j]/height #改变h值
        #查找布局结构为c下的布局点，存储前一个节点的高度

        #frame_list[j][1]=(y_pre+h_pre-real_h)/height
    return frame_list


def main():
    '''
    frame_list=[[0.0, 0.8300000000000001, 1.0, 0.17], [0.0, 0.52, 0.68, 0.31], [0.0, 0.31, 0.68, 0.21], [0.0, 0.0, 0.22, 0.31], [0.22, 0.0, 0.46, 0.31], [0.68, 0.21, 0.32, 0.62], [0.68, 0.0, 0.32, 0.21]]
    S=[1700,1360,682,1748,1664,672] #对应真实高度25，20，31，38，52，21
    bw_list=[68,68,22,46,32,32]
    height=100
    ret=change_frame(frame_list[1::],S,bw_list,height)
    print(ret)
    '''
    '''
    test='C70(R31()(R45(C32(R67()(C32()()))())()))(R60()())'
    bw=[30,20,10,10,10,30,10,10] 
    S=[600,200,120,150,300,300,200,200] #高度为20,10,12,15,30,10,20,20
    '''
    '''
    test='C11(R33()(C44(R55()())(C66(R77()())(R88()()))))(R22()())'
    bw=[30,10,10,10,10,10,10,10,10]
    S=[300,100,200,200,200,250,200,200,200]
    '''
    start=time.time()
    test='C68(R21()(R30()(C39()())))(R45()())'
    bw=[680,680,220,460,320,320]
    S=[142800,170000,68200,161000,160000,105600]
    root=test[0:3]+'a'  #头节点
    his_leaves,right_treenode=read_tree(test)
    div_eq=generate_linear_constraint(his_leaves,right_treenode,root)
    print(div_eq)
    res=calculate_col_S(div_eq,bw,S,his_leaves)
    print(res)
    res[root]=830 #使根节点的高度为纸张的高度
    test1(div_eq,his_leaves,res,bw,S)
    end=time.time()
    print('运行时间：',end-start)





if __name__=="__main__":
    main()