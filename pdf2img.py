import os
import fitz


def get_file(pdfpath):
    files = os.listdir(pdfpath)  # 默认访问的是当前路径
    lis = [pdfpath + os.sep + file for file in files if os.path.splitext(file)[1] == '.pdf']
    return lis

def conver_one_img(pdf_path):
    with fitz.open(pdf_path) as doc:
            pdf_name = os.path.basename(pdf_path).split('.')[0]
            
            for pg in range(doc.pageCount):
                page = doc[pg]
                rotate = int(0)
                # 每个尺寸的缩放系数为10，这将为我们生成分辨率提高100倍的图像。
                zoom_x, zoom_y = 1.5, 1.5
                trans = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)
                pm = page.getPixmap(matrix=trans, alpha=False)
                # pm.writePNG('%s.png' % pdf_name)
                pm.writePNG(f'./img/{pdf_name}.png')

def conver_img(pdf_dir):
    for pdf in pdf_dir:
        # doc = fitz.open(pdf)
        with fitz.open(pdf) as doc:
            pdf_name = os.path.basename(pdf).split('.')[0]
            
            for pg in range(doc.pageCount):
                page = doc[pg]
                rotate = int(0)
                # 每个尺寸的缩放系数为10，这将为我们生成分辨率提高100倍的图像。
                zoom_x, zoom_y = 1.5, 1.5
                trans = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)
                pm = page.getPixmap(matrix=trans, alpha=False)
                # pm.writePNG('%s.png' % pdf_name)
                pm.writePNG(f'./img/{pdf_name}.png')

def main():
    pdfpath = r'./page'
    # pdfpath = '.'
    pdf_dir = get_file(pdfpath)
    conver_img(pdf_dir)


if __name__ == '__main__':
    main()
