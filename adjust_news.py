import numpy as np                                                                                                                                                                                                                                                                                                                                                                              
from ortools.sat.python import cp_model
import read_image
import math
import re
from PIL import Image

#根据布局数据(一个二维数组)和该区域的留白高度确定需要微调的新闻区块
def no_adjust(framedata,eh):
    nasty_id=[] #记录不需要微调的区块号
    for i in range(len(framedata)):
        for j in range(len(eh[i])):
            if framedata[i][1]!=0 and eh[i][j]<7: #y坐标为0时
                styid=np.array([i,j]) 
                nasty_id.append(styid)
    #print(nasty_id)
    return nasty_id

#判断该区块是否需要微调,返回bool值
def bool_adjust(frame_id,nasty_id):
    fi=np.array(frame_id)
    for k in nasty_id: #循环判断[i,j]是否在index中
            if np.all(fi==k):
                return True
    return False

#修改主标题字号
def weight_fs(weight,style):
    main_title_command = re.search(r"(?<=maintitle\n).*",style)
    old_title_command = main_title_command.group()
    #print(old_title_command)
    mtfs=re.findall(r'\d+',old_title_command)[0] #获取主标题字号
    #print(mtfs)
    retfs=''
    if weight == 2:
        fs2=re.sub(r'\d+','36',old_title_command,1) #二头条
        retfs=style.replace(old_title_command,fs2)
        #print(retfs)
    elif weight== 3:
        fs3=re.sub(r'\d+','25',old_title_command,1)#三头条
        retfs=style.replace(old_title_command,fs3)
    elif weight==1:
        retfs=style
    return retfs

#根据布局数据的特点增加线框
def addline(framedata,style):
     for i in range(len(framedata)):
        if framedata[i][3]>50:
            #str=r'\begin{staticcontents*}{statico\d}'%(i+1)
            t=re.search(r"\begin{staticcontents",style)
            print(t)
            t1=t.group()
            print(t1)

#用户选择相关文章自定义插入报花(图片为用户上传的形式)
def insertbh_by_self(article_id,pic_path,pic_w):
    im = Image.open(pic_path)#返回一个Image对象
    #图片尺寸大小单位转化：实际尺寸(英寸)=像素/分辨率; 1英寸=2.54厘米
    idpi=im.info['dpi'][0]#图片分辨率
    iw=(im.size[0]/idpi)*25.4#图片宽度(mm)
    ih=(im.size[1]/idpi)*25.4#图片高度(mm)
    pic_h=(ih*pic_w)/iw #根据图片原比例调整的报花高度
    #间距的设置
    insert_str='\\vspace{%fmm}\n\\includegraphics[width=%fmm,height=%fmm]{%s}\\par'%(3,pic_w,pic_h,pic_path) #报花插入语句
    #根据文章号找出样式语句并插入
    
    return insert_str


#插入报花图片(根据留白高度自动选择插入)
def insert_bh(pw,eh,bh_dict):
    phlist=[]
    min_sub=999
    for i in range(len(bh_dict)):
        w=bh_dict[i]['width']
        h=bh_dict[i]['height']
        ph=(h/w)*pw   #按比例调整后的报花宽度
        phlist.append(ph)
        ts=abs(eh-ph)
        if ts<min_sub:
            min_sub=ts
            select_pic=i #记录高度与留白高度差值最小的图片下标
    pic_name=bh_dict[select_pic]['name']
    insert_str='\\vspace{%fmm}\n\\includegraphics[width=%fmm,height=%fmm]{./bh_image/%s.png}\\par'%(3,pw,eh-3,pic_name) #报花插入语句
    return select_pic,insert_str


if __name__=='__main__':
    bh_dict=read_image.main()
    print(bh_dict)
    a,b=insert_bh(62,40,bh_dict)
    print(a,b)
    #ret=no_adjust([[0,0,33,83], [33,58,67,25], [33,34,67,24], [33,0,67,34]],[[128.54999999999998, 128.54999999999998, 51.54999999999997, 51.54999999999997, 128.54999999999998, 128.54999999999998, 145.64999999999998, 145.64999999999998, 145.64999999999998, 145.64999999999998, 158.04240523588763, 158.04240523588763, 141.1, 5.9999], [1.6499999999999968, 1.6499999999999968], [5.999999999999992, 5.999999999999992, 1.4499999999999984, 1.4499999999999984], [37.699999999999996, 42.25, 42.25, 37.699999999999996, 50.75000000000001, 50.75000000000001, 50.75000000000001, 50.75000000000001, 50.75000000000001, 50.75000000000001, 50.75000000000001, 50.75000000000001]])
    #print(ret[0][0],ret[0][1])
    #str=r'\begin{staticcontents*}{statico4}\begin{mytcbox1}[width=\textwidth,height=0.570000\textheight,leftrule=1pt,colframe=mygrey]'
    #addline([[0,0,33,83], [33,58,67,25], [33,34,67,24], [33,0,67,34]],str)