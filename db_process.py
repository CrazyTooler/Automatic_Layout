from os import error
import pandas as pd
import pymysql


#数据库中插入版面特征信息(总的)
def insert_features(dbconn, features):
    cursor = dbconn.cursor()###创建游标
    sql = "INSERT INTO headpages(article_id,bmid,pageid,atitle,ftitle,ytitle,article_x,article_y,article_w,article_h,maintitle_charsize,subtitle_charsize,\
        maintitle_area_coord,subtitle_area_coord,picture_area_coord,\
        title_style,atitle_char_count,ftitle_char_count,ytitle_char_count,text_char_count,picture_count,article_area,picture_area)\
        values({},{},{},'{}','{}','{}',{},{},{},{},{},{},'{}','{}','{}',{},{},{},{},{},{},{},{});".format(*features)###通过pageid找版面信息的sql
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        dbconn.commit()
    except:
        # 如果发生错误则回滚
        print(f'--something eror')
        raise 'ee'
        dbconn.rollback()

#选择有图新闻信息
def get_havepic_by_pageid(dbconn,pageid):
    cursor = dbconn.cursor()###创建游标
    sql = "select article_id,title_style,picture_area_coord,text_area_coord from headpages_style \
           WHERE ispicnews is NULL and picture_count=1 and pageid = {}".format(pageid)###通过pageid找版面信息的sql
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        dbconn.commit()
        data = cursor.fetchall()
    except:
        # 如果发生错误则回滚
        print(f'--something eror when get page titles by pageid {pageid}')
        dbconn.rollback()
    return data

#为有图新闻插入样式种类
def set_havepic_cate(dbconn,str,articleid):
    cursor = dbconn.cursor()###创建游标
    sql = "update headpages_style set style_category ='{}' WHERE article_id = {}".format(str,articleid)###通过pageid找版面信息的sql
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        dbconn.commit()
        data = cursor.fetchall()
    except error:
        # 如果发生错误则回滚
        print(f'--something error',error)
        dbconn.rollback()

#选择无图文字新闻的信息
def get_nopicnews_by_pageid(dbconn,pageid):
    cursor = dbconn.cursor()###创建游标
    sql = "select article_id,title_style,text_area_coord from headpages_style \
           WHERE picture_count=0 and pageid = {}".format(pageid)###通过pageid找版面信息的sql
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        dbconn.commit()
        data = cursor.fetchall()
    except:
        # 如果发生错误则回滚
        print(f'--something eror when get page titles by pageid {pageid}')
        dbconn.rollback()
    return data

#为无图新闻插入是否分栏的信息
def set_iscolumn(dbconn,flag,articleid):
    cursor = dbconn.cursor()###创建游标
    sql = "update headpages_style set iscolumn ='{}' WHERE article_id = {}".format(flag,articleid)###通过pageid找版面信息的sql
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        dbconn.commit()
        data = cursor.fetchall()
    except error:
        # 如果发生错误则回滚
        print(f'--something error',error)
        dbconn.rollback()

def set_nopic_cate(dbconn,str,articleid):
    cursor = dbconn.cursor()###创建游标
    sql = "update headpages_style set style_category ='{}' WHERE article_id = {}".format(str,articleid)###通过pageid找版面信息的sql
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        dbconn.commit()
        data = cursor.fetchall()
    except error:
        # 如果发生错误则回滚
        print(f'--something error',error)
        dbconn.rollback()

#通过article_id获取判断图片新闻的信息
def get_coord_by_articleid(dbconn,articleid):
    cursor = dbconn.cursor()###创建游标
    sql = "select maintitle_area_coord,picture_area_coord from headpages_style \
           WHERE article_id = {}".format(articleid)###通过pageid找版面信息的sql
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        dbconn.commit()
        data = cursor.fetchall()
    except:
        # 如果发生错误则回滚
        print(f'--something eror when get page titles by pageid {pageid}')
        dbconn.rollback()
    return data

#插入图片新闻的样式类型
def set_picnews_category(dbconn,articleid,cate_str):
    cursor = dbconn.cursor()###创建游标
    sql = "update headpages_style set style_category ='{}' WHERE article_id = {}".format(cate_str,articleid)###通过pageid找版面信息的sql
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        dbconn.commit()
        data = cursor.fetchall()
    except error:
        # 如果发生错误则回滚
        print(f'--something error',error)
        dbconn.rollback()

#通过articleid获得文章信息
def get_articleinfo_by_articleid(dbconn,articleid):
    cursor = dbconn.cursor()###创建游标
    sql = "select article_w,maintitle_charsize,text_char_count,picture_area_coord from headpages_style \
           WHERE article_id = {} and picture_count>=1;".format(articleid)###通过pageid找版面信息的sql
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        dbconn.commit()
        data = cursor.fetchall()
    except:
        # 如果发生错误则回滚
        print(f'--something eror when get page titles by pageid {pageid}')
        dbconn.rollback()
    return data

#设置是否为图片新闻
def set_is_picnews(dbconn,article_id):
    cursor = dbconn.cursor()###创建游标
    sql = "update headpages_style set ispicnews =1 WHERE article_id = {}".format(article_id)###通过pageid找版面信息的sql
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        dbconn.commit()
        data = cursor.fetchall()
    except error:
        # 如果发生错误则回滚
        print(f'--something error',error)
        dbconn.rollback()

#通过pageid获得种类为text的坐标信息
def gettextcoord_by_pageid(dbconn,pageid):
    cursor = dbconn.cursor()###创建游标
    sql = "select x_coordinate,y_coordinate,width,height from layout_elements \
           WHERE Page_id = {} and Category='text';".format(pageid)###通过pageid找版面信息的sql
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        dbconn.commit()
        data = cursor.fetchall()
    except:
        # 如果发生错误则回滚
        print(f'--something eror when get page titles by pageid {pageid}')
        dbconn.rollback()
    return data

#在headpages_style中插入text坐标
def insert_textcoord(dbconn,article_id,text_str):
    cursor = dbconn.cursor()###创建游标
    sql = "update headpages_style set text_area_coord = '{}' WHERE article_id = {}".format(text_str,article_id)###通过pageid找版面信息的sql
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        dbconn.commit()
        data = cursor.fetchall()
    except error:
        # 如果发生错误则回滚
        print(f'--something error',error)
        dbconn.rollback()
    




#设置是否为头条的字段
def set_is_headart(dbconn, pageid):
    cursor = dbconn.cursor()###创建游标
    sql = "select article_id,maintitle_charsize,title_style from headpages \
           WHERE Pageid = {};".format(pageid)###通过pageid找版面信息的sql
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        dbconn.commit()
        data = cursor.fetchall()
    except:
        # 如果发生错误则回滚
        print(f'--something eror when get page titles by pageid {pageid}')
        dbconn.rollback()
    print(data)
    data = sorted(data,key=lambda x : x[1] if x[2] else x[1]*1.5 ) #查找在一个版面下的头条
    print(data)
    art_id = data[-1][0] #头条文章id
    ################
    sql = "update headpages set ishead = {} WHERE article_id = {};".format(1,art_id)###通过pageid找版面信息的sql
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        dbconn.commit()
        data = cursor.fetchall()
    except:
        # 如果发生错误则回滚
        print(f'--something eror when get page titles by pageid {pageid}')
        dbconn.rollback()

#通过pageid获得图片的坐标信息
def get_rec_pictures_by_pageid(dbconn, pageid):
    cursor = dbconn.cursor()###创建游标
    sql = "SELECT x_coordinate,y_coordinate,width,height FROM test\
           WHERE Page_id = {} AND Category = 'figure';".format(pageid)###通过pageid找版面信息的sql
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        dbconn.commit()
        data = cursor.fetchall()
    except:
        # 如果发生错误则回滚
        print(f'--something eror when get page titles by pageid {pageid}')
        dbconn.rollback()
    return data

#通过文章id在new数据库中查找文章的具体信息（标题、正文字数等）
def get_articledata_by_articleid(dbconn, articleid):
    cursor = dbconn.cursor()###创建游标
    sql = "SELECT atitle,ftitle,ytitle,wordcount,acontent FROM news\
           WHERE id = {};".format(int(articleid))###通过pageid找版面信息的sql
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        dbconn.commit()
        data = cursor.fetchall()
    except:
        # 如果发生错误则回滚
        print(f'--something eror when get page titles by pageid {articleid}')
        dbconn.rollback()
    return data

#通过bmid获取文章id
def get_articleid_by_bmid(dbconn, bmid):
    cursor = dbconn.cursor()###创建游标
    sql = "SELECT id FROM news\
           WHERE bmid = {};".format(bmid)###通过pageid找版面信息的sql
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        dbconn.commit()
        data = cursor.fetchall()
    except:
        # 如果发生错误则回滚
        print(f'--something eror when get bmdata by pageid {bmid}')
        dbconn.rollback()
    return data

##通过图片名称获取bmid
def get_bmdata_by_jpgname(dbconn, pageid, jpgname):
    cursor = dbconn.cursor()###创建游标
    sql = "SELECT HotPic,bmid FROM bminfo\
           WHERE REPLACE(Pic,' ','') like '%{}%';".format(jpgname)###通过pageid找版面信息的sql
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        dbconn.commit()
        data = cursor.fetchall()
    except:
        # 如果发生错误则回滚
        print(f'--something eror when get bmdata by pageid {pageid}')
        dbconn.rollback()
    return data

##通过pageid获取paddleocr识别出的文章信息
def get_rec_data_by_pageid(dbconn, pageid):
    cursor = dbconn.cursor()###创建游标
    sql = "SELECT Page_name,category,Content,x_coordinate,y_coordinate,width,height FROM layout_elements\
           WHERE Page_id = {} and (category='title' or category='figure');".format(pageid)###通过pageid找版面信息的sql
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        dbconn.commit()
        data = cursor.fetchall()
    except:
        # 如果发生错误则回滚
        print(f'--something eror when get page titles by pageid {pageid}')
        dbconn.rollback()
    # print(data)
    # if not len(data):
    #     print(f"get no titles by pageid {pageid}")
    #     raise "get no titles by pageid"
    return data

##获取paddleocr识别出的标题内容
def get_rec_titles_by_pageid(dbconn, pageid):
    cursor = dbconn.cursor()###创建游标
    sql = "SELECT Content,x_coordinate,y_coordinate,width,height FROM test\
           WHERE Page_id = {} AND Category = 'title';".format(pageid)###通过pageid找版面信息的sql
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        dbconn.commit()
        data = cursor.fetchall()
    except:
        # 如果发生错误则回滚
        print(f'--something eror when get page titles by pageid {pageid}')
        dbconn.rollback()
    # print(data)
    if not len(data):
        print(f"get no titles by pageid {pageid}")
        raise "get no titles by pageid"
    return data

##根据文字检测结果获得bmid
def get_bmid_by_rec_titles(dbconn, rec_titles, pageid):
    rec_titles = [title for title in rec_titles if len(title) > 3]
    # rec_titles2 = [title[1:3] for title in rec_titles if len(title) > 3]
    # rec_titles += rec_titles2
    num_titles = len(rec_titles)
    sql = "SELECT ATitle,YTitle,FTitle,BmID FROM news WHERE REPLACE(ATitle,' ','') LIKE '%{}%'" + " or REPLACE(ATitle,' ','') LIKE '%{}%' " * (num_titles-1)
    sql = sql.format(*rec_titles) 
    print(rec_titles)
    ################
    bmidlist = pd.read_sql(sql,con=dbconn)
    print(bmidlist)
    print(bmidlist.iloc[:,3].mode())
    ################
    if len(bmidlist.iloc[:,3].mode()) > 1:
        raise f"can't get bmid bzf no same bmid with pageid: {pageid}"
    bmid=bmidlist.iloc[:,3].mode().values[0]###获得一列中最多的元素值
    ###################################
    return bmid

##已知bmid获取news中准确的电子报信息
def get_all_titles_texts_by_bmid(dbconn, bmid, pageid):
    cursor = dbconn.cursor()###创建游标
    sql = "SELECT ATitle,YTitle,FTitle,WordCount,AContent FROM news\
           WHERE BmID = {} ORDER BY CreateTime;;".format(bmid)###通过bmid找文章内容
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        dbconn.commit()
        data = cursor.fetchall()
    except:
        # 如果发生错误则回滚
        print(f'--something eror when get content by pageid {pageid} bybmid {bmid}')
        dbconn.rollback()
    return data

#通过bmid在bminfo表中寻找热区信息
def get_hotarea_by_bmid(dbconn, bmid, pageid):
    cursor = dbconn.cursor()###创建游标
    sql = "SELECT HotPic FROM bminfo\
           WHERE BmID = {};".format(bmid)###通过pageid找版面信息的sql
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        dbconn.commit()
        data = cursor.fetchall()
    except:
        # 如果发生错误则回滚
        print(f'--something eror when get hotpic by pageid {pageid} by bmid {bmid}')
        dbconn.rollback()
    return data

if __name__=="__main__":
    dbconn = pymysql.connect(host="121.196.99.106",port=3306,user="root",password="zzysky123",
            database="rawnewsdata",charset="utf8") ##连接数据库
    #data=gettextcoord_by_pageid(dbconn,1)
    #print(data)
    #insert_textcoord(dbconn,99243,'[1,2,3,6]')
    data1=get_articleinfo_by_articleid(dbconn,99245)
    print(data1[0])
    dbconn.close()
    