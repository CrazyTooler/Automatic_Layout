import imp

from sqlalchemy import true
from style_mysql import mysqlCon
import re
import numpy as np
import cv2
from PIL import Image
'''
sqlcon=mysqlCon()
sql="select id,name,texcode,colnum,title_style,description from style_3 where category='%s'"%('ht_ltcp_c')
rets=sqlcon.select(sql)
print(rets[0][2].replace('#','\\n'))
'''
str1=r"%%subtitle1#{\centering\heiti{\fontsize{21}{0}\selectfont *s1\par}}#\vspace{3mm}#%maintitle#\scalebox{1}[1]{\centering\syht{\fontsize{48}{0}\selectfont \shortstack[c]{*mt}\par}}#%%subtitle2#\vspace{3mm}#{\centering\heiti{\fontsize{21}{0}\selectfont *s2\par}}#\vspace{5mm}#\vspace{-\baselineskip}#\setlength{\columnsep}{5mm}#\begin{multicols}{2}#%pic1#{\songti{\fontsize{9}{10}\selectfont *mc\par}}\par#\end{multicols}#\vspace{-1em}"
style=str1.replace('#','\n')
str1=str1.replace('#','\n').replace('\end{multicols}','').replace('\\begin{multicols}{2}','').replace('\\vspace{-\\baselineskip}','').replace('\\vspace{-1em}','')


#print(str1)
'''
pattern1=r'\begin{multicols}.*'
pattern2=r'\end{multicols}'
pattern3=r'\vspace{-\baselineskip}'
            
s1=re.findall(str1,pattern2)
print(s1)
s11=re.sub(pattern2,'',str1)
print(s11)
'''
pattern1=r"(?<=\\begin\{multicols\}\{).*(?=\})"#找到正文的字号与行距
column_num=re.findall(pattern1,str1)
#column_num=int(column_num[0]) #原栏数
pattern2=r"(?<=\\setlength\{\\columnsep\}\{).*(?=mm\})"#找到正文的字号与行距
column_sep=re.findall(pattern2,style)
column_sep=int(column_sep[0]) #原栏间距
#print(column_num)

#前两篇按照从左到右，从上到下的规则，后面的根据推断模型进行预测,还要看宽度(两栏宽度为分界)
def get_weights(article_num,x_list,y_list,width_list,label,ispicnews):
    max_y=max(y_list)
    weights=np.ones(article_num)*(-1)
    x_sort=np.sort(list(set(x_list))) #从小到大排列
    y_sort=np.sort(list(set(y_list))) #只固定y值最高的新闻块
    print(x_sort)
    print(y_sort)
    for i in range(article_num):
        if ispicnews[i]==0:
            #头条的选择
            if y_list[i]==max_y and x_list[i]==x_sort[0] and width_list[i]>35:
                weights[0]=(i+1)
            elif y_list[i]==max_y and x_list[i]==x_sort[0] and width_list[i]<=35 and label[i]=="vwt_np_nc": #如果x只有一种值
                weights[0]=(i+1)
            #即左上角不符合头条情况
            #二头条的选择
            if len(x_sort)>1:
                if weights[0]==-1: #即在(0,0)处没有符合头条的新闻块
                    if y_list[i]==max_y and x_list[i]==x_sort[1] and width_list[i]>35:
                        weights[0]=(i+1)
                    elif y_list[i]==max_y and x_list[i]==x_sort[1] and width_list[i]<=35 and label[i]=="vwt_np_nc":
                        weights[0]=(i+1)
                else:
                    if y_list[i]==max_y and x_list[i]==x_sort[1] and width_list[i]>35:
                        weights[1]=(i+1)
                    elif y_list[i]==max_y and x_list[i]==x_sort[1] and width_list[i]<=35 and label[i]=="vwt_np_nc":
                        weights[1]=(i+1)
    return weights

def test1(article_num,ispicnews,x_list,y_list,width_list,label,ft_ave_list):
    index=[]
    ft_ave_dict={}
    weights=get_weights(article_num,x_list,y_list,width_list,label,ispicnews) #初始化权重
    #print("初始化权重：",weights)
    real_weights=[]
    for i  in range(article_num):
        if ispicnews[i]==1:
            index.append(i)  #记录图片新闻的下标
            continue
        real_weights.append(i+1)
    #print("real_weights",real_weights)
    for i in range(len(real_weights)):
        if real_weights[i] not in weights:
            ft_ave_dict[real_weights[i]]=ft_ave_list[i]
    #print(ft_ave_dict)
    ft_ave_dict=sorted(ft_ave_dict.items(),key=lambda item:item[1],reverse=True)
    #print(ft_ave_dict)
    
    for i in range(len(ft_ave_dict)):
        weights[i+(len(real_weights)-len(ft_ave_dict))]=ft_ave_dict[i][0]
    
    for i in range(len(index)):
        weights[article_num-len(index)+i]=index[i]+1 
    print(weights)



def crop_image(file_name,new_height,new_width):

    im = Image.open(file_name)
    width, height = im.size   
    #裁剪中心区域
    left = (width - new_width)/2
    top = (height - new_height)/2
    right = (width + new_width)/2
    bottom = (height + new_height)/2

    crop_im = im.crop((left, top, right, bottom)) #Cropping Image 

    crop_im.save(file_name+"_new.jpg")  #Saving Images 



def main():
    '''
    new_width = 256     #Enter the crop image width，单位为像素
    new_height = 256    #Enter the crop image height
    file_name = r"layout_test\15839725380.jpg" #Enter File Names

    crop_image(file_name,new_height,new_width)
    '''
    res=get_weights(5,[0,0,30,30,30],[100,50,100,70,40],[30,30,70,70,70],["ht_np","ht_np_c","ht_np_c","ht_np_c","ht_np_c"],[0,0,0,1,0])
    print(res)
    test1(5,[0,0,0,1,0],[0,0,30,30,30],[100,50,100,70,40],[30,30,70,70,70],["vwt_np_nc","ht_np_c","ht_np_c","ht_np_c","ht_np_c"],[45,35,46,33])
    
if __name__=='__main__':
    main()