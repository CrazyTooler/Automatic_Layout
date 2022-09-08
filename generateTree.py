import numpy as np
import pandas as pd
import time
import pymysql
import matplotlib.pyplot as plt

class SplitException(Exception):
    pass

def updatePageStructure(id, s):
    db = pymysql.connect(host='121.196.99.106',user='root',password='zzysky123',database='rawnewsdata')
    cursor = db.cursor()
    sql = f"UPDATE headpages_style SET PAGE_STRUCTURE = '{s}' WHERE PAGEID = {id};"
    try:
        cursor.execute(sql)
        db.commit()
    except:
        print('更新失败')
        db.rollback()
    db.close()

def getOperations(areas):
    """根据坐标位置划分操作"""
    # print(areas)
    #########################C
    left_ = []
    right_ = []
    col_V = 0
    for i in range(100):
        for x in areas.index:
            if areas.loc[x, "x2"] <= i:
                left_.append(x)
            elif  areas.loc[x, "x1"] >= i:
                right_.append(x)
            else:
                left_.clear()
                right_.clear()
                break
        col_V = i
        if left_ and right_:
            # print(["C", col_V, left_, right_])
            return ["C", col_V, left_, right_]
    ##########################
    #########################R
    up_ = []
    down_ = []
    row_V = 0
    for i in range(100):
        for x in areas.index:
            if areas.loc[x, "y2"] <= i:
                up_.append(x)
            elif  areas.loc[x, "y1"] >= i:
                down_.append(x)
            else:
                up_.clear()
                down_.clear()
                break
        row_V = i
        if up_ and down_:
            # print(["R", row_V, up_, down_])
            return ["R", row_V, up_, down_]
    ##########################
    raise SplitException()

def getTreeStr(areas):
    """输入版面各个矩形的位置信息，输出版面结构""" 
    if areas.shape == (1,4):
        return ""
    else:
        op = getOperations(areas)
        return op[0]+ str(op[1]) + "(" + getTreeStr(areas.loc[op[2],:]) + ")" +"("+ getTreeStr(areas.loc[op[3],:]) +")"

def visulizeThePage(page):
    """page结构图"""
    fig,ax=plt.subplots()
    plt.axis('equal')
    ax.xaxis.set_ticks_position('top')
    ######
    for i in page.index:
        x = [page.loc[i,"x1"], page.loc[i,"x2"], page.loc[i, "x2"], page.loc[i,"x1"], page.loc[i,"x1"]]
        y = [page.loc[i,"y1"], page.loc[i,"y1"], page.loc[i, "y2"], page.loc[i,"y2"], page.loc[i,"y1"]]
        plt.plot(x,y,'b')
    ######
    plt.show()

def main():
    """版面矩形位置转换为二叉树结构，用字符串存储"""
    with open('./banmianStructure.csv') as f:
        data = np.loadtxt(f, delimiter='\t', usecols=[1,2,3,4,5])
    pages = np.array(100*data, dtype=int, copy=True)
    pagesId = set(pages[:,0])
    count = 0
    for id in pagesId:
        page = pages[np.where(pages==id)[0], 1:]
        page[:,2] += page[:,0]
        page[:,3] += page[:,1]
        page = pd.DataFrame(page, columns=["x1","y1","x2","y2"])
        try:
            pageTree = getTreeStr(page)
        except Exception as e:
            # print(id, page)
            # visulizeThePage(page)
            continue
        count += 1
        print(id//100, pageTree)
        ##将结构字符串插入数据库
        # updatePageStructure(id//100, pageTree)
    print(count)

if __name__ == "__main__":
    start = time.time()
    main()
    print("time:", time.time() - start)