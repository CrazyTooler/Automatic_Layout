import pymysql
 
def get_data(n:int):
    # 打开数据库连接
    db = pymysql.connect(host='121.196.99.106',user='root',password='zzysky123',database='tex_template')
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    sql = "select * from jrjd_headpage_frame1 where count = %d;" % n
    # sql = "select * from frame where article_count = %d;" % n
    # 使用 execute()  方法执行 SQL 查询 
    results = None
    try:
        cursor.execute(sql)
        ret = cursor.fetchall()
    except:
        print('error:unable to fetch data') 
    # 关闭数据库连接
    db.close()

    results = []
    names = []
    for r in ret:
        tx = list(map(lambda item: float(item),r[3][1:-1].split(',')))
        ty = list(map(lambda item: float(item),r[4][1:-1].split(',')))
        tw = list(map(lambda item: float(item),r[5][1:-1].split(',')))
        th = list(map(lambda item: float(item),r[6][1:-1].split(',')))
        # t = [tx,ty,tw,th,r[0]]#加上模板id
        t = [tx,ty,tw,th]
        results.append(t)
        names.append(r[2])
    return results,names

def getPagestructures(pagetree:str):
    # 打开数据库连接
    db = pymysql.connect(host='121.196.99.106',user='root',password='zzysky123',database='pageStructure')
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    sql = f"select avail_index from page where structs = '{pagetree}' limit 1;"
    # sql = "select * from frame where article_count = %d;" % n
    # 使用 execute()  方法执行 SQL 查询 
    results = None
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        return results[0]
    except:
        print('error:unable to fetch data') 
    # 关闭数据库连接
    db.close()

def savePagestructures(pagetree:str, avail_indexs):
     # 打开数据库连接
    db = pymysql.connect(host='121.196.99.106',user='root',password='zzysky123',database='pageStructure')
    # 使用 cursor() 方法创建一个游标对象 cursor
    seqs = str(avail_indexs)[1:-1]
    cursor = db.cursor()
    sql = f"insert into page(structs, avail_index) values('{pagetree}','{seqs}');"
    # sql = "select * from frame where article_count = %d;" % n
    # 使用 execute()  方法执行 SQL 查询 
    results = None
    try:
        cursor.execute(sql)
        db.commit()
    except:
        print('error:insert error') 
        db.rollback()
    # 关闭数据库连接
    db.close()

if __name__ == '__main__':
    ret = getPagestructures('qwer')
    print(ret[0].split(','))
    savePagestructures('ssdefe',[1,7,8,9])
