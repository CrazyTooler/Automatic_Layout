import numpy as np
import math
import re

from pymysql import NULL
import layout_test.style_final as ls
import layout_test.param_cal as lp

#横标题换行
def ht_changeline(style,title):#在标题换行处加入换行符号
    sep_pos=len(title)//2
    title=title[0:sep_pos]+"\\\\"+title[sep_pos::]
    pattern1=r"(?<=\\shortstack\[c\]\{).*(?=\})"#找到正文的字号与行距
    style=style.replace('*mt',title)
    #print(style)
    return style

#垂直标题换行
def vt_changeline(style,title):
    sep_pos=len(title)//2
    t1=''
    t2=''
    for t in range(len(title[0:sep_pos])-1):
        t1=t1+title[t]+'\\\\'
    tt1=t1+title[sep_pos-1]   #垂直标题的换行操作
    for t in range(len(title[sep_pos::])-1):
        t2=t2+title[t+sep_pos]+'\\\\'
    tt2=t2+title[-1]   #垂直标题的换行操作
    
    style=style.replace('*mt1',tt1)
    style=style.replace('*mt2',tt2)
    #print(style)
    return style

#图片的处理
def fullhpic(style,bw,pic_count,pic,picarea_id):
    #初步确定图片宽高                                                                                                                                                                                                                                                                                    
    w=math.floor(bw/pic_count)
    #h=(3*w)/5 #限定图片比例为5：3（待修改）
    #h=math.floor(bh/pic_count)
    h=math.floor((w*pic[0][1])/pic[0][0])
    PS=bw*h
    strp=''
    for i in range(pic_count):
        strp=strp+'\\includegraphics[width=%fmm,height=%fmm]{*p%d}\\par\n'%(w,h,i+1)
    #print(strp)
    for i in range(pic_count):
        strp=strp.replace('*p%d'%(i+1),pic[i][2])#插入图片
    pstyle=style.replace('%%pic%d'%(picarea_id),strp)
    #print(PS)
    return h,PS,pstyle

def fullvpic(style,bw,bh,pic_count,pic,picarea_id):
    pattern=r"(?<=minipage\}\{).*(?=\}\n%pic)"
    ww=re.findall(pattern,style)
    #w=bw*0.5-1.5  #minipage宽度获取待补充
    w=bw
    #h=(3*w)/5 #限定图片比例为5：3
    PS=0
    ph=0
    strp=''
    for i in range(0,pic_count):
        #h=(pic[i][1]*w)/pic[i][0]#高度按照图片比例调整
        h=math.floor(bh/pic_count)
        ph=ph+h
        PS=PS+w*h
        strp=strp+'\\includegraphics[width=%fmm,height=%fmm]{*p%d}\par\n'%(w,h,i+1)
    for i in range(0,pic_count):
        strp=strp.replace('*p%d'%(i+1),pic[i][2])#插入图片
    pstyle=style.replace('%%pic%d'%(picarea_id),strp)
    return ph,PS,pstyle

def colpic(style,one_column_width,pic_count,pic,picarea_id):
    fs,lh=ls.mc_fs_lh(style)
    mtlh=lh*1.3
    w=one_column_width
    h=[math.floor((w*pic[i][1])/pic[i][0]) for i in range(pic_count)]
    #按照行数计算图片的高度，防止使不同栏的行与行之间不对齐
    h=[round(h[i]/mtlh)*mtlh for i in range(pic_count)]
    sumh=np.sum(h)
    sumhc=round(sumh/mtlh)
    PS=w*sumh

    strp=''
    for i in range(pic_count):
        strp=strp+'\\includegraphics[width=\\columnwidth,height=%fmm]{*p%d}\\par\n'%(h[i],i+1)
    for i in range(pic_count):
        strp=strp.replace('*p%d'%(i+1),pic[i][2])#插入图片
    pstyle=style.replace('%%pic%d'%(picarea_id),strp)
    return sumhc,PS,pstyle

def getcolnum_and_colsep(style):
    pattern1=r"(?<=\\begin\{multicols\}\{).*(?=\})"#找到正文的字号与行距
    column_num=re.findall(pattern1,style)
    column_num=int(column_num[0]) #原栏数
    pattern2=r"(?<=\\setlength\{\\columnsep\}\{).*(?=mm\})"#找到正文的字号与行距
    column_sep=re.findall(pattern2,style)
    column_sep=int(column_sep[0]) #原栏间距
    return column_num,column_sep

#横标题具体样式与面积(加入换行条件)
def htitle_and_sht(style,bw,have_subtitle,count_subtitle,sub_title,count_title_char,ischangeline):
    pt=0.35
    pattern1=r"(?<=vspace{).*(?=mm})"
    pattern2=r"(?<=\\fontsize\{).*(?=\}\{)"
    vspace = list(map(int,re.findall(pattern1,style)))#vspace列表，这里只需要设置前三个vspace
    #print(vspace)
    fontsize=list(map(int,re.findall(pattern2,style)))#字号列表,顺序为副、主、副
    if ischangeline==1:
        hc=2  #标题行数
    elif ischangeline==0:
        hc=1
    
    #print(fontsize[1])
    #print(hc)
    #print(fontsize)
    if count_subtitle==0:
        vspace[0]=0
        vspace[1]=0
        th=fontsize[1]*pt*hc+vspace[2]
        hTS=th*bw#以mm为单位
    elif count_subtitle==1:
        if sub_title[0]=='':
            count_subtitle_char=len(sub_title[1])
            hcf=math.ceil((fontsize[0]*count_subtitle_char*pt)/bw)#记录副标题行数
            vspace[0]=0
        if sub_title[1]=='':
            count_subtitle_char=len(sub_title[0])
            hcf=math.ceil((fontsize[0]*count_subtitle_char*pt)/bw)
            vspace[1]=0
        th=(fontsize[0]*hcf+fontsize[1]*hc)*pt+vspace[0]+vspace[1]+vspace[2]
        #print(th)
        #print(vspace)
        hTS=bw*th
    elif count_subtitle==2:
        count_subtitle_char1=len(sub_title[0])
        count_subtitle_char2=len(sub_title[1])
        hcf1=math.ceil((fontsize[0]*count_subtitle_char1*pt)/bw)
        hcf2=math.ceil((fontsize[0]*count_subtitle_char2*pt)/bw)
        th=(fontsize[0]*hcf1+fontsize[1]*hc+fontsize[2]*hcf2)*pt+vspace[0]+vspace[1]+vspace[2]
        hTS=th*bw
    vspacestr=[str(i) for i in vspace] #将vspace转化为字符串
    #print(vspacestr)
    htv=re.sub(pattern1,lambda _: vspacestr.pop(0),style)#根据标题数改变间距
    #print(th,hTS,htv)
    #print(hTS)
    return th,hTS,htv

def judge_tw_and_vtc(style,have_subtitle,count_subtitle,sub_title,fs,ischangeline):
    pattern5=r"(?<=\\node\[right =0pt of).*(?=,rectangle)" #副标题位置标志
    subt_pos=re.findall(pattern5,style)
    vtc1=style
    #############根据以上信息处理标题宽度############
    if have_subtitle==False:
        if ischangeline==1:
            tw=fs[0]+fs[1]+16
            vtc1=style.replace('%maintitle2','')
        elif ischangeline==0:
            tw=fs[0]+8
    elif count_subtitle==1:
        if sub_title[0]=='' and ischangeline==1:
            tw=fs[0]+fs[1]+fs[2]+24
            vtc1=style.replace('%righttitle','').replace('%maintitle2','')
        if sub_title[0]=='' and ischangeline==0:
            tw=fs[0]+fs[2]+16
            vtc1=style.replace('%righttitle','')
            vtc1=re.sub(pattern5,' a',vtc1)
        if sub_title[1]=='' and ischangeline==1:
            tw=fs[0]+fs[1]+fs[3]+24
            vtc1=style.replace('%lefttitle','').replace('%maintitle2','')
        if sub_title[1]=='' and ischangeline==0:
            tw=fs[0]+fs[3]+16
            vtc1=style.replace('%lefttitle','')
    elif count_subtitle==2:
        if ischangeline==1:
            tw=fs[0]+fs[1]+fs[2]+fs[3]+32
            vtc1=style.replace('%righttitle','').replace('%lefttitle','').replace('%maintitle2','')
        if ischangeline==0:
            tw=fs[0]+fs[2]+fs[3]+24
            vtc1=style.replace('%righttitle','').replace('%lefttitle','')
    return tw,vtc1

#判断该竖标题的字号与缩放系数
def get_vfontsize_and_vscalecoe(bh,vth,mh,scale_thresh):
    #根据标题高度判断是否换行
    pt=0.35
    vth1=(vth-9.1)*scale_thresh+10.1 #压缩后的标题高度
    if vth1>=mh:
        ischangeline=1
        scalecoe=1
        #加入换行后的压缩系数的计算,暂时设置为1
    else:  #求压缩系数
        ischangeline=0
        maxscalecoe=(mh)/vth  #标题最大压缩系数
        if maxscalecoe>1:
            scalecoe=1
        else:
            scalecoe=maxscalecoe
    return scalecoe,ischangeline  #字号，压缩系数，是否换行

#垂直标题样式与面积（加入换行）
def vtitle1_svt(style,bw,bh,bx,have_subtitle,count_subtitle,sub_title,count_title_char,title,para_char):
    pt=0.35
    vtc=[]
    vTS=[]
    ischangeline=0
    tw=0
    pattern1=r"(?<=wrapfigure\}\{r\}\{).*(?=pt)"#垂直标题在右边时的总宽度
    pattern3=r"(?<=\}\{).*(?=\}\\selectfont)"#行距
    pattern4=r"(?<=\\fontsize\{).*(?=\}\{)"#字号
    
    #print(subt_pos)
    tw=list(map(float,re.findall(pattern1,style)))[0]
    lh=list(map(int,re.findall(pattern3,style)))
    #print(lh) 
    fs=list(map(float,re.findall(pattern4,style)))
    #print(fs)
    tw1,vtc1=judge_tw_and_vtc(style,have_subtitle,count_subtitle,sub_title,fs,0) #不换行标题宽度
    tw2,vtc2=judge_tw_and_vtc(style,have_subtitle,count_subtitle,sub_title,fs,1) #换行标题宽度

    ###########记录数据########################
    mmtw1=tw1*pt
    vth1=(count_title_char*fs[0]+26)*pt  #标题高度，是否根据行数计算高度，单位mm
    mh_test,MS1=ls.shmaintext(style,bw-mmtw1,para_char) #文本宽度为减去标题宽度后的文本高度
    #print('mh_test:',mh_test)
    #print('vth:',vth)
    scalecoe,ischangeline=get_vfontsize_and_vscalecoe(bh,vth1,mh_test,0.6)  #指定压缩系数
    #print('scalecoe:',scalecoe)

    if ischangeline==0: #不换行时
        strtw=str(tw1)
        vtc=vtc1
        vth=(vth1-9.1)*scalecoe+10.1
    elif ischangeline==1: #换行
        strtw=str(tw2)
        vtc=vtc2
        vth=((math.ceil(count_title_char/2))*fs[0]+26)*pt  #竖标题换行后标题区域的高度
    #print(strtw)
    vtc=re.sub(pattern1,strtw,vtc) #改变标题的宽度
    vtc=lp.change_scale_coe(vtc,scalecoe,1)  #改变垂直标题的压缩系数
    #根据新闻方框的x坐标改变垂直标题的方向
    vtc=lp.change_title_direction(vtc,bx)

    tw3=float(strtw)*pt
    vTS=vth*tw3  #竖标题面积
    return tw3,vth,vTS,vtc,ischangeline


######################各样式面积计算#################################################
def ht_np_nc(style,bw,have_subtitle,count_subtitle,sub_title,para_char,count_title_char,ischangeline):
    th,hTS,htv=htitle_and_sht(style,bw,have_subtitle,count_subtitle,sub_title,count_title_char,ischangeline)
    mh,MS=ls.shmaintext(style,bw,para_char)
    sth=th+mh
    S=hTS+MS
    return S,htv

def ht_np_c(style,bw,have_subtitle,count_subtitle,sub_title,para_char,count_title_char,threshold,ischangeline):
    th,hTS,htv=htitle_and_sht(style,bw,have_subtitle,count_subtitle,sub_title,count_title_char,ischangeline)
    if bw<threshold:#判断区块宽度能否分栏
        return 0,False
    colnum,colsep=getcolnum_and_colsep(style)
    ocw1,sumlc,sh,MS=ls.colshmaintext(style,bw,para_char,colnum,colsep)
    S=MS+hTS
    return S,htv

def vwt_np_nc(style,bw,bh,bx,have_subtitle,count_subtitle,sub_title,count_title_char,para_char,title):
    S=[]
    des=[]
    tw,vth,vTS,vtc,ischangeline=vtitle1_svt(style,bw,bh,bx,have_subtitle,count_subtitle,sub_title,count_title_char,title,para_char)
    print(vtc)
    mh,MS=ls.vwmaintext(style,bw,tw,vth,para_char)
    if ischangeline==1:
        vtc=vt_changeline(vtc,title)  #换行时标题的改变
    elif ischangeline==0:
        t1=''
        for t in range(len(title)-1):
            t1=t1+title[t]+'\\\\'
        tt1=t1+title[-1]   #垂直标题的换行操作
        vtc=vtc.replace('*mt1',tt1)
    S=MS
    return S,vtc

def ht_tbp_nc(style,bw,bh,have_subtitle,count_subtitle,sub_title,para_char,count_title_char,pic_count,pic,ischangeline):
    th,hTS,htv=htitle_and_sht(style,bw,have_subtitle,count_subtitle,sub_title,count_title_char,ischangeline)
    mh,MS=ls.shmaintext(style,bw,para_char)
    h,PS,pstyle=ls.fullhpic(htv,bw,pic_count,pic,1)#图片高度处理上待补充（可增加留白高度与图片高度的关系）
    sh=th+mh+h
    if sh>bh:
        return 0,False
    S=hTS+MS+PS
    return S,pstyle

def ht_tbp_c(style,bw,have_subtitle,count_subtitle,sub_title,para_char,count_title_char,pic_count,pic,threshold,ischangeline):
    th,hTS,htv=htitle_and_sht(style,bw,have_subtitle,count_subtitle,sub_title,count_title_char,ischangeline)
    h,PS,pstyle=ls.fullhpic(htv,bw,pic_count,pic,1)
    if bw<threshold:#判断区块宽度能否分栏
        return 0,False
    colnum,colsep=getcolnum_and_colsep(style)
    ocw1,sumlc,sh,MS=ls.colshmaintext(style,bw,para_char,colnum,colsep)
    S=hTS+MS+PS
    return S,pstyle

def ht_tbcp_c(style,bw,have_subtitle,count_subtitle,sub_title,para_char,count_title_char,pic_count,pic,ischangeline):
    pt=0.35
    pattern1=r"(?<=\\fontsize\{).*(?=\}\\selectfont \*mc)"
    fontsize=re.findall(pattern1,style)
    fslh=fontsize[0].replace('{','').split('}') 
    fs=int(fslh[0])*pt#字号，单位为mm
    lh=int(fslh[1])*pt#行距

    th,hTS,htv=htitle_and_sht(style,bw,have_subtitle,count_subtitle,sub_title,count_title_char,ischangeline)
    #colnum,colsep=getcolnum_and_colsep(style)
    pattern1=r"(?<=\\begin\{multicols\}\{).*(?=\})"#找到正文的字号与行距
    colnum=re.findall(pattern1,style)
    pattern2=r"(?<=\\setlength\{\\columnsep\}\{).*(?=mm\})"#找到正文的字号与行距
    colsep=re.findall(pattern2,style)
    if colnum==[]: #该情况为该新闻块样式不适合分栏时进行设置
        colnum=1
        colsep=0
    else:
        colnum=int(colnum[0]) #原栏数
        colsep=int(colsep[0]) #原栏间距
    ocw1,sumlc,sh,MS=ls.colshmaintext(style,bw,para_char,colnum,colsep)
    sumhc,PS,pstyle=colpic(style,ocw1,pic_count,pic,1)
    final_h=math.ceil((sumlc+2+sumhc)/colnum)*1.3*lh
    S=hTS+final_h*bw
    return S,pstyle

def picnews_vertical_nc(style,bw,bh,pic_count,pic):
    pattern=r"(?<=righthand width=).*(?=\\textwidth)"
    radio=re.findall(pattern,style)[0] #图片文字分割比例
    radio=float(radio)
    top,bottom,left,right=ls.tblr_space(style)
    bw1=(bw-left-right)*radio
    bh1=bh-top-bottom
    ph,PS,pstyle=fullvpic(style,bw1,bh1,pic_count,pic,1)
    #print(ph,PS,pstyle)
    #判断图片高度与新闻块高度的对比处理
    S=(ph+top+bottom+4.55)*bw #高度包括各种间距
    return S,pstyle

#待修改（图片宽度与高度的确定）
def picnews_lt_horizontal_nc(style,bw,bh,pic_count,pic,para_char):
    pattern=r"(?<=\%title\n\\begin\{minipage\}\{).*(?=\\textwidth)"
    radio=re.findall(pattern,style)[0]#正文与标题的分割比例
    radio=float(radio)

    top,bottom,left,right=ls.tblr_space(style)
    pattern5=r"(?<=vspace\{).*(?=mm\})"
    vspace=float(re.findall(pattern5,style)[0])
    #print(vspace)
    bw1=bw*(1-radio)-left-right
    mh,MS=ls.shmaintext(style,bw1,para_char)
    bw2=bw*(radio)-left-right
    h,PS,pstyle=ls.fullhpic(style,bw1,pic_count,pic,1)
    sumh=h+top+bottom+vspace+mh #总的图片新闻的高度
    S=bw*sumh
    return S,pstyle

def picnews_ht_horizontal_nc(style,bw,bh,pic_count,pic,para_char,title):
    pt=0.35
    top,bottom,left,right=ls.tblr_space(style)
    pattern=r"(?<=vspace\{).*(?=mm\})"
    vspace=re.findall(pattern,style)
    vspace=[float(x) for x in vspace] #图片与标题、标题与正文的间距
    #print(vspace)

    #获取标题字号
    pattern1=r"(?<=\\fontsize\{).*(?=\}\\selectfont \*mt)"
    fontsize=re.findall(pattern1,style)
    print(style)
    print(fontsize)
    fslh=fontsize[0].replace('{','').split('}') 
    fs=int(fslh[0])*pt#字号，单位为mm
    lh=int(fslh[1])*pt#行距
    #print(fs)
    bw1=bw-left-right
    #标题是否换行的判断
    hc=math.ceil((len(title)*fs)/bw1)
    th=hc*fs #标题的高度
    mh,MS=ls.shmaintext(style,bw1,para_char)
    bh1=bh-mh-top-bottom-th-2
    #h,PS,pstyle=fullhpic(style,bw1,bh1,pic_count,pic,1)
    h,PS,pstyle=fullhpic(style,bw1,pic_count,pic,1)
    print('PS&mh:',PS,mh)
    print('bw1&bh1:',bw1,bh1)
    sumh=top+bottom+h+np.sum(vspace)+fs+mh+4.55 #加上一行的留白高度
    S=sumh*bw
    #print(sumh)
    return S,pstyle

def main():
    style1=r'\begingroup#\setlength{\columnsep}{0pt}#\begin{wrapfigure}{r}{99pt}#\begin{tikzpicture}[scale=1]#%maintitle#\node[rectangle,text width =42pt] (a)#{\scalebox{1}[1]{\heiti{\bfseries\fontsize{42}{32}\selectfont \shortstack[c]{*mt}\par}}};#%%subtitle2#%righttitle\node[right =0pt of a,rectangle,text width =21pt]#%righttitle{\heiti{\bfseries\fontsize{21}{17}\selectfont *s2\par}};#%%subtitle1#%lefttitle\node[left =0pt of a,rectangle,text width =21pt]#%lefttitle{\heiti{\bfseries\fontsize{21}{17}\selectfont *s1\par}};#\end{tikzpicture}\par#\vspace{-\baselineskip}#\end{wrapfigure}#{\songti{\fontsize{9}{10}\selectfont *mc\par}}\par#\endgroup'
    style1=style1.replace('#','\n')
    #a,y=vwt_np_nc(style1,100,100,1,1,['空间的',''],12,[122,33])
    #print(a,y[0])
    style2=r'%%subtitle1#{\centering\heiti{\fontsize{21}{0}\selectfont *s1\par}}#\vspace{3mm}#%maintitle#\scalebox{1}[1]{\centering\syht{\fontsize{48}{0}\selectfont \shortstack[c]{*mt}\par}}#%%subtitle2#\vspace{3mm}#\\{\centering\heiti{\fontsize{21}{0}\selectfont *s2\par}}#\vspace{5mm}#\setlength{\columnsep}{5mm}#\vspace{-\baselineskip}#\begin{multicols}{2}#{\songti{\fontsize{9}{10}\selectfont *mc\par}}\par\end{multicols}#\vspace{-1em}'
    style2=style2.replace('#','\n')
    th,hTS,htv=htitle_and_sht(style2,100,True,1,['','ksal'],12,1)
    #print(htv)
    style3=r'\begingroup#\setlength{\columnsep}{0pt}#\begin{wrapfigure}{r}{99pt}#\begin{tikzpicture}[scale=1]#%maintitle#\node[rectangle,text width =42pt] (a)#{\scalebox{1}[1]{\syht{\bfseries\fontsize{42}{32}\selectfont \shortstack[c]{*mt1}\par}}};#%maintitle2\node[rectangle,text width =42pt] (b)#%maintitle2{\scalebox{1}[1]{\syht{\bfseries\fontsize{42}{32}\selectfont \shortstack[c]{*mt2}\par}}};#%%subtitle2#%righttitle\node[right =0pt of b,rectangle,text width =21pt]#%righttitle{\heiti{\bfseries\fontsize{21}{17}\selectfont *s2\par}};#%%subtitle1#%lefttitle\node[left =0pt of a,rectangle,text width =21pt]#%lefttitle{\heiti{\bfseries\fontsize{21}{17}\selectfont *s1\par}};#\end{tikzpicture}\par#\vspace{-\baselineskip}#\end{wrapfigure}#{\songti{\fontsize{9}{10}\selectfont *mc\par}}\par#\endgroup'
    style3=style3.replace('#','\n')
    #print(style3)
    #tw,vth,vTS,vtc,ic=vtitle1_svt(style3,100,100,True,1,['','12'],12,"接待萨科嗲积分安抚那啥三大覅",[122,200])
    #print(tw)
    #print(vtc[0])
    x,y=vwt_np_nc(style3,93.68,298.65999999999997,False,0,['',''],18,[76, 107, 204, 193, 149],"金华之光·金东文创专区将于本周六启用")
    print(y)


if __name__=="__main__":
    main()
