from PIL import Image
import os

def get_imagedata(image_name):
    im = Image.open('./bh_image/'+image_name)#返回一个Image对象
    #图片尺寸大小单位转化：实际尺寸(英寸)=像素/分辨率; 1英寸=2.54厘米
    idpi=im.info['dpi'][0]#图片分辨率
    iw=(im.size[0]/idpi)*25.4#图片宽度(mm)
    ih=(im.size[1]/idpi)*25.4#图片高度(mm)
    ir=iw/ih
    iname=image_name.split('.')[0]
    idict=dict({'name':iname,'width':iw,'height':ih,'ratio':ir}) #图片属性信息（可加入图片语义信息）
    return idict 

def main():
    pathDir=os.listdir('./bh_image/') #读取图片文件夹下所有图片名称
    #print(pathDir)  
    sdict=[]
    for i in pathDir:
        t=get_imagedata(i)
        sdict.append(t)
    return sdict

if __name__=='__main__':
    t=main()
    print(t) #输出所有图片的字典信息