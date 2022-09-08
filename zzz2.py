from itertools import permutations
from typing import List, Mapping, Dict, Set
from user_setting import Paper_Params
from str2tree import Frame_cond, frameString2Framecond
from process_docx_ import get_article_dic, Article
import pymysql_connect as pyc
import numpy as np
import pandas as pd
from joblib import load
from pgmpy.readwrite import BIFReader
import tools6
from concurrent.futures import *
import time
import recommand_style_main2
# import getSeqs
import getseqs2



def getFramdcond(sset) -> List[str]:
    ret = []
    for s in sset:
        tmp = ''
        for ch in s:
            if ch in 'RC':
                tmp += ch + '1'
            else:
                tmp += ch
        ret.append(frameString2Framecond(tmp))
    return ret

def preproArtDict(filepath:str, newsLevel = [1,2,3,4,5,5,5]) -> Dict[int,Article]:
    """增加一些文章属性: ishead,isgraghnews"""
    #新闻文章字典#######################################
    articles_dict = get_article_dic(filepath)
    articles_dict[1].ishead = True
    for key in articles_dict:
        articles_dict[key].level = newsLevel.pop(0)
        articles_dict[key].isgraghnews = False
        if articles_dict[key].have_pics:
            if articles_dict[key].count_paras_char < 250:  
                articles_dict[key].isgraghnews = True
        # for k,v in articles_dict[key].__dict__.items():
        #     print(k,":  ",v)
    return articles_dict

def preferPctureSize(articles_dict: Mapping[int,Article]) -> Dict[int,float]:
    """推断图片大小"""
    #preprocess#################
    boundaries = []
    article_num = len(articles_dict)
    with open(f'./models1/prefer_model/picture_size/boundaries_n={article_num}.txt', encoding='utf-8', mode='r') as f:
        for c in f.readlines():
            boundaries.append(c[:-2].split('\t'))
    # print(boundaries)
    picSize = {}
    for key in articles_dict:
        if articles_dict[key].have_pics:
            if not articles_dict[key].ishead and not articles_dict[key].isgraghnews:
                newstype = 0
            elif articles_dict[key].ishead and not articles_dict[key].isgraghnews:
                newstype = 1
            else:
                newstype = 2
            allpic_num = 0 if sum([articles_dict[key].count_pics for key in articles_dict]) == 1 else 1
            picture_count = 0 if articles_dict[key].count_pics == 1 else 1
            relabels = [newstype, allpic_num, picture_count]
            print(relabels,'relabels')
            fea = pd.DataFrame(np.array(relabels).reshape(1,-1), columns=['newstype', 'allpic_num', 'picture_count'])
            #prefer#####################
            print(fea)
            preds = np.loadtxt(f'./models1/prefer_model/picture_size/preds_n={article_num}.txt')
            model = BIFReader(f'./models1/prefer_model/picture_size/prefer_picturesize_n={article_num}.bif').get_model(int)
            pred_data = model.predict(fea).loc[:,'picture_area'].to_list()
            # pred_data = model.predict_probability(fea)
            print(pred_data)
            yy = preds[pred_data][0]
            picSize[key] = yy
    return picSize
            

            

def preferHeadWidth(articles_dict: Mapping[int,Article]) -> float:
    """推断头条宽度"""
    #preprocess#################
    boundaries = []
    article_num = len(articles_dict)
    with open(f'./models1/prefer_model/head_width/boundaries_n={article_num}.txt', encoding='utf-8', mode='r') as f:
            for c in f.readlines():
                boundaries.append(c[:-2].split('\t'))
    atitle_char_count = articles_dict[1].count_title_char / max(sum([articles_dict[key].count_title_char for key in articles_dict]), 1)
    text_char_count_ratio = articles_dict[1].count_paras_char / max(sum([articles_dict[key].count_paras_char for key in articles_dict]), 1)
    subtitle_area_count  = articles_dict[1].count_sub_title / max(sum([articles_dict[key].count_sub_title for key in articles_dict]), 1)
    picture_count = articles_dict[1].count_pics / max(sum([articles_dict[key].count_pics for key in articles_dict]), 1)
    labels = [atitle_char_count, text_char_count_ratio, subtitle_area_count, picture_count]
    relabels = []
    for i in range(4):
        for j in range(len(boundaries[i])):
            if labels[i] <= float(boundaries[i][j]):
                relabels.append(j)
                break
            elif j == len(boundaries[i])-1:
                relabels.append(j)
    fea = pd.DataFrame(np.array(relabels).reshape(1,-1), columns=['atitle_char_count', 'text_char_count_ratio', 'subtitle_area_count', 'picture_count'])
    #prefer#####################
    pp = time.time()
    model = BIFReader(f'./models1/prefer_model/head_width/prefer_articlewidth_n={article_num}.bif').get_model(int)
    # print(model.predict_probability(fea))
    print('fff',time.time()-pp)
    pred_data = model.predict(fea).loc[:,'article_w'].to_list()
    width = [0.7, 0.28, 1]
    return width[pred_data[0]]

def preferPageStructures(articles_dict: Mapping[int,Article], area_cof = [0.55,0.28,0.12,0.05]) -> Set[str]:
    """推断版面结构"""
    #preprocess#################
    data = np.array([[articles_dict[key].count_paras_char, articles_dict[key].count_title_char, articles_dict[key].count_pics, articles_dict[key].count_sub_title] for key in articles_dict])
    article_count = data.shape[0]
    # print(data)
    maxd = np.loadtxt(f'./models1/prefer_model/paper_structure/max_n={article_count}.txt', dtype=int)
    mind = np.loadtxt(f'./models1/prefer_model/paper_structure/min_n={article_count}.txt', dtype=int)
    fea = np.dot((data-mind) / (maxd-mind), np.array(area_cof))
    fea = np.sort(fea)
    #prefer#####################
    knn = load(f'./models1/prefer_model/paper_structure/prefer_Struc_n={article_count}.joblib')
    _, b = knn.kneighbors(fea.reshape(1,-1), return_distance=True)
    y_train = np.loadtxt(f'./models1/prefer_model/paper_structure/y_n={article_count}.txt', dtype=str)
    thepreds = y_train[tuple(b)]
    return set(thepreds)

def framedata(filepath, newsLevel = [1,2,3,4,5,5,5]):
    """计算可用版面布局"""
    result = [[] for i in range(4)]
    articles_dict = preproArtDict(filepath, newsLevel)
    article_count = len(articles_dict)
    qq1 = time.time()
    pageStructures = preferPageStructures(articles_dict)
    qq2 = time.time()
    print(qq2-qq1)
    headWidth = preferHeadWidth(articles_dict)
    qq3 = time.time()
    print(qq3-qq2)
    headWidth = int(100*headWidth)
    headWidth = 70
    picSzie = preferPctureSize(articles_dict)
    print(picSzie,'-=-----------------------picsize')
    print(time.time()-qq3)
    frameconds = getFramdcond(pageStructures)
    ##################################################
    paper_params = Paper_Params()
    seqs = [seq for seq in permutations(range(1,article_count+1))]
    aval_seqs = [[] for i in frameconds]
    idxs = [i for i in range(len(seqs))]
    np.random.shuffle(idxs)
    for idx1,frame_cond in enumerate(frameconds):
        avail_index = pyc.getPagestructures(frame_cond.pagetree)
        print(avail_index)
        if avail_index:
            aval_seqs[idx1] = [int(i) for i in avail_index[0].split(',')]
            continue
        for idx2 in idxs:
            # t = getSeqs.main(frame_cond, seqs[idx2], 0, 0, articles_dict, paper_params)
            print(frame_cond.pagetree, idx1, idx2)
            t = getseqs2.main(frame_cond, seqs[idx2], 0, 0, articles_dict, paper_params)
            if t:
                aval_seqs[idx1].append(idx2)
                print(t)
            else:
                print('not available')
        pyc.savePagestructures(frame_cond.pagetree, aval_seqs[idx1])
    print(aval_seqs)
    print(picSzie)
    print(headWidth)
    scount = sum([len(el) for el in aval_seqs])
    acount = 0
    bcount = 0
    for f in frameconds:
        print(f.pagetree)
    #######################
    maxblank = 1000
    bbb = time.time()
    with ProcessPoolExecutor(max_workers=4) as executor:
        fts = []
        for idx1,frame_cond in enumerate(frameconds):
            for idx2 in aval_seqs[idx1]:
                articles_seq_list = seqs[idx2]
                if frame_cond.pagetree.startswith('R1()'):
                    headWidth = 100
                else:
                    headWidth = 30
                fts.append(executor.submit(tools6.main,frame_cond, articles_seq_list, headWidth, picSzie, articles_dict, paper_params, maxblank))
        for ft in as_completed(fts):
            acount += 1
            p = 100*acount//scount
            print(f'\r all{scount},complete %{p}[{p*"▓"}->{(100-p)*" "}] find {bcount} solutions ',end='')
            if ft.result():
                bcount += 1
                d = ft.result()
                result[0].append(d)
                for rec in d[:-2]:
                    rec[1] = 100 - rec[1] - rec[3]
                recommand_style_main2.main([d])
    ##########################
    print('pptime ', time.time()-bbb)
    return result

def main():
    # np.random.seed(1)
    ret = framedata("./testdocx/jh2.docx")    
    print('\n',ret)
    # for ret in ret[0]:
    #     tools1.visulizeThePage(ret[:7])

if __name__ == '__main__':
    start = time.time()
    ret = main()
    end = time.time()
    print('executing time: ', end - start)
