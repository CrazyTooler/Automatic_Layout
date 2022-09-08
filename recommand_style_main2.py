#import ps_bys
import os

from sqlalchemy.sql.expression import null
import process_docx
import numpy as np
from layout_test.style_mysql import mysqlCon
import math
import subprocess
import adjust_news
import layout_test.model_integration as lm
import layout_test.calculate_s as lc
import layout_test.get_treeconstraint as lg
import layout_test.final_ortools2 as fo
import layout_test.param_cal as lp
import time
# import frame_data
import matplotlib.pyplot as plt

current_path = os.path.abspath(__file__)#绝对路径
father_path = os.path.abspath(os.path.dirname(current_path) + os.path.sep + ".")

#print(current_path)
#print(father_path)
#新闻数据的获取
def newscont(filepath,articleid):
    #读取文件内容，获得文章类字典{key=id，value=Article()}
    result =process_docx.get_article_dic(filepath)
    ###将所有一类的数据放到一个数组中##############################
    #新闻信息列表
    title=[]
    paragraphs=[]
    count_pics=[]
    have_subtitle=[]
    count_sub_title=[]
    sub_title=[]
    pic=[]
    have_pics=[]
    para_char=[]
    count_title_char=[]
    for n in articleid:
        #result[n].set_default_size()
        #prn_obj(result[n])
        title.append(result[n].title)
        paragraphs.append(result[n].paragraphs)
        count_pics.append(result[n].count_pics)
        have_subtitle.append(result[n].have_subtitle)
        count_sub_title.append(result[n].count_sub_title)
        sub_title.append(result[n].sub_title)
        pic.append(result[n].pic)
        have_pics.append(result[n].have_pics)
        para_char.append(result[n].para_char)
        count_title_char.append(result[n].count_title_char)
    text_count_sum=0
    for i in range(len(para_char)):
        text_count_sum=text_count_sum+np.sum(para_char[i])
    return text_count_sum,title,paragraphs,count_pics,have_subtitle,count_sub_title,sub_title,pic,have_pics,para_char,count_title_char

def get_rframe(frame):
    rframe=[]
    temp2=[]
    for i in range(len(frame)):
        for j in range(len(frame[i])-2):
            a=[float(b)*0.01 for b in frame[i][j][0:4]]
            temp2.append(a)
        rframe.append(temp2)
        temp2=[]
    return rframe

#从数据库中根据推荐样式类别选择基础样式
def selectstyle(style_list):
    sqlcon=mysqlCon()
    sql="select id,name,texcode,colnum,title_style,description from style_3 where category='%s'"%(style_list)
    rets=sqlcon.select(sql)
    return rets

#插入布局数据
def handleFrame(framedata,texdata):
    frame_count=len(framedata)
    newstaticframe=''
    newenv=''
    #将数据插入newstatic语句中
    newstaticframe=r"\newflowframe[1]{%f\textwidth}{%f\textheight}{%f\textwidth}{%f\textheight}"%(framedata[0][2],framedata[0][3],framedata[0][0],framedata[0][1])+'\n'
    #newenv=r""+'\n'
    for i in range(1,frame_count):
        f1=r"\newstaticframe[1]{%f\textwidth}{%f\textheight}{%f\textwidth}{%f\textheight}[statico%d]"%(framedata[i][2],framedata[i][3],framedata[i][0],framedata[i][1],i)
        f2=r"\begin{staticcontents*}{statico%d}\begin{mytcbox1}[width=\textwidth,height=%f\textheight]%%framestyle%d"%(i,framedata[i][3],i)+'\n'+r"\end{mytcbox1}\end{staticcontents*}"
        newstaticframe=newstaticframe+f1+'\n'
        newenv=newenv+f2+'\n'
        f1=''
        f2=''
    #在Tex文件中插入布局语句与环境
    rettexf=texdata.replace('%framelocation',newstaticframe).replace('%mainframe',newenv)
    return rettexf

#插入样式
def handleStyle(style,texdata,articlecount):
    #sty=[]
    #print("*****sty*",style)
    '''
    for i in range(len(style)):
        s1=style[i][0].replace('#','\n')
        sty.append('\n'+s1+'\n')
        '''
    #print("**********:",sty)
    for i in range(1,articlecount+1):
        rettexs=texdata.replace('%%framestyle%d'%(i),style[i-1])
        texdata=rettexs
    return rettexs

def calcu_s(style_cat,style,bw,bh,bx,have_subtitle,count_subtitle,sub_title,para_char,count_title_char,pic_count,pic,ischangeline,title):
    if style_cat=='ht_np_nc':
        S,pstyle=lc.ht_np_nc(style,bw,have_subtitle,count_subtitle,sub_title,para_char,count_title_char,ischangeline)
    if style_cat=='ht_np_c':
        S,pstyle=lc.ht_np_c(style,bw,have_subtitle,count_subtitle,sub_title,para_char,count_title_char,40,ischangeline)
    if style_cat=='vwt_np_nc':
        S,pstyle=lc.vwt_np_nc(style,bw,bh,bx,have_subtitle,count_subtitle,sub_title,count_title_char,para_char,title)
    if style_cat=='picnews_vertical':
        S,pstyle=lc.picnews_vertical_nc(style,bw,bh,pic_count,pic)
    if style_cat=='picnews_horizontal':
        S,pstyle=lc.picnews_ht_horizontal_nc(style,bw,bh,pic_count,pic,para_char,title)
    if style_cat=='ht_tp_nc' or style_cat=='ht_bp_nc':
        S,pstyle=lc.ht_tbp_nc(style,bw,bh,have_subtitle,count_subtitle,sub_title,para_char,count_title_char,pic_count,pic,ischangeline)
    if style_cat=='ht_tp_c' or style_cat=='ht_bp_c':
        S,pstyle=lc.ht_tbp_c(style,bw,have_subtitle,count_subtitle,sub_title,para_char,count_title_char,pic_count,pic,40,ischangeline)
    if style_cat=='ht_ltcp_c' or style_cat=='ht_rbcp_c':
        S,pstyle=lc.ht_tbcp_c(style,bw,have_subtitle,count_subtitle,sub_title,para_char,count_title_char,pic_count,pic,ischangeline)
    return S,pstyle

#命令行
def cmd(command):
    subp = subprocess.Popen(command,shell=True)#如果把shell设置成True，指定的命令会在shell里解释执行。
    subp.wait()#同步执行

def visulizeThePage(page):
    """page结构图"""
    fig,ax=plt.subplots()
    plt.axis('equal')
    ax.xaxis.set_ticks_position('top')
    ax.invert_yaxis()
    ######
    c = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
    l = [1,5,9,13,17,21,25]
    for rec in page:
         x = [rec[0], rec[0]+rec[2], rec[0]+rec[2], rec[0], rec[0]]
         y = [rec[1], rec[1], rec[1]+rec[3], rec[1]+rec[3], rec[1]]
         plt.plot(x,y,color = c.pop(), alpha = 0.5, linewidth=l.pop())
         ######
    plt.show()

def main(frame):
    start = time.time()
    #print(title)
    #纸张高度
    width=32.0
    height=49.75 #单位为cm
    #frame=[[[0, 83, 100, 17], [0, 48, 70, 35], [0, 24, 70, 24], [0, 0, 28, 24], [28, 0, 42, 24], [70, 38, 30, 45], [70, 0, 30, 38], (1, 2, 4, 6, 3, 5)], [[0, 83, 100, 17], [0, 48, 70, 35], [0, 24, 70, 24], [0, 0, 28, 24], [28, 0, 42, 24], [70, 44, 30, 39], [70, 0, 30, 44], (1, 2, 4, 6, 5, 3)] ,[[0, 83, 100, 17], [0, 48, 70, 35], [0, 24, 70, 24], [0, 0, 44, 24], [44, 0, 26, 24], [70, 38, 30, 45], [70, 0, 30, 38], (1, 2, 6, 4, 3, 5)] ,[[0, 83, 100, 17], [0, 48, 70, 35], [0, 26, 70, 22], [0, 0, 25, 26], [25, 0, 45, 26], [70, 32, 30, 51], [70, 0, 30, 32], (1, 3, 4, 5, 2, 6)] ,[[0, 83, 100, 17], [0, 48, 70, 35], [0, 24, 70, 24], [0, 0, 44, 24], [44, 0, 26, 24], [70, 44, 30, 39], [70, 0, 30, 44], (1, 2, 6, 4, 5, 3)] ,[[0, 83, 100, 17], [0, 48, 70, 35], [0, 31, 70, 17], [0, 0, 49, 31], [49, 0, 21, 31], [70, 32, 30, 51], [70, 0, 30, 32], (1, 5, 3, 4, 2, 6)] ,[[0, 83, 100, 17], [0, 48, 70, 35], [0, 36, 70, 12], [0, 0, 52, 36], [52, 0, 18, 36], [70, 38, 30, 45], [70, 0, 30, 38], (1, 6, 2, 4, 3, 5)] ,[[0, 83, 100, 17], [0, 48, 70, 35], [0, 31, 70, 17], [0, 0, 19, 31], [19, 0, 51, 31], [70, 32, 30, 51], [70, 0, 30, 32], (1, 5, 4, 3, 2, 6)] ,[[0, 83, 100, 17], [0, 48, 70, 35], [0, 26, 70, 22], [0, 0, 47, 26], [47, 0, 23, 26], [70, 32, 30, 51], [70, 0, 30, 32], (1, 3, 5, 4, 2, 6)] ,[[0, 83, 100, 17], [0, 48, 70, 35], [0, 36, 70, 12], [0, 0, 37, 36], [37, 0, 33, 36], [70, 20, 30, 63], [70, 0, 30, 20], (1, 6, 3, 5, 2, 4)] ,[[0, 83, 100, 17], [0, 48, 70, 35], [0, 36, 70, 12], [0, 0, 17, 36], [17, 0, 53, 36], [70, 38, 30, 45], [70, 0, 30, 38], (1, 6, 4, 2, 3, 5)] ,[[0, 83, 100, 17], [0, 48, 70, 35], [0, 36, 70, 12], [0, 0, 52, 36], [52, 0, 18, 36], [70, 44, 30, 39], [70, 0, 30, 44], (1, 6, 2, 4, 5, 3)] ,[[0, 83, 100, 17], [0, 48, 70, 35], [0, 36, 70, 12], [0, 0, 33, 36], [33, 0, 37, 36], [70, 20, 30, 63], [70, 0, 30, 20], (1, 6, 5, 3, 2, 4)] ,[[0, 83, 100, 17], [0, 48, 70, 35], [0, 14, 51, 34], [51, 14, 19, 34], [0, 0, 70, 14], [70, 44, 30, 39], [70, 0, 30, 44], (1, 2, 4, 6, 5, 3)]]
    # fret_=frame_data.framedata('./testdocx/jh2.docx')
    # frame=fret_[0]
    #frame= [[[0.0, 83.0, 100.0, 17.0, 21, 0, 0, 0, 0], [0.0, 52.35, 72.31875, 30.65, 54, 1, 1, 1, 1], [0.0, 15.810000000000002, 45.409375, 36.54, 50, 0, 0, 0, 1], [45.409375, 15.810000000000002, 26.909375, 36.54, 38, 1, 0, 0, 0], [0.0, 1.7763568394002505e-15, 72.31875, 15.81, 30, 1, 0, 0, 1], [72.31875, 27.692, 27.68125, 55.308, 50, 1, 0, 0, 0], [72.31875, -7.105427357601002e-15, 27.68125, 27.692, 34, 0, 0, 0, 1], (1, 2, 4, 6, 3, 5), 2.0], [[0.0, 83.0, 100.0, 17.0, 21, 0, 0, 0, 0], [0.0, 51.464, 72.465625, 31.536, 52, 1, 1, 1, 1], [0.0, 29.674, 72.465625, 21.79, 48, 1, 1, 0, 1], [72.465625, 29.674, 27.534375, 53.326, 48, 1, 0, 0, 0], [0.0, 13.460000000000008, 53.9375, 16.214, 30, 1, 0, 0, 1], [53.9375, 13.460000000000008, 46.0625, 16.214, 35, 1, 0, 0, 1], [0.0, -7.105427357601002e-15, 100.0, 13.46, 44, 1, 0, 0, 1], (1, 2, 3, 6, 5, 4), 2.0], [[0.0, 83.0, 100.0, 17.0, 21, 0, 0, 0, 0], [0.0, 52.488, 70.15625, 30.512, 52, 1, 1, 1, 1], [0.0, 31.599999999999998, 70.15625, 20.888, 48, 1, 1, 0, 1], [70.15625, 31.6, 29.84375, 51.4, 48, 0, 0, 0, 0], [0.0, 14.679999999999993, 44.03125, 16.92, 34, 1, 0, 0, 1], [44.03125, 14.679999999999993, 55.96875, 16.92, 30, 1, 0, 0, 1], [0.0, 7.105427357601002e-15, 100.0, 14.68, 44, 1, 0, 0, 1], (1, 3, 2, 5, 6, 4), 2.0], [[0.0, 83.0, 100.0, 17.0, 21, 0, 0, 0, 0], [0.0, 52.7, 69.78125, 30.3, 49, 1, 1, 1, 1], [0.0, 34.900000000000006, 69.78125, 17.8, 30, 1, 0, 0, 1], [69.78125, 34.9, 30.21875, 48.1, 43, 0, 0, 0, 0], [0.0, 11.330000000000005, 43.503125, 23.57, 38, 1, 0, 0, 1], [43.503125, 11.330000000000005, 56.496875, 23.57, 43, 1, 1, 0, 1], [0.0, -1.7763568394002505e-15, 100.0, 11.33, 34, 1, 0, 0, 1], (1, 6, 2, 4, 3, 5), 2.0], [[0.0, 83.0, 100.0, 17.0, 21, 0, 0, 0, 0], [0.0, 52.536, 72.465625, 30.464, 51, 1, 1, 1, 1], [0.0, 16.046, 27.71875, 36.49, 41, 0, 0, 0, 0], [27.71875, 16.046, 44.746875, 36.49, 47, 0, 0, 0, 1], [0.0, 7.105427357601002e-15, 72.465625, 16.046, 30, 1, 0, 0, 1], [72.465625, 29.276000000000003, 27.534375, 53.724, 47, 1, 0, 0, 0], [72.465625, -3.552713678800501e-15, 27.534375, 29.276, 37, 0, 0, 0, 1], (1, 4, 2, 6, 3, 5), 2.0], [[0.0, 83.0, 100.0, 17.0, 21, 0, 0, 0, 0], [0.0, 52.908, 71.309375, 30.092, 46, 1, 1, 1, 1], [0.0, 37.492000000000004, 71.309375, 15.416, 30, 1, 0, 0, 1], [71.309375, 37.492, 28.690625, 45.508, 42, 0, 0, 0, 0], [0.0, 10.303999999999998, 59.471875, 27.188, 42, 1, 0, 0, 1], [59.471875, 10.303999999999998, 40.528125, 27.188, 38, 0, 0, 0, 1], [0.0, 1.7763568394002505e-15, 100.0, 10.304, 34, 1, 0, 0, 1], (1, 6, 3, 2, 4, 5), 1.0], [[0.0, 83.0, 100.0, 17.0, 21, 0, 0, 0, 0], [0.0, 53.54, 72.46875, 29.46, 50, 1, 1, 1, 1], [0.0, 38.16, 72.46875, 15.38, 38, 1, 0, 0, 1], [72.46875, 38.16, 27.53125, 44.84, 46, 0, 1, 0, 0], [0.0, 9.999999999999996, 60.446875, 28.16, 46, 1, 0, 0, 1], [60.446875, 9.999999999999996, 39.553125, 28.16, 30, 1, 0, 0, 1], [0.0, 0.0, 100.0, 10.0, 34, 1, 0, 0, 1], (1, 4, 3, 2, 6, 5), 1.0], [[0.0, 83.0, 100.0, 17.0, 21, 0, 0, 0, 0], [0.0, 52.91, 69.140625, 30.09, 46, 1, 1, 1, 1], [0.0, 34.268, 69.140625, 18.642, 30, 1, 0, 0, 1], [69.140625, 34.268, 30.859375, 48.732, 42, 0, 0, 0, 0], [0.0, 10.168, 55.378125, 24.1, 42, 1, 1, 0, 1], [55.378125, 10.168, 44.621875, 24.1, 38, 1, 0, 0, 1], [0.0, 7.105427357601002e-15, 100.0, 10.168, 34, 1, 0, 0, 1], (1, 6, 2, 3, 4, 5), 2.0], [[0.0, 83.0, 100.0, 17.0, 21, 0, 0, 0, 0], [0.0, 51.238, 72.984375, 31.762, 55, 1, 1, 1, 1], [0.0, 29.308, 72.984375, 21.93, 50, 1, 1, 0, 1], [72.984375, 29.308, 27.015625, 53.692, 50, 1, 0, 0, 0], [0.0, 13.210000000000008, 45.73125, 16.098, 35, 1, 0, 0, 1], [45.73125, 13.210000000000008, 54.26875, 16.098, 30, 1, 0, 0, 1], [0.0, -7.105427357601002e-15, 100.0, 13.21, 46, 1, 0, 0, 1], (1, 2, 3, 5, 6, 4), 2.0], [[0.0, 83.0, 100.0, 17.0, 21, 0, 0, 0, 0], [0.0, 52.91, 69.140625, 30.09, 46, 1, 1, 1, 1], [0.0, 35.769999999999996, 69.140625, 17.14, 30, 1, 0, 0, 1], [69.140625, 35.77, 30.859375, 47.23, 42, 0, 0, 0, 0], [0.0, 13.489999999999995, 61.315625, 22.28, 42, 1, 1, 0, 1], [61.315625, 13.489999999999995, 38.684375, 22.28, 34, 0, 0, 0, 1], [0.0, -5.329070518200751e-15, 100.0, 13.49, 38, 1, 0, 0, 1], (1, 6, 2, 3, 5, 4), 2.0], [[0.0, 83.0, 100.0, 17.0, 21, 0, 0, 0, 0], [0.0, 53.19, 73.06875, 29.81, 55, 1, 1, 1, 1], [0.0, 31.209999999999997, 73.06875, 21.98, 50, 1, 1, 0, 1], [0.0, 15.379999999999994, 73.06875, 15.83, 30, 1, 0, 0, 1], [0.0, -5.329070518200751e-15, 73.06875, 15.38, 38, 1, 0, 0, 1], [73.06875, 30.234, 26.93125, 52.766, 50, 1, 0, 0, 0], [73.06875, -7.105427357601002e-15, 26.93125, 30.234, 34, 0, 0, 0, 1], (1, 2, 6, 4, 3, 5), 2.0], [[0.0, 83.0, 100.0, 17.0, 21, 0, 0, 0, 0], [0.0, 53.260000000000005, 72.784375, 29.74, 54, 1, 1, 1, 1], [0.0, 37.571999999999996, 72.784375, 15.688, 30, 1, 0, 0, 1], [0.0, 15.520000000000003, 72.784375, 22.052, 50, 1, 1, 0, 1], [0.0, -3.552713678800501e-15, 72.784375, 15.52, 40, 1, 0, 0, 1], [72.784375, 29.718000000000004, 27.215625, 53.282, 50, 0, 0, 0, 0], [72.784375, 3.552713678800501e-15, 27.215625, 29.718, 36, 0, 0, 0, 1], (1, 6, 2, 4, 3, 5), 2.0], [[0.0, 83.0, 100.0, 17.0, 21, 0, 0, 0, 0], [0.0, 53.61, 73.0875, 29.39, 49, 1, 1, 1, 1], [0.0, 32.03, 73.0875, 21.58, 45, 1, 1, 0, 1], [0.0, 16.65, 73.0875, 15.38, 38, 1, 0, 0, 1], [0.0, 7.105427357601002e-15, 73.0875, 16.65, 30, 1, 0, 0, 1], [73.0875, 30.4, 26.9125, 52.6, 45, 1, 0, 0, 0], [73.0875, 7.105427357601002e-15, 26.9125, 30.4, 34, 0, 0, 0, 1], (1, 2, 4, 6, 3, 5), 2.0], [[0.0, 83.0, 100.0, 17.0, 21, 0, 0, 0, 0], [0.0, 53.328, 72.6375, 29.672, 53, 1, 1, 1, 1], [0.0, 37.668000000000006, 72.6375, 15.66, 39, 1, 0, 0, 1], [0.0, 15.762, 72.6375, 21.906, 49, 1, 1, 0, 1], [0.0, 0.0, 72.6375, 15.762, 30, 1, 0, 0, 1], [72.6375, 30.008000000000003, 27.3625, 52.992, 49, 1, 0, 0, 0], [72.6375, -3.552713678800501e-15, 27.3625, 30.008, 35, 0, 0, 0, 1], (1, 4, 2, 6, 3, 5), 2.0], [[0.0, 83.0, 100.0, 17.0, 21, 0, 0, 0, 0], [0.0, 52.864000000000004, 72.91875, 30.136, 59, 1, 1, 1, 1], [0.0, 30.895999999999997, 72.91875, 21.968, 49, 1, 1, 0, 1], [0.0, 0.0, 36.4625, 30.896, 30, 1, 0, 0, 1], [36.4625, 0.0, 36.45625, 30.896, 45, 0, 0, 0, 1], [72.91875, 30.9, 27.08125, 52.1, 49, 0, 0, 0, 0], [72.91875, 7.105427357601002e-15, 27.08125, 30.9, 39, 0, 0, 0, 1], (1, 2, 6, 4, 3, 5), 2.0], [[0.0, 83.0, 100.0, 17.0, 21, 0, 0, 0, 0], [0.0, 52.488, 70.903125, 30.512, 52, 1, 1, 1, 1], [0.0, 29.99, 70.903125, 22.498, 48, 1, 1, 0, 1], [70.903125, 29.990000000000002, 29.096875, 53.01, 48, 0, 0, 0, 0], [0.0, 13.069999999999993, 55.96875, 16.92, 30, 1, 0, 0, 1], [55.96875, 13.069999999999993, 44.03125, 16.92, 34, 1, 0, 0, 1], [0.0, -7.105427357601002e-15, 100.0, 13.07, 44, 1, 0, 0, 1], (1, 3, 2, 6, 5, 4), 2.0], [[0.0, 83.0, 100.0, 17.0, 21, 0, 0, 0, 0], [0.0, 52.980000000000004, 73.125, 30.02, 58, 1, 1, 1, 1], [0.0, 30.763999999999996, 73.125, 22.216, 54, 1, 1, 0, 1], [0.0, -3.552713678800501e-15, 36.45625, 30.764, 38, 0, 0, 0, 1], [36.45625, -3.552713678800501e-15, 36.66875, 30.764, 30, 1, 0, 0, 1], [73.125, 29.134, 26.875, 53.866, 54, 1, 1, 0, 0], [73.125, 0.0, 26.875, 29.134, 34, 0, 0, 0, 1], (1, 2, 4, 6, 3, 5), 2.0], [[0.0, 83.0, 100.0, 17.0, 21, 0, 0, 0, 0], [0.0, 53.05, 72.46875, 29.95, 57, 1, 1, 1, 1], [0.0, 37.33, 72.46875, 15.72, 30, 1, 0, 0, 1], [0.0, 0.0, 43.08125, 37.33, 53, 0, 0, 0, 1], [43.08125, 0.0, 29.3875, 37.33, 45, 0, 0, 0, 1], [72.46875, 29.96, 27.53125, 53.04, 53, 1, 1, 0, 0], [72.46875, -7.105427357601002e-15, 27.53125, 29.96, 40, 0, 0, 0, 1], (1, 6, 2, 4, 3, 5), 2.0], [[0.0, 83.0, 100.0, 17.0, 21, 0, 0, 0, 0], [0.0, 53.328, 72.94375, 29.672, 53, 1, 1, 1, 1], [0.0, 0.0, 30.43125, 53.328, 49, 0, 0, 0, 0], [30.43125, 26.650000000000002, 42.5125, 26.678, 30, 1, 0, 0, 1], [30.43125, 7.105427357601002e-15, 42.5125, 26.65, 41, 0, 0, 0, 1], [72.94375, 28.884, 27.05625, 54.116, 49, 0, 0, 0, 0], [72.94375, 0.0, 27.05625, 28.884, 37, 0, 0, 0, 1], (1, 2, 6, 4, 3, 5), 2.0], [[0.0, 83.0, 100.0, 17.0, 21, 0, 0, 0, 0], [0.0, 50.244, 72.01875, 32.756, 60, 1, 1, 1, 1], [0.0, 0.0, 25.453125, 50.244, 50, 0, 0, 0, 0], [25.453125, 13.369999999999997, 46.565625, 36.874, 55, 0, 0, 0, 1], [25.453125, 5.329070518200751e-15, 46.565625, 13.37, 30, 1, 0, 0, 1], [72.01875, 28.61, 27.98125, 54.39, 55, 1, 0, 0, 0], [72.01875, 0.0, 27.98125, 28.61, 41, 0, 0, 0, 1], (1, 4, 2, 6, 3, 5), 1.0], [[0.0, 83.0, 100.0, 17.0, 21, 0, 0, 0, 0], [0.0, 53.117999999999995, 72.46875, 29.882, 56, 1, 1, 1, 1], [0.0, 0.0, 30.409375, 53.118, 52, 0, 0, 0, 0], [30.409375, 29.204, 42.059375, 23.914, 39, 1, 0, 0, 1], [30.409375, -7.105427357601002e-15, 42.059375, 29.204, 30, 1, 0, 0, 1], [72.46875, 28.616, 27.53125, 54.384, 52, 1, 0, 0, 0], [72.46875, 0.0, 27.53125, 28.616, 34, 0, 0, 0, 1], (1, 2, 4, 6, 3, 5), 2.0]]
    #frame=[frame[1]]
    rframe=get_rframe(frame)  #获得布局数据
    '''
    for page in rframe:
        visulizeThePage(page)
    '''
    # print(rframe)
    # print('布局长度：',len(rframe[0]))
    rframe1=rframe
    #sumS=width*(0.83*height)*100
    sumS=0
    paper_bh=height*10*0.83

    #weights=[[1,5,2,4,6,3],[1,5,2,3,6,4],[1,5,2,4,6,3],[1,5,2,3,6,4]]  #这里设定图片新闻的新闻块号放在最后面
    for i in range(len(frame)):#布局结构数
    #for i in range(5):#布局结构数
        sum_bw=[]
        sum_bh=[]
        sum_bx=[]
        sum_label=[]
        sum_texcode=[]
        sum_data=[]
        sum_init_column=[] #栏数集合
        sum_S=[]  #文章实际面积集合
        ################################################
        news_block_S=[] #新闻块面积集合
        bh_dict=adjust_news.read_image.main() #获得报花图片的所有信息

        article_num=len(frame[i][-2])
        #print(article_num)
        
        #ispicnews=[0,0,1,0,0,0]
        ispicnews=np.zeros(article_num) #1表示该区块为图片新闻，0相反

        for b in range(article_num):
            if frame[i][-2][b]==article_num:  #指定文章号为4的为图片新闻
                ispicnews[b]=1 
        # print('ispicnews：',ispicnews)
        # print('顺序',frame[i][-2])
        #获得整个版面字号范围组合
        text_count_sum,title,paragraphs,count_pics,have_subtitle,count_sub_title,sub_title,pic,have_pics,para_char,count_title_char\
        =newscont('./testdocx/jh2.docx',frame[i][-2])
        # print("区块权重：",weights)
        #print(ft)

        for j in range(article_num): #文章篇数
            #########预测样式#############################
            #输入的特征
            #注意要预测的坐标系与历史数据坐标的转换(以左下角为原点的左下角点->以左上角为原点的左上角点)
            xtest=[[math.floor(frame[i][j+1][0]*0.01*width),math.floor(height-(frame[i][j+1][1]*0.01*height+frame[i][j+1][3]*0.01*height)),math.floor(frame[i][j+1][2]*0.01*width)]]
            label=lm.nb_model(count_pics[j],ispicnews[j],xtest)
            # print('label:',label)
            sum_label.append(label)
            #########获取初始样式并计算面积##################################
            data=selectstyle(str(label)) 
            sum_data.append(data[0])
            texcode=data[0][2].replace('#','\n') #样式latex语句
            sum_texcode.append(texcode)
            #print('原始样式：',texcode)
            colnum=int(data[0][3])#原始样式列数
            sum_init_column.append(colnum)
            bw=(frame[i][j+1][2]*3.2)-10 #减去左右间距，单位mm
            sum_bw.append(bw)
            bh=(frame[i][j+1][3]*4.975)
            sum_bh.append(bh)
            sum_bx.append(frame[i][j+1][0])
            sumS=sumS+bw*bh
        weights,ft=lm.get_ft_combination(article_num,frame[i][1:article_num+1],width,height,count_title_char,para_char,text_count_sum,count_sub_title,ispicnews,sum_label)
        dict={}  #字典记录对应字号已经计算过的面积
        s_list=[]
        for k in range(len(ft)):
            sum_column_num=[]
            sum_style=[]
            sum_final_S=[]

            # print(ft[k]) #字号组合
            S=lm.get_s_combination(sum_label,sum_data,sum_texcode,sum_init_column,sum_bw,sum_bh,count_sub_title,sub_title,para_char,count_title_char,count_pics,pic,title,ft[k],dict)
            # print(S)
            #####自定义报花插入######
            #S=S+bh
            ######
            #s_temp=[int(round(((S[a]*rframe1[i][a+1][2]*100000)/(sum_bw[a]*height)))) for a in range(len(S))] #可以在这加点留白区域
            s_temp=[int(round((((S[a]/sum_bw[a])+0)/(height*10))*1000*(rframe1[i][a+1][2]*1000))) for a in range(len(S))]#留白
            s_temp.insert(0,170000) #加入报头面积
            s_list.append(s_temp)
            '''
            isvalid=lg.pagesolver(frame_construct[0],S,sumS,paper_bh,sum_bw)#判断参数是否有效,paper_bh为减去报头的高度
            print(isvalid)
            if not isvalid: #若参数无效则不进行布局生成
                continue
            '''
        #print(s_list)
        ret,index=fo.solver_layout(rframe1[i],s_list)
        # print(ret,index)
        if ret==null:
            print('该布局下无解')
            continue
        
        ###################生成布局###############################################
        for j in range(article_num):
            st=''
            for b in range(len(paragraphs[j])):
                st=st+paragraphs[j][b].replace('%','\%')+'\\par '  #特殊字符需要转义
            #contents.append(st)
            contents=st   #获得加上分段符和处理特殊字符后的正文字符串 

            #将参数插入每个新闻块的基础样式中
            if sum_data[j][4]=="horizontal":
                title_style=0
            elif sum_data[j][4]=="vertical":
                title_style=1
            a,b,temp1,temp2,flag=lm.cal_style_param(sum_bw[j],sum_init_column[j],sum_texcode[j],ft[index][j],count_title_char[j],title_style,count_sub_title[j],para_char[j])   
            S,pstyle=calcu_s(sum_label[j],temp2,sum_bw[j],sum_bh[j],sum_bx[j],have_subtitle[j],count_sub_title[j],sub_title[j],para_char[j],count_title_char[j],count_pics[j],pic[j],flag,title[j])
            #print(pstyle)
            if flag==1 and sum_label[j]!='vwt_np_nc':  #横标题样式换行操作（竖标题换行在面积计算里）
                pstyle=lc.ht_changeline(pstyle,title[j]) #横标题换行
            pstyle=pstyle.replace('*s1',sub_title[j][0]).replace('*mt',title[j]).replace('*s2',sub_title[j][1]).replace('*mc',r'\setlength{\parindent}{2em}'+contents) #插入内容
            ########插入报花图片进行微调############################
            eh=(sum_bw[j]*ret[j+1][3]*height*10-S)/sum_bw[j]    #计算留白高度
            if eh>13 and ispicnews[j]==0:
                selpic,insert_str=adjust_news.insert_bh(sum_bw[j],eh,bh_dict)
                pstyle=pstyle+insert_str #即在文章尾部插入
                del bh_dict[selpic]  #可以使用used数组记录报花的使用情况
            if ispicnews[j]==1 and eh>4.55:
                pstyle=lp.change_pic_size(pstyle,eh-4.55,pic[j])  
            #########end#####################
            #print(new_style) #输出加入推荐样式参数的样式code
            sum_style.append(pstyle)
            sum_final_S.append(S)
            news_block_S.append(sum_bw[j]*ret[j+1][3]*height*10) #新闻块方框的面积
            #print(sum_style)
        # print("____________%dframe______________________________________________________________________"%(i))      
        # print(rframe1[i])
        # print('S:',sum_final_S)  #单位为毫米的平方
        # print('news_bloch_s:',news_block_S)
        # print('字号组合：',ft[index])
        # print('比例面积组合：',s_list[index])

        ##############计算留白面积#####################################
        #即新闻块与文章面积的差值(可以给个误差范围，+-3mm)
        eh=[(news_block_S[a]-sum_final_S[a])/sum_bw[a] for a in range(len(sum_final_S))] #留白高度(普遍大于真实高度，可以给个误差)
        # print('eh:',eh)

        ############布局的合成，生成pdf文件#############################
        f = open(father_path+'/prototype.tex',mode='r',encoding='utf-8')
        tex = f.read()
        f.close()
        texf=handleFrame(ret,tex) #在样式模板中加入布局元素
        texex=handleStyle(sum_style,texf,len(rframe1[i])-1)
        ###############################################-------------------------------------
        k = int(''.join([str(c) for c in np.random.randint(0,10,6)]))
        f = open(father_path+'/page'+'/tex%s.tex'%(k),mode='w',encoding='utf-8')
        f.write(texex)
        f.close()
    
        cmd('xelatex -halt-on-error -output-directory %s %s' % (father_path+'/page/' ,father_path+'/page'+'/tex%s.tex'%(k)))#利用命令行运行tex文件
        texex=''
        texf=''
        #break
    end = time.time()
    print('运行时间：',end-start)
    ###############################copy picture

if __name__=="__main__":
    main()