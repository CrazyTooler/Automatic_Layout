import numpy as np
import pandas as pd
import re 
'''
#将样式字符串中的参数导出并修改

标题：行数、字号、缩放比例
正文：栏数、栏距
图片：位置、比例、大小
'''
#改变横标题字号大小
def change_htitle_size(style,fontsize):
    main_title_command = re.search(r"(?<=maintitle\n).*",style)
    if main_title_command==None:
        return style
    old_title_command = main_title_command.group()
    pattern1=r"(?<=\\fontsize\{).*(?=\}\{)"#找到正文的字号与行距
    fontsize1=re.findall(pattern1,old_title_command)
    #print(fontsize1)
    fs=re.sub(pattern1,fontsize,old_title_command)
    retfs=style.replace(old_title_command,fs)
    #print(retfs)
    return retfs

#改变竖标题字号大小(换行的也需要改)
def change_vtitle_size(style,fontsize):
    pattern1=r"(?<=\\fontsize\{).*(?=\}\{)"
    fs1 = list(map(int,re.findall(pattern1,style)))
    pattern2=r"(?<=text width =).*(?=pt)"
    fs2 = list(map(int,re.findall(pattern2,style)))
    #print(fs2)
    fs1[0]=fontsize
    fs1[1]=fontsize
    fs2[0]=fontsize
    fs2[1]=fontsize
    fs1=[str(i) for i in fs1]
    fs2=[str(i) for i in fs2]
    htv1=re.sub(pattern1,lambda _: fs1.pop(0),style)
    htv2=re.sub(pattern2,lambda _: fs2.pop(0),htv1)
    #print('htv2',htv2)
    return htv2
    

def change_column_num(style,cnum): #这里的cnum为字符串格式
    pattern1=r"(?<=\\begin\{multicols\}\{).*(?=\})"#找到正文的字号与行距
    column_num=re.findall(pattern1,style)
    column_num=int(column_num[0]) #原栏数
    #print(column_num)
    new_str=re.sub(pattern1,cnum,style,1)
    #print(new_str)
    return new_str

#改变栏距
def change_column_sep(style,colsep):
    pattern1=r"(?<=\\setlength\{\\columnsep\}\{).*(?=mm\})"#找到正文的字号与行距
    column_sep=re.findall(pattern1,style)
    column_sep=int(column_sep[0]) #原栏间距
    #print(column_sep)
    new_str=re.sub(pattern1,colsep,style,1)
    print(new_str)
    return new_str

#根据标题样式改变字体的压缩系数
def change_scale_coe(style,scalecoe,title_style):
    pattern1=r"(?<=\\scalebox\{).*(?=\]\{\\)"#找到正文的字号与行距
    pattern2=r"(?<=\\scalebox\{).*(?=\]\{\\)"
    sc = re.findall(pattern2,style)
    #print(sc)
    scale_org=re.findall(pattern1,style)
    #print(scale_org)
    #print(scale_org)
    if title_style==0:#横标题
        if scale_org==[]:
            return style
        str1=str(scalecoe)+'}['+str(1)
        retsc=re.sub(pattern1,str1,style)
    elif title_style==1: #竖标题
        if sc==[]:
            return style
        str1=str(1)+'}['+str(scalecoe)
        str2=[str1,str1]
        retsc=re.sub(pattern2,lambda _: str2.pop(0),style)
    #print(retsc)
    return retsc

#根据留白高度改变图片新闻的高度
def change_pic_height(style,eh):
    pattern1=r"(?<=,height=).*(?=mm]{)"
    height=re.findall(pattern1,style)
    height=float(height[0])  #暂时只改变一张图片的大小
    #print(height)
    final_pich=height+eh
    newstyle=re.sub(pattern1,str(final_pich),style)
    return newstyle

#不伸缩图片比例，通过剪裁图片获得与空间比例相同的图片
def change_pic_size(style,eh,pic):
    #获取图片的原始比例
    pattern1=r"(?<=,height=).*(?=mm]{)"
    pattern2=r"(?<=\[width=).*(?=mm,height)"
    pattern3=r"(?<=\[width=).*(?=]{)"
    height=re.findall(pattern1,style)
    height=float(height[0])
    width=re.findall(pattern2,style)
    width=float(width[0])
    #print(width)
    pic_width=(pic[0][0]/300)*25.4#原始图片的宽度(mm)
    pic_height=(pic[0][1]/300)*25.4#原始图片的高度(mm)
    ratio_pic=round((pic_width/pic_height),2)
    #获得图片区域的比例
    ratio_area=float(width/(height+eh)) 
    #计算左下右上剪裁大小(单位mm)  
    if ratio_pic>ratio_area:
        #原图过宽
        width_init=ratio_area*pic_height
        left=(pic_width-width_init)/2
        right=(pic_width-width_init)/2
        top=0
        bottom=0
    elif ratio_pic<ratio_area:
        #原图过高
        height_init=pic_width/ratio_area
        left=0
        right=0
        top=(pic_height-height_init)/2
        bottom=(pic_height-height_init)/2
    else:
        left=0
        top=0
        right=0
        bottom=0
    
    #修改tex语句,trim表示修剪左上右下区域的图片大小
    final_tex="%fmm,trim=%fmm %fmm %fmm %fmm,clip"%(width,left,bottom,right,top)
    newstyle=re.sub(pattern3,str(final_tex),style)
    return newstyle

#改变垂直标题的方向，当新闻块x为0时为左边，x大于0时为右边,其中，默认方向为r
def change_title_direction(style,x):
    pattern1=r"(?<=wrapfigure}{).*(?=}{)"
    title_direction=re.findall(pattern1,style)
    #print(title_direction)
    if x==0:
        newstyle=re.sub(pattern1,'l',style)
    else:
        newstyle=style #因为默认垂直标题方向为r
    return newstyle


def main():
    str1=r'%%subtitle1#{\centering\heiti{\fontsize{21}{0}\selectfont *s1\par}}#\vspace{3mm}#%maintitle#\scalebox1}[1]{\centering\syht{\fontsize{48}{0}\selectfont *mt\par}}#%%subtitle2#\vspace{3mm}#{\centering\heiti{\fontsize{21}{0}\selectfont *s2\par}}#\vspace{5mm}#\setlength{\columnsep}{5mm}#\vspace{-\baselineskip}#\begin{multicols}{2}#{\songti{\fontsize{9}{10}\selectfont *mc\par}}\par\end{multicols}#\vspace{-1em}'
    str1=str1.replace('#','\n')
    str2=r'\begingroup#\setlength{\columnsep}{0pt}#\begin{wrapfigure}{r}{99pt}#\begin{tikzpicture}[scale=1]#%maintitle#\node[rectangle,text width =42pt] (a)#{\scalebox{1}[1]{\syht{\bfseries\fontsize{42}{32}\selectfont \shortstack[c]{*mt1}\par}}};#%maintitle2\node[right=0pt of a,rectangle,text width =42pt] (b)#%maintitle2{\scalebox{1}[1]{\syht{\bfseries\fontsize{42}{32}\selectfont \shortstack[c]{*mt2}\par}}};#%%subtitle2#%righttitle\node[right =0pt of b,rectangle,text width =21pt]#%righttitle{\heiti{\bfseries\fontsize{21}{17}\selectfont *s2\par}};#%%subtitle1#%lefttitle\node[left =0pt of a,rectangle,text width =21pt]#%lefttitle{\heiti{\bfseries\fontsize{21}{17}\selectfont *s1\par}};#\end{tikzpicture}\par#\vspace{-\baselineskip}#\end{wrapfigure}#{\songti{\fontsize{9}{10}\selectfont *mc\par}}\par#\endgroup'
    str2=str2.replace('#','\n')
    #print(str2)
    #change_column_num(str1,'4')
    #ret=change_title_size(str1,'40')
    #print(ret)
    #change_column_sep(str1,'7')
    #s=change_vtitle_size(str2,'45')
    #print(s)
    #change_htitle_size(str1,'45')
    #a=change_scale_coe(str2,0.5,1)
    #print(a)
    str3=r'\begin{tcolorbox}#[colframe=red!75!white,colback=white,top=2mm,right=2mm,bottom=2mm,left=2mm,outer arc=0mm,arc=0mm,boxsep=0mm]#{\includegraphics[width=92.1mm,height=30.2mm]{./bh_image/1.png} \vspace{3mm}}#{\includegraphics[width=92.1mm,height=30.2mm]{./bh_image/1.png} \vspace{3mm}}#%title#{\centering\heiti{\fontsize{21}{0}\selectfont *mt\par}}#\vspace{3mm}#%text#{\kaishu\fontsize{9}{10}\selectfont *mc\par}#\end{tcolorbox}'
    str3=str3.replace('#','\n')
    print(str3)
    b=change_pic_height(str3,2)
    #print(b)
    c=change_title_direction(str2,0)
    print(c)


if __name__=='__main__':
    main()