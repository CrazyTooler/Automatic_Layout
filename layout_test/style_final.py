import re
import doctest
import math
import numpy as np
from pynverse import inversefunc
import itertools
from layout_test.style_mysql import mysqlCon

################样式中标题、分栏、图片的一些处理#########################################
#查找正文字号与行距
def mc_fs_lh(style):
    pt=0.35
    pattern1=r"(?<=\\fontsize\{).*(?=\}\\selectfont \*mc)"#找到正文的字号与行距
    fontsize=re.findall(pattern1,style)
    fslh=fontsize[0].replace('{','').split('}') 
    fs=int(fslh[0])*pt#字号
    lh=int(fslh[1])*pt#行距
    return fs,lh

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
#标题具体样式与面积
def htitle_and_sht(style,bw,have_subtitle,count_subtitle,sub_title,count_title_char):
    pt=0.35
    pattern1=r"(?<=vspace{).*(?=mm})"
    pattern2=r"(?<=\\fontsize\{).*(?=\}\{)"
    vspace = list(map(int,re.findall(pattern1,style)))#vspace列表，这里只需要设置前三个vspace
    #print(vspace)
    fontsize=list(map(int,re.findall(pattern2,style)))#字号列表,顺序为副、主、副
    #计算主标题所占行数(考虑主标题换行情况)
    maxohc=math.floor(bw/(fontsize[1]*pt))
    hc=math.ceil(count_title_char/maxohc)
    '''
    if ischangeline==1:
        hc=2  #标题行数
    elif ischangeline==0:
        hc=1
    '''
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

def vtitle1_svt(style,bw,bh,have_subtitle,count_subtitle,sub_title,count_title_char):
    pt=0.35
    vtc=[]
    vTS=[]
    vtc1=style
    tw=0
    pattern1=r"(?<=wrapfigure\}\{r\}\{).*(?=pt)"#垂直标题在右边时的总宽度
    pattern2=r"(?<=wrapfigure\}\{).*(?=\}\{)"
    pattern3=r"(?<=\}\{).*(?=\}\\selectfont)"#行距
    pattern4=r"(?<=\\fontsize\{).*(?=\}\{)"#字号
    tw=list(map(float,re.findall(pattern1,style)))[0]
    lh=list(map(int,re.findall(pattern3,style)))
    #print(lh)
    fs=list(map(float,re.findall(pattern4,style)))
    #print(fs)
    if have_subtitle==False:
        tw=fs[0]+8
    elif count_subtitle==1:
        if sub_title[0]=='':
            tw=fs[0]+fs[1]+16
            vtc1=style.replace('%righttitle','')
        if sub_title[1]=='':
            tw=fs[0]+fs[1]+16
            vtc1=style.replace('%lefttitle','')
    elif count_subtitle==2:
        tw=fs[0]+fs[1]+fs[2]+24
        vtc1=style.replace('%righttitle','').replace('%lefttitle','')
    strtw=str(tw)
    #print(strtw)
    s1=re.sub(pattern1,strtw,vtc1)
    vtc.append(s1)
    s2=re.sub(pattern2,'l',s1)#增加标题在左边的样式
    vtc.append(s2)
    #竖直标题面积计算
    tw=tw*pt
    #print(tw)
    vth=(count_title_char*lh[0]*1.3+26)*pt#是否根据行数计算高度
    #print(vth)
    #if vth>bh:#如果竖直标题大于区块高度则传入空串
        #vtc=''
    vTS.append(vth*tw)
    vTS.append(vth*tw)
    return tw,vth,vTS,vtc

def vtitle2_svt(style,bw,bh,have_subtitle,count_subtitle,sub_title,count_title_char):
    pt=0.35
    vtc=style
    #tw=0
    pattern1=r"(?<=righthand width=).*(?=pt,halign)"#垂直标题在右边时的总宽度
    pattern2=r"(?<=lefthand width=).*(?=pt,halign)"#垂直标题在左边时的总宽度
    pattern3=r"(?<=\\fontsize\{).*(?=\}\\selectfont \*mt)"#找到主标题的字号与行距
    pattern4=r"(?<=\\fontsize\{).*(?=\}\\selectfont \*s1)"#找到副标题一的字号与行距
    pattern5=r"(?<=\\fontsize\{).*(?=\}\\selectfont \*s2)"#找到副标题二的字号与行距
    fslh1=re.findall(pattern3,style)
    fslh2=re.findall(pattern4,style)
    fslh3=re.findall(pattern5,style)
    fh1=fslh1[0].replace('{','').split('}')
    fh2=fslh2[0].replace('{','').split('}')
    fh3=fslh3[0].replace('{','').split('}') 
    fs=[int(fh1[0]),int(fh2[0]),int(fh3[0])]
    lh=[int(fh1[1]),int(fh2[1]),int(fh3[1])]
    #print(fs)
    #print(lh)
    tw1=list(map(float,re.findall(pattern1,style)))
    tw2=list(map(float,re.findall(pattern2,style)))
    if tw1==[]:
        tw=tw2[0]
        #print(tw)
    else:
        tw=tw1[0]
    #print(tw)
    if have_subtitle==False:
        tw=fs[0]+8
    elif count_subtitle==1:
        if sub_title[0]=='':
            tw=fs[0]+fs[1]+16
            vtc=style.replace('%righttitle','')
        if sub_title[1]=='':
            tw=fs[0]+fs[1]+16
            vtc=style.replace('%lefttitle','')
    elif count_subtitle==2:
        tw=fs[0]+fs[1]+fs[2]+24
        vtc=style.replace('%righttitle','').replace('%lefttitle','')
    strtw=str(tw)
    vtc=re.sub(pattern1,strtw,vtc)
    vtc=re.sub(pattern2,strtw,vtc)
    #print(vtc)
    #竖直标题面积计算
    tw=tw*pt
    #print(tw)
    vth=(count_title_char*lh[0]*1.3+26)*pt#代补充
    #print(vth)
    if vth>bh:#如果竖直标题大于区块高度则传入空串
        vtc=''
    vTS=bh*tw  #这里需要将高度改为文本高度
    #print(vTS)
    return tw,vth,vTS,vtc

##多列样式的处理分
def colshmaintext(style,bw,para_char,colnum,colsep):
    pt=0.35
    fs,lh=mc_fs_lh(style)
    ocw=(bw-(colnum-1)*colsep)/colnum#一栏宽度
    occ=round(ocw/fs)#一栏字数(按照四舍五入的形式)
    ocw1=occ*fs#一栏宽度（按字数计算）
    hc=[]
    for i in para_char:
        t=math.ceil(i/occ)
        hc.append(t)
    sumcc=math.ceil((np.sum(np.array(hc)))/colnum)#计算总行数
    sumlc=np.sum(np.array(hc)) #计算文章在该栏宽的总行数

    sh=sumcc*lh*1.3
    MS=sumcc*lh*1.3*bw
    return ocw1,sumlc,sh,MS #返回一栏字数、一栏的行数、文章高度、文章面积

def handlecolnum(style,bw,para_char,threshold):
    cstyle=[]
    MS=[]
    ocw=[]
    scolnum=[]
    sh=[]
    sumlc=[]
    pattern=r"(?<=\\columnsep\}\{).*(?=mm)"
    colsep=list(map(float,re.findall(pattern,style)))#获取栏间距
    #print(colsep)
    cube = (lambda colnum: (bw-(colnum-1)*colsep[0])/colnum)
    invcube = inversefunc(cube,y_values=threshold,domain=[1,15])#设置栏数范围为1-8
    #print(invcube)
    colnum=math.floor(invcube)
    if colnum<2:#若无法分栏则返回错误值
        return 0,0,0,0,0,False
    if colnum>6:
        return 0,0,0,0,0,False#设置最高分栏数为6
    pattern1=r"(?<=multicols\}\{).*(?=\})"
    for i in range(2,colnum+1):
        t=str(i)
        st1=re.sub(pattern1,t,style)
        cstyle.append(st1)
        ocw1,sumlc1,sh1,ms1=colshmaintext(style,bw,para_char,i,colsep[0])
        MS.append(ms1)
        sumlc.append(sumlc1) #记录文章在该栏宽下的总行数
        scolnum.append(i)#记录栏数
        ocw.append(ocw1)#一栏的宽度
        sh.append(sh1)#文章高度
    return scolnum,ocw,sumlc,sh,MS,cstyle
#图片的处理
def fullhpic(style,bw,pic_count,pic,picarea_id):
    #初步确定图片宽高                                                                                                                                                                                                                                                                                    
    w=math.floor(bw/pic_count)
    h=(3*w)/5 #限定图片比例为5：3（待修改）
    PS=bw*h
    strp=''
    for i in range(pic_count):
        strp=strp+'\\includegraphics[width=%fmm,height=%fmm]{*p%d}\n'%(w,h,i+1)
    #print(strp)
    for i in range(pic_count):
        strp=strp.replace('*p%d'%(i+1),pic[i][2])#插入图片
    pstyle=style.replace('%%pic%d'%(picarea_id),strp)
    #print(PS)
    return h,PS,pstyle

def fullvpic(style,bw,pic_count,pic,picarea_id):
    pattern=r"(?<=minipage\}\{).*(?=\}\n%pic)"
    ww=re.findall(pattern,style)
    #w=bw*0.5-1.5  #minipage宽度获取待补充
    w=bw
    #h=(3*w)/5 #限定图片比例为5：3
    PS=0
    ph=0
    strp=''
    for i in range(0,pic_count):
        h=(pic[i][1]*w)/pic[i][0]#高度按照图片比例调整
        ph=ph+h
        PS=PS+w*h
        strp=strp+'\\includegraphics[width=%fmm,height=%fmm]{*p%d}\par\n'%(w,h,i+1)
    for i in range(0,pic_count):
        strp=strp.replace('*p%d'%(i+1),pic[i][2])#插入图片
    pstyle=style.replace('%%pic%d'%(picarea_id),strp)
    return ph,PS,pstyle

def colpic(style,bh,ocw,pic):
    #\includegraphics[width=\columnwidth,height=0mm]{*ct}
    pattern1=r'(?<=includegraphics\[width=\\columnwidth,height=).*(?=mm])'
    pc = list(map(int,re.findall(pattern1,style)))
    #找到正文的字号与行距(mm)
    pt=0.35
    fs,lh=mc_fs_lh(style)
    olh=lh*1.3 #一行的高度
    if len(pc)==1:
        w1=pic[0][0]
        h1=pic[0][1]
        pht=(ocw*h1)/w1 #按图片比例计算
        ph=math.floor(pht/olh)*olh #根据行数计算图片高度
        if ph>bh:
            return 0,0,False
        PS=ocw*ph
        pstyle1=re.sub(pattern1,str(ph),style)
        pstyle=pstyle1.replace('*ct',pic[0][2]).replace('*cb',pic[0][2])
    elif len(pc)==2:
        w1=pic[0][0]
        h1=pic[0][1]
        w2=pic[1][0]
        h2=pic[1][1]
        pht1=(ocw*h1)/w1
        ph1=math.floor(pht1/olh)*olh #根据行数计算图片高度
        pht2=(ocw*h2)/w2
        ph2=math.floor(pht2/olh)*olh #根据行数计算图片高度
        if ph1>bh or ph2>bh:
            return 0,0,False
        ph=ph1+ph2
        PS1=ocw*ph1
        PS2=ocw*ph2
        PS=PS1+PS2
        strph=[str(ph1),str(ph2)]
        pstyle1=re.sub(pattern1,lambda _: strph.pop(0),style)
        pstyle=pstyle1.replace('*ct',pic[0][2]).replace('*cb',pic[1][2])
    return ph,PS,pstyle

def col_pic_s(style,ph,sumlc,ocw,column):
    fs,lh=mc_fs_lh(style)
    olh=lh*1.3
    if sumlc<column:
        olc=ph/olh #一栏高度

#图片的分配（几张图片，几个图片区域,分配方案）
def ditrpic(pic_count,pic,picarea):
    newpicnumarr=[]
    picarr=[]
    refernp=np.arange(1,pic_count,1)#生成图片数量范围内的数组
    picnumarr=list(itertools.product(refernp,repeat=picarea))
    #print(refernp)
    for i in range(len(picnumarr)):
        if np.sum(picnumarr[i])==pic_count and max(picnumarr[i])<5:#每个图片区域能存放的图片最大数量为4
            newpicnumarr.append(picnumarr[i])
    #print(newpicnumarr)
    for i in range(len(newpicnumarr)):
        if len(newpicnumarr[0])==2: #两个图片区域
            pic_temp=[pic[0:newpicnumarr[i][0]],pic[newpicnumarr[i][0]::]]
            picarr.append(pic_temp)
        if len(newpicnumarr[0])==3: #三个图片区域的图片处理
            pic_temp=[pic[0:newpicnumarr[i][0]],pic[newpicnumarr[i][0]:np.sum(newpicnumarr[i][0:2])],pic[np.sum(newpicnumarr[i][0:2])::]]
            picarr.append(pic_temp)
    #print(picarr)
    return newpicnumarr,picarr

#不分栏情况下正文的面积计算
def shmaintext(style,bw,para_char):
    pt=0.35
    fs,lh=mc_fs_lh(style) #读取正文字号与行距
    #按段计算行数
    ohc=round(bw/fs) #一行的字数(采用四舍五入)
    #print('ohc:',ohc)
    #print(ohc)
    hc=[]
    for i in para_char:
        t=math.ceil(i/ohc)
        hc.append(t)
    sumhc=np.sum(np.array(hc))#计算总行数
    mh=sumhc*lh*1.3#文本高度
    MS=mh*bw
    #print(MS)
    #print('mh&bw:',mh,bw,sumhc,lh)
    return mh,MS

#垂直标题文字环绕情况下文本面积的计算
def vwmaintext(style,bw,tw,th,parachar):
    pt=0.35
    fs,lh=mc_fs_lh(style)
    maxlhc=round(th/(lh*1.3)) #标题高度对应的正文行数
    tth=0#
    spara=0 #开始分割的段落号
    ohc1=round((bw-tw)/fs) #前半部分一行字数
    ohc2=round(bw/fs) #后半部分一行字数
    for i in range(len(parachar)):
        tth=tth+math.ceil((parachar[i]/ohc1)*lh*1.3)
        if tth>maxlhc*lh*1.3:
            spara=i #找出文本宽度开始改变的段落(从0开始)
            break
    print("spara:",spara)
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
            hc3=hc3+math.ceil(parachar[i]/ohc2)*lh*1.3
            hh3=hh3+math.ceil(parachar[i]/ohc2)
    MS=(histh+hh1+hh2+hh3)*lh*1.3*bw
    mh=(histh+hh1+hh2+hh3)*lh*1.3
    #print("hh2:",hh2)
    print("pre:",(histh+hh1))
    print("final:",(hh2+hh3))
    return mh,MS

def getstydict(th,tw,hTS,mh,MS,ph):
    sdict=dict({'title_height':th,'title_width':tw,'title_s':hTS,'mt_height':mh,'mt_s':MS})
    return sdict

################具体样式的处理##############################
def ht_np_nc(style,name,bw,have_subtitle,count_subtitle,sub_title,para_char,count_title_char):
    th,hTS,htv=htitle_and_sht(style,bw,have_subtitle,count_subtitle,sub_title,count_title_char)
    mh,MS=shmaintext(style,bw,para_char)
    sth=th+mh
    S=hTS+MS
    des='ht_np_nc'
    return des,S,htv

def ht_np_c(style,name,bw,have_subtitle,count_subtitle,sub_title,para_char,count_title_char,threshold):
    S=[]
    des=[]
    sth=[]#文章总体高度
    th,hTS,htv=htitle_and_sht(style,bw,have_subtitle,count_subtitle,sub_title,count_title_char)
    if bw<threshold:#判断区块宽度能否分栏
        return 0,0,False
    scolnum,ocw,sumlc,sh,MS,cstyle=handlecolnum(htv,bw,para_char,threshold)
    if ocw==0 and sh==0 and MS==0 and cstyle==False and scolnum==0:#若该宽度无法分栏则返回错误信息
        return 0,0,False
    for i in range(len(MS)):
        s1=hTS+MS[i]
        sth1=th+sh[i]
        sth.append(sth1)
        des.append('ht_np_%dc'%(scolnum[i]))
        S.append(s1)
    return des,S,cstyle

def vwt_np_nc(style,name,bw,bh,have_subtitle,count_subtitle,sub_title,count_title_char,para_char):
    S=[]
    des=[]
    sth=[]#后期修改高度的计算方法
    tw,vth,vTS,vtc=vtitle1_svt(style,bw,bh,have_subtitle,count_subtitle,sub_title,count_title_char)
    mh,MS=vwmaintext(style,bw,tw,vth,para_char)
    #mh,MS=shmaintext(style,bw,para_char)
    mh_test,MS1=shmaintext(style,bw-tw,para_char)
    if vtc=='' or mh_test<vth:
        return 0,0,False #表示标题高度大于区块高度，返回失败信息
    else:
        #S.append(vTS[0]+MS)
        #S.append(vTS[1]+MS)
        S.append(MS)
        S.append(MS)
        des.append('vwrt_np_nc')
        des.append('vwlt_np_nc')
        #tt=(vTS[0]+MS)/bw
        tt=(MS)/bw
        sth.append(tt)
        sth.append(tt)
        return des,S,vtc

def rvt_np_nc(style,name,bw,bh,have_subtitle,count_subtitle,sub_title,count_title_char,para_char):
    tw,vth,vTS,vtc=vtitle2_svt(style,bw,bh,have_subtitle,count_subtitle,sub_title,count_title_char)
    bw1=bw-tw  #没有加上竖标题与文本间距
    mh,MS=shmaintext(style,bw1,para_char)
    sth=max(vth,mh)
    #S=tw*sth+MS
    S=bw*sth
    if name=='rvt_np_nc':
        des='rvt_np_nc'
    elif name=='lvt_np_nc':
        des='lvt_np_nc'

    if vtc=='':
        return 0,0,False #表示标题高度大于区块高度，返回失败信息
    else:
        return des,S,vtc

def rvt_np_c(style,name,bw,bh,have_subtitle,count_subtitle,sub_title,count_title_char,para_char,threshold):
    S=[]
    sth=[]
    des=[]
    tw,vth,vTS,vtc=vtitle2_svt(style,bw,bh,have_subtitle,count_subtitle,sub_title,count_title_char)
    bw1=bw-tw#正文宽度为减掉竖直标题的宽度
    if vtc=='' or bw1<threshold:#表示标题高度大于区块高度或宽度无法分栏，返回失败信息
        return 0,0,False 
    else:
        scolnum,ocw,sumlc,sh,MS,cstyle=handlecolnum(vtc,bw1,para_char,threshold)
        if ocw==0 and sh==0 and MS==0 and cstyle==False and scolnum==0:#若该宽度无法分栏则返回错误信息
            return 0,0,False
        for i in range(len(MS)):
            stht=max(vth,sh[i])
            s1=tw*stht+MS[i]
            s1=stht*bw
            S.append(s1)
            if name=='rvt_np_c':
                des.append('rvt_np_%dc'%(scolnum[i]))
            elif name=='lvt_np_c':
                des.append('lvt_np_%dc'%(scolnum[i]))
            sth.append(max(vth,sh[i]))
        return des,S,cstyle

def ht_t1p_nc(style,name,bw,bh,have_subtitle,count_subtitle,sub_title,para_char,count_title_char,pic_count,pic):
    th,hTS,htv=htitle_and_sht(style,bw,have_subtitle,count_subtitle,sub_title,count_title_char)
    mh,MS=shmaintext(style,bw,para_char)
    h,PS,pstyle=fullhpic(htv,bw,pic_count,pic,1)#图片高度处理上待补充（可增加留白高度与图片高度的关系）
    sh=th+mh+h
    if sh>bh:
        return 0,0,False
    S=hTS+MS+PS
    if name=='ht_t1p_nc':
        des='ht_t1p_nc'
    elif name=='ht_b1p_nc':
        des='ht_b1p_nc'
    return des,S,pstyle

def ht_tb2p_nc(style,name,bw,bh,have_subtitle,count_subtitle,sub_title,para_char,count_title_char,pic_count,pic):
    S=[]
    pstylef=[]
    des=[]
    sth=[]
    th,hTS,htv=htitle_and_sht(style,bw,have_subtitle,count_subtitle,sub_title,count_title_char)
    mh,MS=shmaintext(style,bw,para_char)
    newpicnumarr,picarr=ditrpic(pic_count,pic,2)
    for i in range(len(newpicnumarr)):
        h1,PS1,pstyle1=fullhpic(htv,bw,newpicnumarr[i][0],picarr[i][0],1)
        h2,PS2,pstyles=fullhpic(pstyle1,bw,newpicnumarr[i][1],picarr[i][1],2)
        sh=th+mh+h1+h2
        if sh>bh:#如果高度大于区块高度，则淘汰该样式
            sth.append(0)
            S.append(0)
            des.append(0)
            pstylef.append(False)
        else:
            s1=hTS+MS+PS1+PS2
            S.append(s1)
            des.append('ht_tb2p-%d_nc'%(i))
            sth.append(sh) 
            pstylef.append(pstyles)
    return des,S,pstylef

def ht_l1p_nc(style,name,bw,bh,have_subtitle,count_subtitle,sub_title,para_char,count_title_char,pic_count,pic):
    th,hTS,htv=htitle_and_sht(style,bw,have_subtitle,count_subtitle,sub_title,count_title_char)
    bw1=0.5*bw-1.5 #待修改minipage中
    mh,MS=shmaintext(style,bw1,para_char)
    ph,PS,pstyle=fullvpic(htv,bw1,pic_count,pic,1)
    maxh=max(mh,ph)#获得图片与文本的最大高度
    sumh=maxh+th
    S=hTS+sumh*bw
    if name=='ht_l1p_nc':
        des='ht_l1p_nc'
    elif name=='ht_r1p_nc':
        des='ht_r1p_nc'
    if sumh>bh:
        return 0,0,False
    return des,S,pstyle
    
def ht_tl2p_nc(style,name,bw,bh,have_subtitle,count_subtitle,sub_title,para_char,count_title_char,pic_count,pic):
    S=[]
    pstylef=[]
    sth=[]
    des=[]
    th,hTS,htv=htitle_and_sht(style,bw,have_subtitle,count_subtitle,sub_title,count_title_char)
    bw1=0.5*bw-1.5#获得文字区域宽度
    mh,MS=shmaintext(style,bw1,para_char)
    newpicnumarr,picarr=ditrpic(pic_count,pic,2)
    for i in range(len(newpicnumarr)):
        h1,PS1,pstyle1=fullhpic(htv,bw,newpicnumarr[i][0],picarr[i][0],1)
        h2,PS2,pstyles=fullvpic(pstyle1,bw1,newpicnumarr[i][1],picarr[i][1],2)
        maxh=max(h2,mh)
        sumh=maxh+th+h1
        if sumh>bh:
            des.append(0)
            sth.append(0)
            S.append(0)
            pstylef.append(False)
        else:
            s1=hTS+maxh*bw+PS1
            sth.append(sumh)
            if name=='ht_tl2p_nc':
                des.append('ht_tl2p-%d_nc'%(i))
            elif name=='ht_bl2p_nc':
                des.append('ht_bl2p-%d_nc'%(i))
            elif name=='ht_tr2p_nc':
                des.append('ht_tr2p-%d_nc'%(i))
            elif name=='ht_br2p_nc':
                des.append('ht_br2p-%d_nc'%(i))
            S.append(s1)
            pstylef.append(pstyles)
    return des,S,pstylef

def ht_tlb3p_nc(style,name,bw,bh,have_subtitle,count_subtitle,sub_title,para_char,count_title_char,pic_count,pic):
    S=[]
    pstylef=[]
    sth=[]
    des=[]
    th,hTS,htv=htitle_and_sht(style,bw,have_subtitle,count_subtitle,sub_title,count_title_char)
    bw1=0.5*bw-1.5#获得文字区域宽度
    mh,MS=shmaintext(style,bw1,para_char)
    newpicnumarr,picarr=ditrpic(pic_count,pic,3)
    for i in range(len(newpicnumarr)):
        h1,PS1,pstyle1=fullhpic(htv,bw,newpicnumarr[i][0],picarr[i][0],1)
        h2,PS2,pstyle2=fullvpic(pstyle1,bw1,newpicnumarr[i][1],picarr[i][1],2)
        h3,PS3,pstyles=fullhpic(pstyle2,bw,newpicnumarr[i][2],picarr[i][2],3)
        maxh=max(h2,mh)
        sumh=th+h1+maxh+h3
        if sumh>bh:
            des.append(0)
            sth.append(0)
            S.append(0)
            pstylef.append(False)
        else:
            s1=hTS+PS1+PS3+maxh*bw
            if name=='ht_tlb3p_nc':
                des.append('ht_tlb3p-%d_nc'%(i))
            elif name=='ht_trb3p_nc':
                des.append('ht_trb3p-%d_nc'%(i))
            sth.append(sumh)
            S.append(s1)
            pstylef.append(pstyles)
    return des,S,pstylef

def vwt_t1p_nc(style,name,bw,bh,have_subtitle,count_subtitle,sub_title,para_char,count_title_char,pic_count,pic):
    S=[]
    pstyle=[]
    sth=[]
    des=[]
    tw,vth,vTS,vtc=vtitle1_svt(style,bw,bh,have_subtitle,count_subtitle,sub_title,count_title_char)
    #mh,MS=shmaintext(style,bw,para_char)
    mh,MS=vwmaintext(style,bw,tw,vth,para_char)
    mh_test,MS1=shmaintext(style,bw-tw,para_char)
    if vtc=='' or mh_test<vth:
        return 0,0,False #表示标题高度大于区块高度，返回失败信息
    else:
        h1,PS1,pstyle1=fullhpic(vtc[0],bw,pic_count,pic,1)
        h2,PS2,pstyle2=fullhpic(vtc[1],bw,pic_count,pic,1)
        #S.append(vTS[0]+MS+PS1)
        #S.append(vTS[1]+MS+PS2)
        S.append(MS+PS1)
        S.append(MS+PS2)
        sth.append((MS+PS1)/bw)
        sth.append((MS+PS2)/bw)
        #sth.append((vTS[0]+MS+PS1)/bw)
        #sth.append((vTS[1]+MS+PS2)/bw)
        if name=='vwt_t1p_nc':
            des.append('vwrt_t1p_nc')
            des.append('vwlt_t1p_nc')
        elif name=='vwt_b1p_nc':
            des.append('vwrt_b1p_nc')
            des.append('vwlt_b1p_nc')
        pstyle.append(pstyle1)
        pstyle.append(pstyle2)
    return des,S,pstyle

def vwt_tb2p_nc(style,name,bw,bh,have_subtitle,count_subtitle,sub_title,para_char,count_title_char,pic_count,pic):
    S=[]
    sth=[]
    pstyle=[]
    des=[]
    tw,vth,vTS,vtc=vtitle1_svt(style,bw,bh,have_subtitle,count_subtitle,sub_title,count_title_char)
    #mh,MS=shmaintext(style,bw,para_char)
    mh,MS=vwmaintext(style,bw,tw,vth,para_char)
    mh_test,MS1=shmaintext(style,bw-tw,para_char)
    if vtc=='' or mh_test<vth:
        return 0,0,False #表示标题高度大于区块高度，返回失败信息
    else:
        newpicnumarr,picarr=ditrpic(pic_count,pic,2)
        for i in range(len(newpicnumarr)):
            #左标题
            h1,PS1,pstyle1=fullhpic(vtc[0],bw,newpicnumarr[i][0],picarr[i][0],1)
            h2,PS2,pstyle2=fullhpic(pstyle1,bw,newpicnumarr[i][1],picarr[i][1],2)
            #右标题
            h3,PS3,pstyle3=fullhpic(vtc[1],bw,newpicnumarr[i][0],picarr[i][0],1)
            h4,PS4,pstyle4=fullhpic(pstyle3,bw,newpicnumarr[i][1],picarr[i][1],2)
            #S.append(vTS[0]+MS+PS1+PS2)
            #S.append(vTS[1]+MS+PS3+PS4)
            S.append(MS+PS1+PS2)
            S.append(MS+PS3+PS4)
            sth.append((vTS[0]+MS+PS1+PS2)/bw)
            sth.append((vTS[1]+MS+PS3+PS4)/bw)
            des.append('vwrt_tb2p_nc')
            des.append('vwlt_tb2p_nc')
            pstyle.append(pstyle2)
            pstyle.append(pstyle4)
    return des,S,pstyle

def ht_t1p_c(style,name,bw,bh,have_subtitle,count_subtitle,sub_title,para_char,count_title_char,pic_count,pic,threshold):
    S=[]
    sth=[]
    des=[]
    th,hTS,htv=htitle_and_sht(style,bw,have_subtitle,count_subtitle,sub_title,count_title_char)
    h,PS,pstyle=fullhpic(htv,bw,pic_count,pic,1)
    if bw<threshold:#判断区块宽度能否分栏
        return 0,0,False
    scolnum,ocw,sumlc,sh,MS,cstyle=handlecolnum(pstyle,bw,para_char,threshold)
    if ocw==0 and sh==0 and MS==0 and cstyle==False and scolnum==0:#若该宽度无法分两栏则返回错误信息
        return 0,0,False
    for i in range(len(MS)):
        s1=hTS+MS[i]+PS
        sth.append(th+h+sh[i])
        if name=='ht_t1p_c':
            des.append('ht_t1p_%dc'%(scolnum[i]))
        elif name=='ht_b1p_c':
            des.append('ht_b1p_%dc'%(scolnum[i]))
        S.append(s1)
    return des,S,cstyle

def ht_tb2p_c(style,name,bw,bh,have_subtitle,count_subtitle,sub_title,para_char,count_title_char,pic_count,pic,threshold):
    S=[]
    PS=[]
    sth=[]
    des=[]
    ph=[]#图片区域的高度
    pstyle=[]#插入图片后的样式集合
    cstyle=[]#插图分栏后图片样式的集合
    th,hTS,htv=htitle_and_sht(style,bw,have_subtitle,count_subtitle,sub_title,count_title_char)
    #获得图片样式
    newpicnumarr,picarr=ditrpic(pic_count,pic,2)
    for i in range(len(newpicnumarr)):
        h1,PS1,pstyle1=fullhpic(htv,bw,newpicnumarr[i][0],picarr[i][0],1)
        h2,PS2,pstylef=fullhpic(pstyle1,bw,newpicnumarr[i][1],picarr[i][1],2)
        ph.append(h1+h2)
        pstyle.append(pstylef)
        sps=PS1+PS2
        PS.append(sps)
    #循环处理分栏
    if bw<threshold:#判断区块宽度能否分栏
        return 0,0,False
    for i in range(len(pstyle)):
        scolnum,ocw,sumlc,sh,MS,cstyles=handlecolnum(pstyle[i],bw,para_char,threshold)
        if ocw==0 and sh==0 and MS==0 and cstyles==False and scolnum==0:#若该宽度无法分两栏则返回错误信息
            des.append(0)
            sth.append(0)
            S.append(0)
            cstyle.append(False)
            continue #若无法分栏则跳出循环
        for j in range(len(MS)):
            s1=hTS+MS[j]+PS[i]
            sth.append(th+ph[i]+sh[j])
            des.append('ht_tb2p_%dc'%(scolnum[i]))
            S.append(s1)
            cstyle.append(cstyles[j])
    return des,S,cstyle

def ht_r1p_c(style,name,bw,bh,have_subtitle,count_subtitle,sub_title,para_char,count_title_char,pic_count,pic,threshold):
    S=[]
    cstyle=[]
    sth=[]
    des=[]
    th,hTS,htv=htitle_and_sht(style,bw,have_subtitle,count_subtitle,sub_title,count_title_char)
    bw1=0.5*bw-1.5 
    ph,PS,pstyle=fullvpic(htv,bw1,pic_count,pic,1)
    if bw1<threshold:#判断区块宽度能否分栏
        return 0,0,False
    scolnum,ocw,sumlc,sh,MS,cstyle1=handlecolnum(pstyle,bw1,para_char,threshold)
    if ocw==0 and sh==0 and MS==0 and cstyle1==False and scolnum==0:#若该宽度无法分两栏则返回错误信息
        return 0,0,False
    for i in range(len(MS)):
        maxh=max(sh[i],ph)
        ssh=maxh+th#总高度
        if ssh>bh:
            des.append(0)
            sth.append(0)
            S.append(0)
            cstyle.append(False)
        else:
            s1=hTS+maxh*bw
            S.append(s1)
            sth.append(ssh)
            if name=='ht_r1p_c':
                des.append('ht_r1p_%dc'%(scolnum[i]))
            elif name=='ht_l1p_c':
                des.append('ht_l1p_%dc'%(scolnum[i]))
            cstyle.append(cstyle1[i])
    return des,S,cstyle

def ht_tr2p_c(style,name,bw,bh,have_subtitle,count_subtitle,sub_title,para_char,count_title_char,pic_count,pic,threshold):
    S=[]
    sth=[]
    des=[]
    cstyle=[]
    th,hTS,htv=htitle_and_sht(style,bw,have_subtitle,count_subtitle,sub_title,count_title_char)
    bw1=0.5*bw-1.5 
    if bw1<threshold:#判断区块宽度能否分栏
        return 0,0,False
    newpicnumarr,picarr=ditrpic(pic_count,pic,2)
    for i in range(len(newpicnumarr)):
        ph1,PS1,pstyle1=fullhpic(htv,bw,newpicnumarr[i][0],picarr[i][0],1)
        ph2,PS2,pstylef1=fullvpic(pstyle1,bw1,newpicnumarr[i][1],picarr[i][1],2)
        scolnum,ocw,sumlc,sh,MS,cstyle1=handlecolnum(pstylef1,bw1,para_char,threshold)
        if ocw==0 and sh==0 and MS==0 and cstyle1==False and scolnum==0:#若该宽度无法分两栏则返回错误信息
            des.append(0)
            S.append(0)
            sth.append(0)
            cstyle.append(False)
            continue
        for i in range(len(sh)):
            maxh=max(sh[i],ph2)
            ssh=maxh+th+ph1#总高度
            if ssh>bh:
                des.append(0)
                sth.append(0)
                S.append(0)
                cstyle.append(False)
            else:
                s1=hTS+PS1+maxh*bw
                sth.append(ssh)
                if name=='ht_tr2p_c':
                    des.append('ht_tr2p_%dc'%(scolnum[i]))
                elif name=='ht_br2p_c':
                    des.append('ht_br2p_%dc'%(scolnum[i]))
                elif name=='ht_tl2p_c':
                    des.append('ht_tl2p_%dc'%(scolnum[i]))
                elif name=='ht_bl2p_c':
                    des.append('ht_bl2p_%dc'%(scolnum[i]))
                S.append(s1)
                cstyle.append(cstyle1[i])
    return des,S,cstyle

def ht_tlb3p_c(style,name,bw,bh,have_subtitle,count_subtitle,sub_title,para_char,count_title_char,pic_count,pic,threshold):
    S=[]
    sth=[]
    cstyle=[]
    des=[]
    th,hTS,htv=htitle_and_sht(style,bw,have_subtitle,count_subtitle,sub_title,count_title_char)
    bw1=0.5*bw-1.5
    if bw1<threshold:#判断区块宽度能否分栏
        return 0,0,False 
    newpicnumarr,picarr=ditrpic(pic_count,pic,2)
    for i in range(len(newpicnumarr)):
        ph1,PS1,pstyle1=fullhpic(htv,bw,newpicnumarr[i][0],picarr[i][0],1)
        ph2,PS2,pstyle2=fullvpic(pstyle1,bw1,newpicnumarr[i][1],picarr[i][1],2)
        ph3,PS3,pstylef=fullhpic(pstyle2,bw,newpicnumarr[i][2],picarr[i][2],3)
        scolnum,ocw,sumlc,sh,MS,cstyle1=handlecolnum(pstylef,bw1,para_char,threshold)
        if ocw==0 and sh==0 and MS==0 and cstyle1==False and scolnum==0:#若该宽度无法分两栏则返回错误信息
            des.append(0)
            S.append(0)
            sth.append(0)
            cstyle.append(False)
            continue
        for i in range(len(MS)):
            maxh=max(sh[i],ph2)
            ssh=maxh+th+ph1+ph3#总高度
            if ssh>bh:
                des.append(0)
                sth.append(0)
                S.append(0)
                cstyle.append(False)
            else:
                s1=hTS+PS1+maxh*bw+PS3
                sth.append(ssh)
                if name=='ht_tlb3p_c':
                    des.append('ht_tlb3p_%dc'%(scolnum[i]))
                elif name=='ht_trb3p_c':
                    des.append('ht_trb3p_%dc'%(scolnum[i]))
                S.append(s1)
                cstyle.append(cstyle1[i])
    return des,S,cstyle

def ht_tc1p_c(style,name,bw,bh,have_subtitle,count_subtitle,sub_title,para_char,count_title_char,pic_count,pic,threshold):
    S=[]
    sth=[]
    des=[]
    pstyle=[]
    fs,lh=mc_fs_lh(style) #正文字号、行距
    olh=lh*1.3 #行高

    th,hTS,htv=htitle_and_sht(style,bw,have_subtitle,count_subtitle,sub_title,count_title_char)
    if bw<threshold:#判断区块宽度能否分栏
        return 0,0,False
    scolnum,ocw,sumlc,sh,MS,cstyle=handlecolnum(htv,bw,para_char,threshold)
    if ocw==0 and sh==0 and MS==0 and cstyle==False and scolnum==0:#若该宽度无法分两栏则返回错误信息
        return 0,0,False
    tbh=bh-th #区块高度减去标题高度
    for i in range(len(MS)):
        ph,PS,pstyle1=colpic(cstyle[i],tbh,ocw[i],pic)
        if ph==0 and PS==0 and pstyle1==False: #即图片高度大于剩余高度时赋值0
            sth.append(0)
            S.append(0)
            des.append(0)
            pstyle.append(False)
            continue
        nh=(sh[i]*scolnum[i]+ph)/scolnum[i]#加入图片后的文本高度
        if nh<ph: #当图片高度大于计算的栏高时
            olc=round(ph/olh) #一栏的行数
            rcolnum=math.ceil(sumlc[i]/olc) #实际栏数
            nh=ph
            if rcolnum<scolnum[i]: #文字太少无法分成多栏
                sth.append(0)
                S.append(0)
                des.append(0)
                pstyle.append(False)
                continue
            elif rcolnum==scolnum[i]:
                rest_lc=sumlc-olc*(scolnum[i]-1) #最后一栏的空白区域所占行数
            
        #s1=hTS+MS[i]+PS
        s1=hTS+nh*bw
        sth.append(th+nh)
        S.append(s1)
        if name=='ht_tc1p_c':
            des.append('ht_tc1p_%dc'%(scolnum[i]))
        elif name=='ht_bc1p_c':
            des.append('ht_bc1p_%dc'%(scolnum[i]))
        pstyle.append(pstyle1)
    return des,S,pstyle

def ht_ttc2p_c(style,name,bw,bh,have_subtitle,count_subtitle,sub_title,para_char,count_title_char,pic_count,pic,threshold):
    S=[]
    sth=[]
    pstyle=[]
    des=[]
    #print(style)
    th,hTS,htv=htitle_and_sht(style,bw,have_subtitle,count_subtitle,sub_title,count_title_char)
    h,PS1,pstyle1=fullhpic(htv,bw,pic_count-1,pic[1:pic_count],1)
    if bw<threshold:#判断区块宽度能否分栏
        return 0,0,False
    scolnum,ocw,sumlc,sh,MS,cstyle=handlecolnum(pstyle1,bw,para_char,threshold)
    if ocw==0 and sh==0 and MS==0 and cstyle==False and scolnum==0:#若该宽度无法分两栏则返回错误信息
        return 0,0,False
    tbh=bh-th-h
    for i in range(len(MS)):
        ph,PS2,pstyle2=colpic(cstyle[i],tbh,ocw[i],[pic[0]])
        nh=(sh[i]*scolnum[i]+ph)/scolnum[i]#加入图片后的文本高度
        ssh=th+h+nh
        if ph==0 and PS2==0 and pstyle2==False or ssh>bh:
            sth.append(0)
            S.append(0)
            des.append(0)
            pstyle.append(False)
            continue
        else:
            s1=hTS+MS[i]+PS1+PS2
            sth.append(ssh)
            if name=='ht_ttc2p_c':
                des.append('ht_ttc2p_%dc'%(scolnum[i]))
            elif name=='ht_tbc2p_c':
                des.append('ht_tbc2p_%dc'%(scolnum[i]))
            elif name=='ht_tcb2p_c':
                des.append('ht_tcb2p_%dc'%(scolnum[i]))
            elif name=='ht_bcb2p_c':
                des.append('ht_bcb2p_%dc'%(scolnum[i]))
            S.append(s1)
            pstyle.append(pstyle2)
    return des,S,pstyle

def ht_ttcbc3p_c(style,name,bw,bh,have_subtitle,count_subtitle,sub_title,para_char,count_title_char,pic_count,pic,threshold):
    S=[]
    sth=[]
    des=[]
    pstyle=[]
    th,hTS,htv=htitle_and_sht(style,bw,have_subtitle,count_subtitle,sub_title,count_title_char)
    h,PS1,pstyle1=fullhpic(htv,bw,pic_count-2,pic[2:pic_count],1)
    if bw<threshold:#判断区块宽度能否分栏
        return 0,0,False
    scolnum,ocw,sumlc,sh,MS,cstyle=handlecolnum(pstyle1,bw,para_char,threshold)
    if ocw==0 and sh==0 and MS==0 and cstyle==False and scolnum==0:#若该宽度无法分两栏则返回错误信息
        return 0,0,False
    tbh=bh-th-h
    for i in range(len(MS)):
        ph,PS2,pstyle2=colpic(cstyle[i],tbh,ocw[i],[pic[0],pic[1]])
        nh=(sh[i]*scolnum[i]+ph)/scolnum[i]#加入图片后的文本高度
        ssh=th+h+nh
        if ph==0 and PS2==0 and pstyle2==False or ssh>bh:
            sth.append(0)
            S.append(0)
            des.append(0)
            pstyle.append(False)
            continue
        else:
            s1=hTS+MS[i]+PS1+PS2
            S.append(s1)
            if name=='ht_ttcbc3p_c':
                des.append('ht_ttcbc3p_%dc'%(scolnum[i]))
            elif name=='ht_btcbc3p_c':
                des.append('ht_btcbc3p_%dc'%(scolnum[i]))
            sth.append(ssh)
            pstyle.append(pstyle2)
    return des,S,pstyle

def ht_tcbc2p_c(style,name,bw,bh,have_subtitle,count_subtitle,sub_title,para_char,count_title_char,pic_count,pic,threshold):
    S=[]
    sth=[]
    des=[]
    pstyle=[]
    #print(style)
    th,hTS,htv=htitle_and_sht(style,bw,have_subtitle,count_subtitle,sub_title,count_title_char)
    #print(th,hTS,htv)
    if bw<threshold:#判断区块宽度能否分栏
        return 0,0,False
    scolnum,ocw,sumlc,sh,MS,cstyle=handlecolnum(htv,bw,para_char,threshold)
    if ocw==0 and sh==0 and MS==0 and cstyle==False and scolnum==0:#若该宽度无法分两栏则返回错误信息
        return 0,0,False
    tbh=bh-th
    for i in range(len(MS)):
        ph,PS2,pstyle2=colpic(cstyle[i],tbh,ocw[i],pic)
        nh=(sh[i]*scolnum[i]+ph)/scolnum[i]#加入图片后的文本高度
        ssh=th+nh
        if ph==0 and PS2==0 and pstyle2==False or ssh>bh:
            sth.append(0)
            S.append(0)
            des.append(0)
            pstyle.append(False)
            continue
        else:
            s1=hTS+MS[i]+PS2
            S.append(s1)
            sth.append(ssh)
            des.append('ht_tcbc2p_%dc'%(scolnum[i]))
            pstyle.append(pstyle2)
    return des,S,pstyle

def ht_tbtcbc4p_c(style,name,bw,bh,have_subtitle,count_subtitle,sub_title,para_char,count_title_char,pic_count,pic,threshold):
    S=[]
    sth=[]
    des=[]
    pstylef=[]
    th,hTS,htv=htitle_and_sht(style,bw,have_subtitle,count_subtitle,sub_title,count_title_char) 
    if bw<threshold:#判断区块宽度能否分栏
        return 0,0,False
    newpicnumarr,picarr=ditrpic(pic_count-2,pic[2::],2)
    for i in range(len(newpicnumarr)):
        h1,PS1,pstyle1=fullhpic(htv,bw,newpicnumarr[i][0],picarr[i][0],1)
        h2,PS2,pstyles=fullhpic(pstyle1,bw,newpicnumarr[i][1],picarr[i][1],2)
        scolnum,ocw,sumlc,sh,MS,cstyle=handlecolnum(pstyles,bw,para_char,threshold)
        #print(scolnum,ocw,sh,MS,cstyle)
        if ocw==0 and sh==0 and MS==0 and cstyle==False and scolnum==0:#若该宽度无法分两栏则返回错误信息
            return 0,0,False
        tbh=bh-h1-h2-th
        for j in range(len(MS)):
            ph,PS3,pstyle2=colpic(cstyle[j],tbh,ocw[j],pic[0:2])
            nh=(sh[j]*scolnum[j]+ph)/scolnum[j]#加入图片后的文本高度
            ssh=th+nh+h1+h2
            #print(nh)
            if ssh>bh or ph==0 and PS3==0 and pstyle2==False:#如果高度大于区块高度，则淘汰该样式
                des.append(0)
                sth.append(0)
                S.append(0)
                pstylef.append(False)
            else:
                s1=hTS+MS[i]+PS1+PS2+PS3
                S.append(s1)
                des.append('ht_tbtcbc4p-%d_%dc'%(j,i))
                sth.append(ssh)
                pstylef.append(pstyle2)
    return des,S,pstylef

def vt_mt1p_nc(style,name,bw,bh,have_subtitle,count_subtitle,sub_title,para_char,count_title_char,pic_count,pic):
    tw,vth,vTS,vtc=vtitle2_svt(style,bw,bh,have_subtitle,count_subtitle,sub_title,count_title_char)
    h,PS,pstyle=fullhpic(vtc,bw,pic_count,pic,1)
    bw1=bw-tw
    mh,MS=shmaintext(style,bw1,para_char)
    maxh=max(vth,mh)
    sh=maxh+h
    if name=='vt_mt1p_nc':
        des='vt_mt1p_nc'
    elif name=='vt_mb1p_nc':
        des='vt_mb1p_nc'
    if vtc=='' or sh>bh:
        return 0,0,False #表示标题高度大于区块高度，返回失败信息
    else:
        S=sh*bw 
        return des,S,pstyle

def picnews_vertical_nc(style,bw,bh,pic_count,pic):
    pattern=r"(?<=righthand width=).*(?=\\textwidth)"
    radio=re.findall(pattern,style)[0] #图片文字分割比例
    radio=float(radio)
    top,bottom,left,right=tblr_space(style)
    bw1=(bw-left-right)*radio
    ph,PS,pstyle=fullvpic(style,bw1,pic_count,pic,1)
    #print(ph,PS,pstyle)
    #判断图片高度与新闻块高度的对比处理
    des='picnews_verticle_nc'
    S=ph*bw
    return des,S,pstyle

def picnews_lt_horizontal_nc(style,bw,bh,pic_count,pic,para_char):
    pattern=r"(?<=\%title\n\\begin\{minipage\}\{).*(?=\\textwidth)"
    radio=re.findall(pattern,style)[0]#正文与标题的分割比例
    radio=float(radio)

    top,bottom,left,right=tblr_space(style)
    pattern5=r"(?<=vspace\{).*(?=mm\})"
    vspace=float(re.findall(pattern5,style)[0])
    #print(vspace)
    bw1=bw*(1-radio)-left-right
    mh,MS=shmaintext(style,bw1,para_char)
    h,PS,pstyle=fullhpic(style,bw,pic_count,pic,1)
    sumh=h+top+bottom+vspace+mh #总的图片新闻的高度
    des='picnews_lt_horizontal_nc'
    S=bw*sumh
    return des,S,pstyle

def picnews_ht_horizontal_nc(style,bw,bh,pic_count,pic,para_char):
    pt=0.35
    top,bottom,left,right=tblr_space(style)
    pattern=r"(?<=vspace\{).*(?=mm\})"
    vspace=re.findall(pattern,style)
    vspace=[float(x) for x in vspace] #图片与标题、标题与正文的间距
    #print(vspace)

    #获取标题字号
    pattern1=r"(?<=\\fontsize\{).*(?=\}\\selectfont \*mt)"
    fontsize=re.findall(pattern1,style)
    fslh=fontsize[0].replace('{','').split('}') 
    fs=int(fslh[0])*pt#字号
    lh=int(fslh[1])*pt#行距
    #print(fs)

    h,PS,pstyle=fullhpic(style,bw,pic_count,pic,1)
    des='picnews_ht_horizontal_nc'
    bw1=bw-left-right
    mh,MS=shmaintext(style,bw1,para_char)
    sumh=top+bottom+h+np.sum(vspace)+fs+mh
    S=sumh*bw
    #print(sumh)
    return des,S,pstyle

def ht_betpic1cp_c():
    pass                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
    
if __name__ == "__main__":
    '''
    style1=r"%%subtitle1#{\centering\heiti{\fontsize{21}{0}\selectfont *s1\par}}#\vspace{3mm}#%maintitle#{\centering\syht{\fontsize{48}{0}\selectfont *mt\par}}#%%subtitle2#\vspace{3mm}#{\centering\heiti{\fontsize{21}{0}\selectfont *s2\par}}#\vspace{5mm}#{\songti{\fontsize{9}{10}\selectfont *mc\par}}\par"
    style1f=style1.replace('#','\n')
    style2=r"\begingroup#\setlength{\columnsep}{0pt}#\begin{wrapfigure}{r}{99pt}#\begin{tikzpicture}[scale=1]#\node[rectangle,text width =42pt] (a)#{\heiti{\bfseries\fontsize{42}{32}\selectfont  *mt\par}};#%righttitle\node[right =0pt of a,rectangle,text width =21pt]#%righttitle{\heiti{\bfseries\fontsize{21}{17}\selectfont  *s1\par}};#%lefttitle\node[left =0pt of a,rectangle,text width =21pt]#%lefttitle{\heiti{\bfseries\fontsize{21}{17}\selectfont *s2\par}};#\end{tikzpicture}\par#\vspace{-\baselineskip}# \end{wrapfigure}##{\songti{\fontsize{9}{10}\selectfont *mc\par}}\par#\endgroup"
    style2f=style2.replace('#','\n')
    style3=r'%%subtitile1#{\centering\heiti{\fontsize{21}{0}\selectfont *s1\par}}#\vspace{3mm}#%maintitle#{\centering\syht{\fontsize{48}{0}\selectfont  *mt\par}}#%%subtitile2#\vspace{3mm}#{\centering\heiti{\fontsize{21}{0}\selectfont *s2\par}}#\vspace{5mm}#\setlength{\columnsep}{5mm}#\vspace{-\baselineskip}#\begin{multicols}{2}#{\songti{\fontsize{9}{10}\selectfont *mc\par}}\par\end{multicols}'
    style3f=style3.replace('#','\n')
    style4=r'%%subtitile1#{\centering\heiti{\fontsize{21}{0}\selectfont *s1\par}}#\vspace{3mm}#%maintitle#{\centering\syht{\fontsize{48}{0}\selectfont  *mt\par}}#%%subtitile2#\vspace{3mm}#{\centering\heiti{\fontsize{21}{0}\selectfont *s2\par}}#\vspace{5mm}#\begin{minipage}{0.5\textwidth-1.5mm}#%pic1#\end{minipage}#\hspace{3mm}#\begin{minipage}{0.5\textwidth-1.5mm}#{\songti{\fontsize{9}{10}\selectfont *mc\par}}\par#\end{minipage}'
    style4f=style4.replace('#','\n')
    style5=r'\begin{tcolorbox}#[sidebyside,sidebyside gap=0mm,lower separated=false,righthand width=95pt,halign lower=flush left,top=0mm,right=0mm,bottom=0mm,left=0mm,outer arc=0mm,arc=0mm,boxsep=0mm,opacityback=0,opacityframe=0,enhanced jigsaw]#{\songti{\fontsize{9}{10}\selectfont *mc\par}}\par#\tcblower#\begin{tikzpicture}[scale=1]#\node[rectangle,text width =42pt] (a)#{\heiti{\bfseries\fontsize{42}{32}\selectfont *mt\par}};#%righttitle\node[right =0pt of a,rectangle,text width =21pt]#%righttitle{\heiti{\bfseries\fontsize{21}{17}\selectfont *s1\par}};#%lefttitle\node[left =0pt of a,rectangle,text width =21pt]#%lefttitle{\heiti{\bfseries\fontsize{21}{17}\selectfont *s2\par}};#\end{tikzpicture}#\end{tcolorbox}'
    style5f=style5.replace('#','\n')
    style6=r'\begin{tcolorbox}#[sidebyside,sidebyside gap=0mm,lower separated=false,righthand width=95pt,halign lower=flush left,top=0mm,right=0mm,bottom=0mm,left=0mm,outer arc=0mm,arc=0mm,boxsep=0mm,opacityback=0,opacityframe=0,enhanced jigsaw]#\setlength{\columnsep}{5mm}#\begin{multicols}{2}#{\songti{\fontsize{9}{10}\selectfont *mc\par}}\par#\end{multicols}#\tcblower# \begin{tikzpicture}[scale=1]#\node[rectangle,text width =42pt] (a)#{\heiti{\bfseries\fontsize{42}{32}\selectfont *mt\par}};#%righttitle\node[right =0pt of a,rectangle,text width =21pt]#%righttitle{\heiti{\bfseries\fontsize{21}{17}\selectfont *s1\par}};#%lefttitle\node[left =0pt of a,rectangle,text width =21pt]#%lefttitle{\heiti{\bfseries\fontsize{21}{17}\selectfont *s2\par}};#\end{tikzpicture}#\end{tcolorbox}'
    style6f=style6.replace('#','\n')
    style7=r'%%subtitile1#{\centering\heiti{\fontsize{21}{0}\selectfont *s1\par}}#\vspace{3mm}#%maintitle#{\centering\syht{\fontsize{48}{0}\selectfont *mt\par}}#%%subtitile2#\vspace{3mm}#{\centering\heiti{\fontsize{21}{0}\selectfont *s2\par}}#\vspace{5mm}#%pic1#{\songti{\fontsize{9}{10}\selectfont *mc\par}}\par#%pic2'
    style7f=style7.replace('#','\n')
    style8=r'%%subtitile1#{\centering\heiti{\fontsize{21}{0}\selectfont *s1\par}}#\vspace{3mm}#%maintitle#{\centering\syht{\fontsize{48}{0}\selectfont *mt\par}}#%%subtitile2#\vspace{3mm}#{\centering\heiti{\fontsize{21}{0}\selectfont *s2\par}}#%pic1#\vspace{5mm}#\vspace{-\baselineskip}#\setlength{\columnsep}{5mm}#\begin{multicols}{2}#{\songti{\fontsize{9}{10}\selectfont *mc\par}}\par#\end{multicols}#%pic2'
    style8f=style8.replace('#','\n')
    style9=r'%%subtitile1#{\centering\heiti{\fontsize{21}{0}\selectfont *s1\par}}#\vspace{3mm}#%maintitle#{\centering\syht{\fontsize{48}{0}\selectfont *mt\par}}#%%subtitile2#\vspace{3mm}#{\centering\heiti{\fontsize{21}{0}\selectfont *s2\par}}#\vspace{5mm}#%pic1#\begin{minipage}{0.5\textwidth-1.5mm}#%pic2#\end{minipage}#\hspace{3mm}#\begin{minipage}{0.5\textwidth-1.5mm}#\setlength{\columnsep}{5mm}#\begin{multicols}{2}#{\songti{\fontsize{9}{10}\selectfont *mc\par}}#\end{multicols}#\end{minipage}'
    style9f=style9.replace('#','\n')
    style10=r'%%subtitile1#{\centering\heiti{\fontsize{21}{0}\selectfont *s1\par}}#\vspace{3mm}#%maintitle#{\centering\syht{\fontsize{48}{0}\selectfont *mt\par}}#%%subtitile2#\vspace{3mm}#{\centering\heiti{\fontsize{21}{0}\selectfont *s2\par}}#\vspace{5mm}#\vspace{-\baselineskip}#\setlength{\columnsep}{5mm}#\begin{multicols}{2}#\includegraphics[width=\columnwidth,height=0mm]{*ct}\par#{\songti{\fontsize{9}{10}\selectfont *mc\par}}\par#\includegraphics[width=\columnwidth,height=0mm]{*cb}\par#\end{multicols}'
    style10f=style10.replace('#','\n')
    style11=r'%%subtitile1#{\centering\heiti{\fontsize{21}{0}\selectfont *s1\par}}#\vspace{3mm}#%maintitle#{\centering\syht{\fontsize{48}{0}\selectfont *mt\par}}#%%subtitile2#\vspace{3mm}#{\centering\heiti{\fontsize{21}{0}\selectfont *s2\par}}#\vspace{5mm}#\vspace{-\baselineskip}#\setlength{\columnsep}{5mm}#\begin{multicols}{2}#\includegraphics[width=\columnwidth,height=0mm]{*ct}\par#{\songti{\fontsize{9}{10}\selectfont *mc\par}}\par#\end{multicols}#%pic1'
    style11f=style11.replace('#','\n')
    xx=r'\begin{tcolorbox}#[sidebyside,sidebyside gap=0mm,lower separated=false,righthand width=95pt,halign lower=flush left,top=0mm,right=0mm,bottom=0mm,left=0mm,outer arc=0mm,arc=0mm,boxsep=0mm,opacityback=0,opacityframe=0,enhanced jigsaw]#{\songti{\fontsize{9}{10}\selectfont *mc\par}}\par#\tcblower#\begin{tikzpicture}[scale=1]#\node[rectangle,text width =42pt] (a)#{\heiti{\bfseries\fontsize{42}{32}\selectfont *mt\par}};#%righttitle\node[right =0pt of a,rectangle,text width =21pt]#%righttitle{\heiti{\bfseries\fontsize{21}{17}\selectfont *s2\par}};#%lefttitle\node[left =0pt of a,rectangle,text width =21pt]#%lefttitle{\heiti{\bfseries\fontsize{21}{17}\selectfont *s1\par}};#\end{tikzpicture}#\end{tcolorbox}'
    yy=xx.replace('#','\n')


    #print(style6f)
    mh,hts,htv=htitle_and_sht(style1f,400,True,1,['','我是测试啊啊啊啊'],7)
    print(mh,hts,htv)
    #print(style5f)
    tw,vth,x1,y1=vtitle1_svt(style2f,90.5,164.208,False,0,['',''],3)
    #print(x1,y1)
    u1,f,g=vwt_np_nc(style2f,'g',50,400,False,0,['',''],7,[440,167])
    #print(f,g)

    mh,MS=vwmaintext(style2f,62.85,17.5,96.46,[112,187,352])
    #print('MS',mh,MS)

    b1,x1,y1,z1,d1,a1=handlecolnum(style6f,100,[350,100],30)
    #print(x1,y1,z1)
    s=['','好哒卡,粉浮粉']
    #print(len(s[1]))
    u3,s1,s2=ht_tb2p_nc(style7f,'j',200,400,True,1,['','我是测试啊啊啊啊'],[32,200],7,5,[[5,3,'./img/jh2_image1.jpeg'],[5,3,'./img/newstitle.png'],[5,3,'./img/jh2_image1.jpeg'],[5,3,'./img/jh2_image4.jpeg'],[5,3,'./img/jh2_image5.jpeg']])
    #print(s1,s2[0],s2[1])
    
    u4,r1,r2=ht_tb2p_c(style8f,'j',300,500,True,1,['','我是测试啊啊啊啊'],[32,200],6,3,[[5,3,'./img/jh2_image1.jpeg'],[5,3,'./img/newstitle.png'],[5,3,'']],40)
    #print(r1,r2)
    u5,r3,r4=ht_tr2p_c(style9f,'j',200,300,True,1,['','我是测试啊啊啊啊'],[32,200],7,3,[[2,1,'./img/jh2_image1.jpeg'],[5,3,'./img/newstitle.png'],[10,5,'./img/newstitle3.png']],40)
    #print(r3,r4[0],r4[1])

    tt1,tt2,tt3=fullvpic(style9f,200,3,[[2,1,'./img/jh2_image1.jpeg'],[5,3,'./img/newstitle.png'],[10,5,'./img/newstitle3.png']],2)#这里的bw为minipage的宽度
    #print(tt1,tt2,tt3)

    b,x,y,z,a,d=handlecolnum(style3f,100,[350,100],15)
    #print(x,y,z)
    h,ps,x2=fullhpic(style1f,100,3,[[5,3,'./img/jh2_image1.jpeg'],[5,3,'./img/jh2_image1.jpeg'],[5,3,'']],1)
    #print(ps,x2)

    a1,a2,a3=colpic(style10f,100,30,[[5,3,'./img/jh2_image1.jpeg'],[5,3,'./img/jh2_image1.jpeg']])
    #print(a1,a2,a3)

    pic=[[50,30,'./img/jh2_image1.jpeg'],[50,30,'./img/jh2_image2.jpeg']]
    #print(pic[0:2])

    u6,b1,b2=ht_ttc2p_c(style11f,'j',200,300,True,1,['','我是测试啊啊啊啊'],[32,200],7,3,[[5,3,'./img/jh2_image1.jpeg'],[5,3,'./img/newstitle.png'],[5,3,'./img/newstitle1.png']],40)
    #print(b1,b2[0],'\n',b2[1])
    '''
    '''
    ss=r'\includegraphics[width=\columnwidth,height=0mm]{*ct}'
    pattern1=r'(?<=includegraphics\[width=\\columnwidth,height=).*(?=mm])'
    v = re.findall(pattern1,style10f)
    print(v)
    
    pattern=r"(?<=minipage\}\{).*(?=\}\n%pic)"
    v = re.findall(pattern,style4f)
    #print(v)
    maxh=max(4,3)
    print(maxh)
    '''
    
    '''
    str2=r'%%subtitile1#{\centering\heiti{\fontsize{21}{0}\selectfont *s1\par}}#\vspace{3mm}#%maintitle#{\centering\syht{\fontsize{48}{0}\selectfont *mt\par}}#%%subtitile2#\vspace{3mm}#{\centering\heiti{\fontsize{21}{0}\selectfont *s2\par}}#\vspace{5mm}#%pic1#\begin{minipage}{0.5\textwidth-1.5mm}#%pic2#\end{minipage}#\hspace{3mm}#\begin{minipage}{0.5\textwidth-1.5mm}#{\songti{\fontsize{9}{10}\selectfont *mc\par}}\par#\end{minipage}#%pic3'
    st2f=str2.replace('#','\n')
    u7,xxx2,yyy2=ht_tlb3p_nc(st2f,'j',200,400,True,1,['','我是测试啊啊啊啊'],[32,200],7,5,[[5,3,'./img/jh2_image1.jpeg'],[5,3,'./img/newstitle.png'],[5,3,'./img/jh2_image1.jpeg'],[5,3,'./img/jh2_image4.jpeg'],[5,3,'./img/jh2_image5.jpeg']])
    #print(yyy2[0])
    #print(yyy2[1])
    #print(yyy2[2])
    st3=r'\begin{tcolorbox}#[sidebyside,sidebyside gap=0mm,lower separated=false,righthand width=95pt,halign lower=flush left,top=0mm,right=0mm,bottom=0mm,left=0mm,outer arc=0mm,arc=0mm,boxsep=0mm,opacityback=0,opacityframe=0,enhanced jigsaw]#{\songti{\fontsize{9}{10}\selectfont *mc\par}}\par#\tcblower#\begin{tikzpicture}[scale=1]#\node[rectangle,text width =42pt] (a)#{\heiti{\bfseries\fontsize{42}{32}\selectfont *mt\par}};#%righttitle\node[right =0pt of a,rectangle,text width =21pt]#%righttitle{\heiti{\bfseries\fontsize{21}{17}\selectfont *s2\par}};#%lefttitle\node[left =0pt of a,rectangle,text width =21pt]#%lefttitle{\heiti{\bfseries\fontsize{21}{17}\selectfont *s1\par}};#\end{tikzpicture}#\end{tcolorbox}'
    st3f=st3.replace('#','\n')

    str4=r'%%subtitile1#{\centering\heiti{\fontsize{21}{0}\selectfont *s1\par}}#\vspace{3mm}#%maintitle#{\centering\syht{\fontsize{48}{0}\selectfont *mt\par}}#%%subtitile2#\vspace{3mm}#{\centering\heiti{\fontsize{21}{0}\selectfont *s2\par}}#\vspace{5mm}#\vspace{-\baselineskip}#%pic1#\setlength{\columnsep}{5mm}#\begin{multicols}{2}#\includegraphics[width=\columnwidth,height=0mm]{*ct}\par#{\songti{\fontsize{9}{10}\selectfont *mc\par}}\par#\includegraphics[width=\columnwidth,height=0mm]{*cb}\par#\end{multicols}#%pic2'
    str4f=str4.replace('#','\n')
    u8,xxx3,yyy3=ht_tbtcbc4p_c(str4f,'j',200,500,True,1,['','我是测试啊啊啊啊'],[32,200],7,5,[[5,3,'./img/jh2_image1.jpeg'],[5,3,'./img/newstitle.png'],[5,3,'./img/newstitle1.png'],[5,3,'./img/jh2_image4.jpeg'],[5,3,'./img/jh2_image5.jpeg']],40)
    #print(xxx3,yyy3[0],yyy3[1],yyy3[2],yyy3[3],yyy3[4],yyy3[5])

    str5=r'%%subtitile1#{\centering\heiti{\fontsize{21}{0}\selectfont *s1\par}}#\vspace{3mm}#%maintitle#{\centering\syht{\fontsize{48}{0}\selectfont *mt\par}}#%%subtitile2#\vspace{3mm}#{\centering\heiti{\fontsize{21}{0}\selectfont *s2\par}}#\vspace{5mm}#\vspace{-\baselineskip}#\setlength{\columnsep}{5mm}#\begin{multicols}{2}#\includegraphics[width=\columnwidth,height=0mm]{*ct}\par#{\songti{\fontsize{9}{10}\selectfont *mc\par}}\par#\includegraphics[width=\columnwidth,height=0mm]{*cb}\par#\end{multicols}'
    str5f=str5.replace('#','\n')
    u9,xxx4,yyy4=ht_tcbc2p_c(str5f,'j',100,200,False,0,['',''],[32,200],7,2,[[5,3,'./img/jh2_image1.jpeg'],[5,3,'./img/newstitle.png']],40)
    #print(xxx4,yyy4)
    #print(yyy4[0])
    #print(yyy4[1])

    str6=r'%pic1#\begin{tcolorbox}#[sidebyside,sidebyside gap=0mm,lower separated=false,lefthand width=95pt,halign lower=flush left,top=0mm,right=0mm,bottom=0mm,left=0mm,outer arc=0mm,arc=0mm,boxsep=0mm,opacityback=0,opacityframe=0,enhanced jigsaw]#\begin{tikzpicture}[scale=1]#\node[rectangle,text width =42pt] (a)#{\heiti{\bfseries\fontsize{42}{32}\selectfont *mt\par}};#%righttitle\node[right =0pt of a,rectangle,text width =21pt]#%righttitle{\heiti{\bfseries\fontsize{21}{17}\selectfont *s2\par}};#%lefttitle\node[left =0pt of a,rectangle,text width =21pt]#%lefttitle{\heiti{\bfseries\fontsize{21}{17}\selectfont *s1\par}};#\end{tikzpicture}\par#\tcblower#{\songti{\fontsize{9}{10}\selectfont *mc\par}}\par#\end{tcolorbox}'
    str6f=str6.replace('#','\n')
    u10,xxx5,yyy5=vt_mt1p_nc(str6f,'vt_mt1p_nc',100,200,False,0,['',''],[32,200],7,2,[[5,3,'./img/jh2_image1.jpeg'],[5,3,'./img/newstitle.png']])
    #print(xxx5,yyy5)

    #print('******')
    st1=r'%%subtitile1#{\centering\heiti{\fontsize{21}{0}\selectfont *s1\par}}#\vspace{3mm}#%maintitle#{\centering\syht{\fontsize{48}{0}\selectfont *mt\par}}#%%subtitile2#\vspace{3mm}#{\centering\heiti{\fontsize{21}{0}\selectfont *s2\par}}#\vspace{5mm}#%pic1#{\songti{\fontsize{9}{10}\selectfont *mc\par}}'
    st1f=st1.replace('#','\n')
    u11,xxx1,yyy1=ht_t1p_nc(st1f,'ht_t1p_nc',67.55,290.5,True,1,['全面建成小康社会',''],[339],6,1,[[67,40.2,'./image1']])
    #print(u11,xxx1,yyy1)

    print('*************************************')
    u2,xx1,yy1=rvt_np_nc(yy,'rvt_np_nc',62.85,196,True,1,['韩国',''],7,[447])
    #print(u2,xx1,yy1)
    '''

    st3=r'\begin{tcolorbox}#[sidebyside,sidebyside align=bottom seam,sidebyside gap=5mm,colframe=red!75!white,colback=white,lower separated=false,righthand width=0.6\textwidth,halign lower=flush right,top=2mm,right=2mm,bottom=2mm,left=5mm,outer arc=0mm,arc=0mm,,boxsep=0mm]#{%title#{ \centering\heiti{\fontsize{21}{0}\selectfont *mt \par}}#\vspace{3mm}#%text#{\fontsize{9}{9}\selectfont\kaishu *mc \par }}#\tcblower#%pic1#\end{tcolorbox}'
    st3f=st3.replace('#','\n')
    ret1=picnews_vertical_nc(st3f,100,200,2,[[5,3,'./img/jh2_image1.jpeg'],[5,3,'./img/newstitle.png']])

    st4=r'\begin{tcolorbox}#[colframe=red!75!white,colback=white,top=2mm,right=2mm,bottom=2mm,left=2mm,outer arc=0mm,arc=0mm,boxsep=0mm]#{%pic1 \vspace{3mm} }#%title#\begin{minipage}{0.3\textwidth}#{\centering\heiti{\fontsize{21}{0}\selectfont *mt \par}}#\end{minipage}#\hspace{5mm}#%text#\begin{minipage}{0.7\textwidth-7mm}#{\kaishu\fontsize{9}{9}\selectfont *mc\par }#\end{minipage}\end{tcolorbox}'
    st4f=st4.replace('#','\n')
    print(st4f)
    picnews_lt_horizontal_nc(st4f,100,200,1,[[5,3,'./img/jh2_image1.jpeg']],[123])
    #print(st4f)

    st5=r'\begin{tcolorbox}#[colframe=red!75!white,colback=white,top=2mm,right=2mm,bottom=2mm,left=2mm,outer arc=0mm,arc=0mm,boxsep=0mm]#{%pic1 \vspace{3mm}}#%title#{\centering\heiti{\fontsize{21}{0}\selectfont *mt\par}}#\vspace{3mm}#%text#{\kaishu\fontsize{9}{9}\selectfont *mc\par}#\end{tcolorbox}'
    st5f=st5.replace('#','\n')
    picnews_ht_horizontal_nc(st5f,100,200,1,[[5,3,'./img/jh2_image1.jpeg']],[123])