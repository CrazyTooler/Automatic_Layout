import numpy as np
import math
import re

def tblr_space(style):
    pattern1=r"(?<=top=).*(?=mm,right)"
    top=float(re.findall(pattern1,style)[0])
    #print(top)
    pattern2=r"(?<=right=).*(?=mm,bottom)"
    right=float(re.findall(pattern2,style)[0])
    #print(right)
    pattern3=r"(?<=bottom=).*(?=mm,left)"
    bottom=float(re.findall(pattern3,style)[0])
    #print(bottom)
    pattern4=r"(?<=left=).*(?=mm,outer)"
    left=float(re.findall(pattern4,style)[0])
    #print(left)
    return top,bottom,left,right
#图片的处理
#这里的bh不是新闻块的高度，而是图片区域的高度
def fullhpic(bw,pic_count,pic):
    #初步确定图片宽高                                                                                                                                                                                                                                                                                    
    w=math.floor(bw/pic_count)
    #h=(3*w)/5 #限定图片比例为5：3（待修改）
    h=math.floor((w*pic[0][1])/pic[0][0])
    #h=math.floor(bh/pic_count)
    PS=bw*h
    return h,PS

def fullvpic(bw,bh,pic_count):
    w=bw
    #h=(3*w)/5 #限定图片比例为5：3
    PS=0
    ph=0
    for i in range(0,pic_count):
        #h=(pic[i][1]*w)/pic[i][0]#高度按照图片比例调整
        h=math.floor(bh/pic_count)
        ph=ph+h
        PS=PS+w*h
    return ph,PS

def colpic(one_column_width,pic_count,pic,mtlh):
    pt=0.35
    mtlh=mtlh*pt*1.3
    w=one_column_width
    h=[math.floor((w*pic[i][1])/pic[i][0]) for i in range(pic_count)]
    #按照行数计算图片的高度，防止使不同栏的行与行之间不对齐
    h=[round(h[i]/mtlh)*mtlh for i in range(pic_count)]
    sumh=np.sum(h)
    sumhc=round(sumh/mtlh)
    PS=w*sumh
    return sumhc,PS

#横标题具体样式与面积(加入换行条件)
def htitle_and_sht(bw,count_subtitle,sub_title,ischangeline,vspace,mt_fontsize,subt_fontsize): #初始vspace=[3,3,5]
    pt=0.35
    if ischangeline==1:
        hc=2  #标题行数
    elif ischangeline==0:
        hc=1
    if count_subtitle==0:
        vspace[2]=5
        th=mt_fontsize*pt*hc+vspace[2]
        hTS=th*bw#以mm为单位
    elif count_subtitle==1:
        if sub_title[0]=='':
            count_subtitle_char=len(sub_title[1])
            hcf=math.ceil((subt_fontsize*count_subtitle_char*pt)/bw)#记录副标题行数
            vspace=[0,3,5]
        if sub_title[1]=='':
            count_subtitle_char=len(sub_title[0])
            hcf=math.ceil((subt_fontsize*count_subtitle_char*pt)/bw)
            vspace=[3,0,5]
        th=(subt_fontsize*hcf+mt_fontsize*hc)*pt+vspace[0]+vspace[1]+vspace[2]
        hTS=bw*th
    elif count_subtitle==2:
        vspace=[3,3,5]
        count_subtitle_char1=len(sub_title[0])
        count_subtitle_char2=len(sub_title[1])
        hcf1=math.ceil((subt_fontsize*count_subtitle_char1*pt)/bw)
        hcf2=math.ceil((subt_fontsize*count_subtitle_char2*pt)/bw)
        th=(subt_fontsize*hcf1+mt_fontsize*hc+subt_fontsize*hcf2)*pt+vspace[0]+vspace[1]+vspace[2]
        hTS=th*bw
    return th,hTS

#垂直标题样式与面积（加入换行）
def vtitle1_svt(count_title_char,ischangeline,tw,scalecoe,mt_fontsize):
    pt=0.35
    vth1=(count_title_char*mt_fontsize+26)*pt #一列标题的高度
    if ischangeline==0: #不换行时
        vth=(vth1-9.1)*scalecoe+10.1
    elif ischangeline==1: #换行
        vth=((math.ceil(count_title_char/2))*mt_fontsize+26)*pt  #竖标题换行后标题区域的高度
    vTS=vth*tw  #竖标题面积
    return tw,vth,vTS

#不分栏情况下正文的面积计算
def shmaintext(bw,para_char,mtfs,mtlh):
    pt=0.35
    #按段计算行数
    ohc=round(bw/(mtfs*pt)) #一行的字数(采用四舍五入)
    #print('ohc:',ohc)
    #print(ohc)
    hc=[]
    for i in para_char:
        t=math.ceil(i/ohc)
        hc.append(t)
    sumhc=np.sum(np.array(hc))#计算总行数
    #print('sumhc:',sumhc)
    mh=sumhc*mtlh*1.3*pt#文本高度
    MS=mh*bw
    #print(MS)
    #print('mh&bw:',mh,bw,sumhc,mtlh)
    return mh,MS

#垂直标题文字环绕情况下文本面积的计算
def vwmaintext(bw,tw,th,parachar,mtfs,mtlh):
    pt=0.35
    mtfs=mtfs*pt
    mtlh=mtlh*pt
    maxlhc=round(th/(mtlh*1.3)) #标题高度对应的正文行数
    tth=0#
    spara=0 #开始分割的段落号
    ohc1=round((bw-tw)/mtfs) #前半部分一行字数
    ohc2=round(bw/mtfs) #后半部分一行字数
    for i in range(len(parachar)):
        tth=tth+math.ceil((parachar[i]/ohc1)*mtlh*1.3)
        if tth>maxlhc*mtlh*1.3:
            spara=i #找出文本宽度开始改变的段落(从0开始)
            break
    #print("spara:",spara)
    c1=0 #前半部分所有段落字数
    for i in range(spara-1):
        c1=c1+parachar[i]
    histh=0
    hc3=0
    hh3=0
    hh1=0
    hh2=0
    for i in range(len(parachar)):
        if spara!=0 and i<spara:
            histh=histh+math.ceil(parachar[i]/ohc1) #在分段之前的行数
            #print('histh：',histh)
        elif spara==0:
            histh=0
        if i == spara :  
            if maxlhc-histh<0:
                hh1=math.ceil(parachar[spara]/ohc1)#前半部分
                hh2=0 #后半部分
            else:
                c2=ohc1*(abs(maxlhc-histh))-2 #前半部分字数,减去缩进
                hh1=maxlhc-histh
                c3=parachar[spara]-c2 #后半部分字数
                hh2=math.ceil(c3/ohc2)
        if i>spara:
            hc3=hc3+math.ceil(parachar[i]/ohc2)*mtlh*1.3
            hh3=hh3+math.ceil(parachar[i]/ohc2)
    MS=(histh+hh1+hh2+hh3)*mtlh*1.3*bw
    mh=(histh+hh1+hh2+hh3)*mtlh*1.3
    #print("hh2:",hh2)
    #print("pre:",(histh+hh1))
    #print("final:",(hh2+hh3))
    return mh,MS

def colshmaintext(bw,para_char,colnum,colsep,mtfs,mtlh):
    pt=0.35
    mtfs=mtfs*pt
    mtlh=mtlh*pt
    ocw=(bw-(colnum-1)*colsep)/colnum#一栏宽度
    occ=round(ocw/mtfs)#一栏字数(按照四舍五入的形式)
    ocw1=occ*mtfs#一栏宽度（按字数计算）
    hc=[]
    for i in para_char:
        t=math.ceil(i/occ)
        hc.append(t)
    sumcc=math.ceil((np.sum(np.array(hc))+2)/colnum)#计算总行数，加2为给个两行的误差值。
    sumlc=np.sum(np.array(hc)) #计算文章在该栏宽的总行数
    sh=sumcc*mtlh*1.3
    MS=sumcc*mtlh*1.3*bw
    final_column_lines=sumcc*colnum-(np.sum(np.array(hc))) #最后一栏空的行数
    #print('一段字数',hc)
    #print('一栏字数',occ)
    #print('总行数&一栏行数：',sumcc,sumlc)
    #print('-------------')
    return ocw1,sumlc,MS #返回一栏字数、一栏的行数、文章高度、文章面积

#######################################################################
def ht_np_nc(bw,count_subtitle,sub_title,para_char,ischangeline,vspace,mt_fontsize,subt_fontsize,mtfs,mtlh):
    th,hTS=htitle_and_sht(bw,count_subtitle,sub_title,ischangeline,vspace,mt_fontsize,subt_fontsize)
    mh,MS=shmaintext(bw,para_char,mtfs,mtlh)
    #print('hTS&MS:',hTS,MS)
    S=hTS+MS
    return S

def ht_np_c(bw,count_subtitle,sub_title,para_char,ischangeline,vspace,mt_fontsize,subt_fontsize,colnum,colsep,mtfs,mtlh):
    th,hTS=htitle_and_sht(bw,count_subtitle,sub_title,ischangeline,vspace,mt_fontsize,subt_fontsize)
    ocw1,sumlc,MS=colshmaintext(bw,para_char,colnum,colsep,mtfs,mtlh)
    #print('hTS&MS:',hTS,MS)
    S=MS+hTS
    return S

def vwt_np_nc(bw,count_title_char,para_char,ischangeline,tw,scalecoe,mt_fontsize,mtfs,mtlh):
    tw,vth,vTS=vtitle1_svt(count_title_char,ischangeline,tw,scalecoe,mt_fontsize)
    mh,MS=vwmaintext(bw,tw,vth,para_char,mtfs,mtlh)
    S=MS
    return S

def ht_tbp_nc(bw,count_subtitle,sub_title,para_char,pic_count,pic,ischangeline,vspace,mt_fontsize,subt_fontsize,mtfs,mtlh):
    th,hTS=htitle_and_sht(bw,count_subtitle,sub_title,ischangeline,vspace,mt_fontsize,subt_fontsize)
    mh,MS=shmaintext(bw,para_char,mtfs,mtlh)
    h,PS=fullhpic(bw,pic_count,pic)#图片高度处理上待补充（可增加留白高度与图片高度的关系）
    sh=th+mh+h
    S=hTS+MS+PS
    return S

def ht_tbp_c(bw,count_subtitle,sub_title,para_char,pic_count,pic,ischangeline,vspace,mt_fontsize,subt_fontsize,colnum,colsep,mtfs,mtlh):
    th,hTS=htitle_and_sht(bw,count_subtitle,sub_title,ischangeline,vspace,mt_fontsize,subt_fontsize)
    h,PS=fullhpic(bw,pic_count,pic)
    ocw1,sumlc,MS=colshmaintext(bw,para_char,colnum,colsep,mtfs,mtlh)
    S=hTS+MS+PS
    return S

def ht_tbcp_c(bw,count_subtitle,sub_title,para_char,pic_count,pic,ischangeline,vspace,mt_fontsize,subt_fontsize,colnum,colsep,mtfs,mtlh):
    pt=0.35
    th,hTS=htitle_and_sht(bw,count_subtitle,sub_title,ischangeline,vspace,mt_fontsize,subt_fontsize)
    ocw1,sumlc,MS=colshmaintext(bw,para_char,colnum,colsep,mtfs,mtlh)
    sumhc,PS=colpic(ocw1,pic_count,pic,mtlh)
    final_h=math.ceil((sumlc+2+sumhc)/colnum)*mtlh*1.3*pt
    S=hTS+final_h*bw
    return S

def picnews_vertical_nc(style,bw,bh,pic_count):
    pattern=r"(?<=righthand width=).*(?=\\textwidth)"
    radio=re.findall(pattern,style)[0] #图片文字分割比例
    radio=float(radio)
    top,bottom,left,right=tblr_space(style)
    bw1=(bw-left-right)*radio
    bh1=bh-top-bottom
    ph,PS=fullvpic(bw1,bh1,pic_count)
    #print(ph,PS,pstyle)
    #判断图片高度与新闻块高度的对比处理
    S=(ph+top+bottom+4.55)*bw #高度包括各种间距
    return S

#待修改（图片宽度与高度的确定）
def picnews_lt_horizontal_nc(style,bw,pic_count,pic,para_char):
    pattern=r"(?<=\%title\n\\begin\{minipage\}\{).*(?=\\textwidth)"
    radio=re.findall(pattern,style)[0]#正文与标题的分割比例
    radio=float(radio)

    top,bottom,left,right=tblr_space(style)
    pattern5=r"(?<=vspace\{).*(?=mm\})"
    vspace=float(re.findall(pattern5,style)[0])
    #print(vspace)
    bw1=bw*(1-radio)-left-right
    mh,MS=shmaintext(style,bw1,para_char)
    bw2=bw*(radio)-left-right
    h,PS=fullhpic(bw1,pic_count,pic)
    sumh=h+top+bottom+vspace+mh #总的图片新闻的高度
    S=bw*sumh
    return S

def picnews_ht_horizontal_nc(style,bw,bh,pic_count,pic,para_char,title,mtfs,mtlh):
    pt=0.35
    top,bottom,left,right=tblr_space(style)
    pattern=r"(?<=vspace\{).*(?=mm\})"
    vspace=re.findall(pattern,style)
    vspace=[float(x) for x in vspace] #图片与标题、标题与正文的间距
    #print(vspace)
    #获取标题字号
    pattern1=r"(?<=\\fontsize\{).*(?=\}\\selectfont \*mt)"
    fontsize=re.findall(pattern1,style)
    #print(style)
    #print(fontsize)
    fslh=fontsize[0].replace('{','').split('}') 
    fs=int(fslh[0])*pt#字号，单位为mm
    lh=int(fslh[1])*pt#行距
    #print(fs)
    bw1=bw-left-right
    #标题是否换行的判断
    hc=math.ceil((len(title)*fs)/bw1)
    th=hc*fs #标题的高度
    mh,MS=shmaintext(bw1,para_char,mtfs,mtlh)
    bh1=bh-mh-top-bottom-th-2  
    #h,PS=fullhpic(bw1,bh1,pic_count,pic)
    h,PS=fullhpic(bw1,pic_count,pic)
    #print('bw1&bh1:',bw1,bh1)
    #print('PS&mh:',PS,mh)
    sumh=top+bottom+h+np.sum(vspace)+fs+mh+4.55 #加上一行的留白高度
    S=sumh*bw
    #print(sumh)
    return S



def main():
    '''
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
    '''
    s1=ht_tbcp_c(100,0,['',''],[100,200,130],1,[[10,10,'']],0,[3,3,5],30,21,3,5,9,10)
    print(s1)


if __name__=="__main__":
    main()
