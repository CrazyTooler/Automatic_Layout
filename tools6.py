from itertools import permutations
import matplotlib.pyplot as plt
from user_setting import Paper_Params
from ortools.sat.python import cp_model
from str2tree import Frame_cond, frameString2Framecond
from process_docx_ import get_article_dic, Article
import time

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

def main(frame_cond:Frame_cond, articles_seq_list:tuple, head_infer, pic_infer, articles_dict:dict, paper_params:Paper_Params, maxblank:int):
    """以frame_cond为矩形约束，文章大小列表articles_seq_list的条件下，进行矩形划分"""
    #建立模型
    # print('-------------start-----------')
    model = cp_model.CpModel()
    article_count = len(articles_seq_list)
    # print(article_count)
    articles_seq = [0] + list(articles_seq_list)
    ###################################################
    thepic = []
    #######已知条件（统一单位0.01mm）
    paper_width = 100 * paper_params.paper_width                                                       #paper宽度（默认320mm）
    paper_height = 100 * paper_params.paper_height                                                     #paper高度（默认500mm）
    frame_width_gap = 100 * paper_params.frame_width_gap                                               #文章距离两侧边框的距离左右为(默认5mm)
    frame_height_gap = int(100 * paper_params.frame_height_gap)                                             #文章距离两侧边框的距离上下为(0mm)
    title_subtitle_gap = 100 * paper_params.title_subtitle_gap                                         #主标题与子标题之间的距离(3mm)
    title_text_gap = 100 * paper_params.title_text_gap                                                 #标题区域与正文区域之间的距离(5mm)
    column_gap = 100 * paper_params.column_gap                                                         #栏距（默认5mm）
    pt = paper_params.pt                                                                               ##100*0.35pt与mm换算（默认35）1pt = 0.35mm
    subtitle_font_pt = paper_params.subtitle_font_pt                                                   #副标题字号(单位：pt)
    ###################
    subtitle_font_size = pt * paper_params.subtitle_font_pt                                            #副标题字号(单位：pt)
    text_font_width_size = pt * paper_params.text_font_width_pt                                        #正文字符宽度（默认9pt）
    text_font_height_size = pt * paper_params.text_font_height_pt                                      #正文字符高度（默认10pt）
    level_fontgap = paper_params.level_font_gap
    level1_title_font_range = [item  for item in paper_params.level1_title_font]                   #新闻等级1下标题字号范围（默认30-60pt）
    level2_title_font_range = [item  for item in paper_params.level2_title_font]                   #新闻等级2下标题字号范围（默认30-55pt）
    level3_title_font_range = [item  for item in paper_params.level3_title_font]                   #新闻等级3下标题字号范围（默认30-50pt）
    level4_title_font_range = [item  for item in paper_params.level4_title_font]                   #新闻等级4下标题字号范围（默认30-45pt）
    level5_title_font_range = [item  for item in paper_params.level5_title_font]                   #新闻等级5下标题字号范围（默认30-40pt）
    level_title_font_range = [level1_title_font_range, level2_title_font_range, level3_title_font_range, level4_title_font_range, level5_title_font_range]
    M = 1000 * max(paper_height, paper_width)
    ratio_ = [int(100*item) for item in paper_params.ratio]
    ratio1_ = [int(100*item) for item in paper_params.ratio]
    ratio21_ = [int(100*item) for item in paper_params.ratio21]
    ratio22_ = [int(100*item) for item in paper_params.ratio22]
    ratio31_ = [int(100*item) for item in paper_params.ratio31]
    ratio32_ = [int(100*item) for item in paper_params.ratio32]
    ratio4_ = [int(100*item) for item in paper_params.ratio4]
    ##################################################################################################################
    #创建变量
    #frame变量
    frames_x = [model.NewIntVar(0, paper_width, "frames_x_%d" % i) for i in range(article_count + 1)]#x坐标
    frames_y = [model.NewIntVar(0, paper_height, "frames_y_%d" % i) for i in range(article_count + 1)]#y坐标
    frames_w = [model.NewIntVar(5000, paper_width, "frames_w_%d" % i) for i in range(article_count + 1)]#w宽度
    frames_h = [model.NewIntVar(5000, paper_height, "frames_h_%d" % i) for i in range(article_count + 1)]#h高度
    frames_available_w = [model.NewIntVar(1, paper_width, "frames_available_w_%d" % i) for i in range(article_count + 1)]#可用宽度
    frames_available_h = [model.NewIntVar(1, paper_height, "frames_available_h_%d" % i) for i in range(article_count + 1)]#可用宽度
    frames_area = [model.NewIntVar(0, paper_width * paper_height, "frames_area_%d" % i) for i in range(article_count + 1)]#面积
    articles_height = [model.NewIntVar(0, paper_height, "articles_height_%d" % i) for i in range(article_count + 1)]
    articles_area = [model.NewIntVar(0, paper_width * paper_height, "articles_area_%d" % i) for i in range(article_count + 1)]#a文章面积
    frames_pad_height = [model.NewIntVar(0, paper_height, "frames_pad_height_%d" % i) for i in range(article_count + 1)]
    frames_pad_area = [model.NewIntVar(0, paper_width * paper_height, "frames_pad_area_%d" % i) for i in range(article_count + 1)]#s留白
    combinational_frames_x = {str(i) : model.NewIntVar(0, paper_width, "combinational_frames_x_%d" % i) for i in range(article_count - 1)}
    combinational_frames_y = {str(i) : model.NewIntVar(0, paper_height, "combinational_frames_y_%d" % i) for i in range(article_count - 1)}
    combinational_frames_w = {str(i) : model.NewIntVar(0, paper_width, "combinational_frames_w_%d" % i) for i in range(article_count - 1)}
    combinational_frames_h = {str(i) : model.NewIntVar(0, paper_height, "combinational_frames_h_%d" % i) for i in range(article_count - 1)}
    isgoodv_frames = [model.NewIntVar(0, 1,"isgoodv_frames1_%d" % i) for i in range(article_count+1)]
    isgoodh_frames = [model.NewIntVar(0, 1,"isgoodh_frames1_%d" % i) for i in range(article_count+1)]
    isgoodv_frames1 = [model.NewBoolVar("isgoodv_frames4_%d" % i) for i in range(article_count+1)]
    isgoodh_frames1 = [model.NewBoolVar("isgoodh_frames4_%d" % i) for i in range(article_count+1)]
    isgoodv_frames21 = [model.NewBoolVar("isgoodv_frames21_%d" % i) for i in range(article_count+1)]
    isgoodh_frames21 = [model.NewBoolVar("isgoodh_frames21_%d" % i) for i in range(article_count+1)]
    isgoodv_frames22 = [model.NewBoolVar("isgoodv_frames22_%d" % i) for i in range(article_count+1)]
    isgoodh_frames22 = [model.NewBoolVar("isgoodh_frames22_%d" % i) for i in range(article_count+1)]
    isgoodv_frames31 = [model.NewBoolVar("isgoodv_frames31_%d" % i) for i in range(article_count+1)]
    isgoodh_frames31 = [model.NewBoolVar("isgoodh_frames31_%d" % i) for i in range(article_count+1)]
    isgoodv_frames32 = [model.NewBoolVar("isgoodv_frames32_%d" % i) for i in range(article_count+1)]
    isgoodh_frames32 = [model.NewBoolVar("isgoodh_frames32_%d" % i) for i in range(article_count+1)]
    isgoodv_frames4 = [model.NewBoolVar("isgoodv_frames4_%d" % i) for i in range(article_count+1)]
    isgoodh_frames4 = [model.NewBoolVar("isgoodh_frames4_%d" % i) for i in range(article_count+1)]
    #article变量
    #########################
    levels_font = [model.NewIntVar(subtitle_font_pt, level1_title_font_range[1], "levels_font_%d" % i) for i in range(5)]
    #########################
    picstyles_bool = [model.NewBoolVar("picstyles_bool_%d" % i) for i in range(article_count + 1)] 
    pic_height = [model.NewIntVar(0, paper_height, "pic_height_%d" % i) for i in range(article_count + 1)]
    pic_width = [model.NewIntVar(0, paper_width, "pic_width_%d" % i) for i in range(article_count + 1)]
    tmppicheight = [model.NewIntVar(0, paper_height, "tmppicheight_%d" % i) for i in range(article_count + 1)]
    pic_rr = [model.NewIntVar(-paper_height*paper_width, paper_height*paper_width, "pic_rr_%d" % i) for i in range(article_count + 1)]
    pic_ratio = [model.NewIntVar(0, paper_height*paper_width, "pic_ratio_%d" % i) for i in range(article_count + 1)]
    area_ = [model.NewIntVar(0, paper_height*paper_width, "area_%d" % i) for i in range(article_count + 1)]
    ####
    titles_style_h_bool = [model.NewBoolVar("titles_style_h_bool_%d" % i) for i in range(article_count + 1)]###是否为横向标题
    #######
    atitle_font_pts = [model.NewIntVar(subtitle_font_pt, level1_title_font_range[1], 'atitle_font_pts_%d' % i) for i in range(article_count + 1)]#atitle字号
    atitles_rows_bool = [model.NewBoolVar('atitles_rows_bool_%d' % i) for i in range(article_count + 1)]#atitle所占的行数(1-2行)
    atitles_height = [model.NewIntVar(0, paper_height,'atitles_height_%d' % i) for i in range(article_count + 1)]#atitle高度
    # ###
    ftitles_rows_bool = [model.NewBoolVar('ftitles_rows_bool_%d' % i) for i in range(article_count + 1)]#ftitle所占的行数(1-2行)
    ftitles_height = [model.NewIntVar(0, paper_height,'ftitles_height_%d' % i) for i in range(article_count + 1)]#ftitle高度
    # ###
    ytitles_rows_bool = [model.NewBoolVar('ytitles_rows_bool_%d' % i) for i in range(article_count + 1)]#ftitle所占的行数(1-2行)
    ytitles_height = [model.NewIntVar(0, paper_height,'ytitles_height_%d' % i) for i in range(article_count + 1)]#ftitle高度
    # ###
    texts_columns = [model.NewIntVar(1, 5, 'texts_columns_%d' % i) for i in range(article_count + 1)]#text栏数
    texts_width = [model.NewIntVar(1, paper_width, 'texts_width_%d' % i) for i in range(article_count + 1)]#text宽度
    texts_rows = [model.NewIntVar(0, 100000, 'texts_rows_%d' % i) for i in range(article_count + 1)]#text行数
    texts_rows_error_bypara = [model.NewIntVar(0, 10, 'texts_rows_error_bypara_%d' % i) for i in range(article_count + 1)]#段落数引起的行数误差
    texts_height = [model.NewIntVar(0, paper_height,'texts_height_%d' % i) for i in range(article_count + 1)]#text高度
    ##########################
    ###竖标题变量
    atitles_w = [ model.NewIntVar(0, paper_width,'atitle_w_%d' % i) for i in range(article_count + 1)]
    ftitles_w = [ model.NewIntVar(0, paper_width,'ftitle_w_%d' % i) for i in range(article_count + 1)]
    ytitles_w = [ model.NewIntVar(0, paper_width,'ytitle_w_%d' % i) for i in range(article_count + 1)]
    titlesw = [ model.NewIntVar(0, paper_width,'titlew_%d' % i) for i in range(article_count + 1)]##
    titlesh = [ model.NewIntVar(0, paper_height,'titleh_%d' % i) for i in range(article_count + 1)]#
    textsw = [ model.NewIntVar(1, paper_width,'textw_%d' % i) for i in range(article_count + 1)]##
    textsh = [ model.NewIntVar(0, paper_height,'texth_%d' % i) for i in range(article_count + 1)]##
    textsr = [ model.NewIntVar(0, 10000, 'textr_%d' % i) for i in range(article_count + 1)]
    moresheight = [ model.NewIntVar(0,paper_height,'moreheight_%d' % i) for i in range(article_count + 1)]#
    moresarea = [ model.NewIntVar(0,5000000000000,'morearea_%d' % i) for i in range(article_count + 1)]
    ######################################
    ##字号
    for i in range(1, 5):
        model.Add(levels_font[i-1] >= levels_font[i] + level_fontgap)
    ##文章约束
    #版心
    for i in range(1, article_count + 1):
        model.Add(frames_available_h[i] == frames_h[i] - 2 * frame_height_gap)
        model.Add(frames_available_w[i] == frames_w[i] - 2 * frame_width_gap)
    for i in range(1, article_count + 1):
        ####################################
        maxtitleheight = model.NewIntVar(0, paper_height, "maxtitleheight_%d" % i)
        isgraghnews = articles_dict[articles_seq[i]].isgraghnews
        ishead = articles_dict[articles_seq[i]].ishead
        havegragh = articles_dict[articles_seq[i]].have_pics
        atitle_char_count = articles_dict[articles_seq[i]].count_title_char  ##atitle字数
        ftitle_char_count = articles_dict[articles_seq[i]].count_ftitle_char  ##ftitle字数
        ytitle_char_count = articles_dict[articles_seq[i]].count_ytitle_char  ##ytitle字数
        articlelevel = articles_dict[articles_seq[i]].level
        char_count_per_para = articles_dict[articles_seq[i]].para_char
        char_count = sum(char_count_per_para) ##段落字数
        count_para = len(char_count_per_para) ##段落段数
        #####################################################字号
        model.Add(atitle_font_pts[i] == levels_font[articlelevel-1])
        # print(articlelevel)
        model.Add(atitle_font_pts[i] <= level_title_font_range[articlelevel-1][1])
        model.Add(atitle_font_pts[i] >= level_title_font_range[articlelevel-1][0])
        ####################################################################################
        model.Add(frames_pad_height[i] == frames_available_h[i] - articles_height[i])
        #############################
        model.Add(2 * frames_w[i] >= frames_h[i]).OnlyEnforceIf(titles_style_h_bool[i])
        model.Add(2 * frames_w[i] + 1 <= frames_h[i]).OnlyEnforceIf(titles_style_h_bool[i].Not())
        ##########################横排标题
        # model.Add(titles_style_h_bool[i] == True)
        # model.Add(frames_w[i] <= paper_width // 3).OnlyEnforceIf(titles_style_h_bool[i])
        ###atitle
        ##1行
        model.Add(atitles_height[i] == atitle_font_pts[i] * pt + title_text_gap).OnlyEnforceIf(atitles_rows_bool[i]).OnlyEnforceIf(titles_style_h_bool[i])
        model.Add(atitle_char_count * atitle_font_pts[i] * pt <= 2 * frames_available_w[i]).OnlyEnforceIf(atitles_rows_bool[i]).OnlyEnforceIf(titles_style_h_bool[i])
        ##2行
        model.Add(atitles_height[i] == 2 * atitle_font_pts[i] * pt + title_text_gap).OnlyEnforceIf(atitles_rows_bool[i].Not()).OnlyEnforceIf(titles_style_h_bool[i])
        model.Add(atitle_char_count * atitle_font_pts[i] * pt >= 2 * frames_available_w[i] + 1).OnlyEnforceIf(atitles_rows_bool[i].Not()).OnlyEnforceIf(titles_style_h_bool[i])
        model.Add(atitle_char_count * atitle_font_pts[i] * pt <= 4 * frames_available_w[i]).OnlyEnforceIf(atitles_rows_bool[i].Not()).OnlyEnforceIf(titles_style_h_bool[i])
        ###ftitle
        if ftitle_char_count > 0:
            ##1行
            model.Add(ftitles_height[i] == subtitle_font_size + title_subtitle_gap).OnlyEnforceIf(ftitles_rows_bool[i]).OnlyEnforceIf(titles_style_h_bool[i])
            model.Add(ftitle_char_count * subtitle_font_size <= frames_available_w[i]).OnlyEnforceIf(ftitles_rows_bool[i]).OnlyEnforceIf(titles_style_h_bool[i])
            ##2行
            model.Add(ftitles_height[i] == 2 * subtitle_font_size + title_subtitle_gap).OnlyEnforceIf(ftitles_rows_bool[i].Not()).OnlyEnforceIf(titles_style_h_bool[i])
            model.Add(ftitle_char_count * subtitle_font_size >= frames_available_w[i] + 1).OnlyEnforceIf(ftitles_rows_bool[i].Not()).OnlyEnforceIf(titles_style_h_bool[i])
            model.Add(ftitle_char_count * subtitle_font_size <= 2 * frames_available_w[i]).OnlyEnforceIf(ftitles_rows_bool[i].Not()).OnlyEnforceIf(titles_style_h_bool[i])
        ###ytitle
        if ytitle_char_count > 0:
            ##1行
            model.Add(ytitles_height[i] == subtitle_font_size + title_subtitle_gap).OnlyEnforceIf(ytitles_rows_bool[i]).OnlyEnforceIf(titles_style_h_bool[i])
            model.Add(ytitle_char_count * subtitle_font_size <= frames_available_w[i]).OnlyEnforceIf(ytitles_rows_bool[i]).OnlyEnforceIf(titles_style_h_bool[i])
            ##2行
            model.Add(ytitles_height[i] == 2 * subtitle_font_size + title_subtitle_gap).OnlyEnforceIf(ytitles_rows_bool[i].Not()).OnlyEnforceIf(titles_style_h_bool[i])
            model.Add(ytitle_char_count * subtitle_font_size >= frames_available_w[i] + 1).OnlyEnforceIf(ytitles_rows_bool[i].Not()).OnlyEnforceIf(titles_style_h_bool[i])
            model.Add(ytitle_char_count * subtitle_font_size <= 2 * frames_available_w[i]).OnlyEnforceIf(ytitles_rows_bool[i].Not()).OnlyEnforceIf(titles_style_h_bool[i])
        ###text
        model.AddDivisionEquality(texts_columns[i], frames_available_w[i], paper_width//6)
        model.Add(texts_width[i] == frames_available_w[i] - texts_columns[i] * column_gap + column_gap).OnlyEnforceIf(titles_style_h_bool[i])
        model.AddDivisionEquality(texts_rows[i], char_count * text_font_width_size, texts_width[i])
        model.AddDivisionEquality(texts_rows_error_bypara[i], count_para, texts_columns[i])
        model.Add(texts_height[i] == text_font_height_size * texts_rows[i] + text_font_height_size * texts_rows_error_bypara[i] + text_font_height_size).OnlyEnforceIf(titles_style_h_bool[i])
        #####
        #########################竖排标题
        ###########################
        model.Add(2 * frames_w[i] + 1 <= frames_h[i]).OnlyEnforceIf(titles_style_h_bool[i].Not())
        model.Add(titlesw[i] == atitles_w[i] + ftitles_w[i] + ytitles_w[i]).OnlyEnforceIf(titles_style_h_bool[i].Not())
        model.AddMaxEquality(maxtitleheight, [atitles_height[i], ftitles_height[i], ytitles_height[i]])
        model.Add(maxtitleheight >= titlesh[i])
        ###atitle
        ##1列
        model.Add(atitles_w[i] == atitle_font_pts[i] * pt + title_text_gap).OnlyEnforceIf(atitles_rows_bool[i]).OnlyEnforceIf(titles_style_h_bool[i].Not())
        model.Add(atitles_height[i] == atitle_char_count * atitle_font_pts[i] * pt + 2 * title_text_gap).OnlyEnforceIf(atitles_rows_bool[i]).OnlyEnforceIf(titles_style_h_bool[i].Not())
        model.Add(7 * atitles_height[i] <= 10 * titlesh[i]).OnlyEnforceIf(atitles_rows_bool[i]).OnlyEnforceIf(titles_style_h_bool[i].Not())
        ##2列
        model.Add(atitles_w[i] == 2 * atitle_font_pts[i] * pt + title_text_gap).OnlyEnforceIf(atitles_rows_bool[i].Not()).OnlyEnforceIf(titles_style_h_bool[i].Not())
        model.Add(atitles_height[i] == (atitle_char_count//2 + 1) * atitle_font_pts[i] * pt + 2 * title_text_gap).OnlyEnforceIf(atitles_rows_bool[i].Not()).OnlyEnforceIf(titles_style_h_bool[i].Not())
        model.Add(7 * atitles_height[i] <= 10 * titlesh[i]).OnlyEnforceIf(atitles_rows_bool[i].Not()).OnlyEnforceIf(titles_style_h_bool[i].Not())
        ###ftitle
        if ftitle_char_count > 0:
            ##1列
            model.Add(ftitles_w[i] == subtitle_font_size + title_subtitle_gap).OnlyEnforceIf(ftitles_rows_bool[i]).OnlyEnforceIf(titles_style_h_bool[i].Not())
            model.Add(ftitles_height[i] == ftitle_char_count * subtitle_font_size + 2 * title_text_gap).OnlyEnforceIf(ftitles_rows_bool[i]).OnlyEnforceIf(titles_style_h_bool[i].Not())
            model.Add(ftitles_height[i] <= titlesh[i]).OnlyEnforceIf(ftitles_rows_bool[i]).OnlyEnforceIf(titles_style_h_bool[i].Not())
            ##2列
            model.Add(ftitles_w[i] == 2 * subtitle_font_size + title_subtitle_gap).OnlyEnforceIf(ftitles_rows_bool[i].Not()).OnlyEnforceIf(titles_style_h_bool[i].Not())
            model.Add(ftitles_height[i] == (ftitle_char_count // 2 + 1) * subtitle_font_size + 2 * title_text_gap).OnlyEnforceIf(ftitles_rows_bool[i].Not()).OnlyEnforceIf(titles_style_h_bool[i].Not())
            model.Add(ftitles_height[i] <= titlesh[i]).OnlyEnforceIf(ftitles_rows_bool[i].Not()).OnlyEnforceIf(titles_style_h_bool[i].Not())
        else:
            model.Add(ftitles_w[i] == 0)
            model.Add(ftitles_height[i] == 0)
        ###ytitle
        if ytitle_char_count > 0:
            ##1列
            model.Add(ytitles_w[i] == subtitle_font_size + title_subtitle_gap).OnlyEnforceIf(ytitles_rows_bool[i]).OnlyEnforceIf(titles_style_h_bool[i].Not())
            model.Add(ytitles_height[i] == ytitle_char_count * subtitle_font_size + 2 * title_text_gap).OnlyEnforceIf(ytitles_rows_bool[i]).OnlyEnforceIf(titles_style_h_bool[i].Not())
            model.Add(ytitles_height[i] <= titlesh[i]).OnlyEnforceIf(ytitles_rows_bool[i]).OnlyEnforceIf(titles_style_h_bool[i].Not())
            ##2列
            model.Add(ytitles_w[i] == 2 * subtitle_font_size + title_subtitle_gap).OnlyEnforceIf(ytitles_rows_bool[i].Not()).OnlyEnforceIf(titles_style_h_bool[i].Not())
            model.Add(ytitles_height[i] == (ytitle_char_count // 2 + 1) * subtitle_font_size + 2 * title_text_gap).OnlyEnforceIf(ytitles_rows_bool[i].Not()).OnlyEnforceIf(titles_style_h_bool[i].Not())
            model.Add(ytitles_height[i] <= titlesh[i]).OnlyEnforceIf(ytitles_rows_bool[i].Not()).OnlyEnforceIf(titles_style_h_bool[i].Not())
        else:
            model.Add(ytitles_w[i] == 0)
            model.Add(ytitles_height[i] == 0)
        ###text
        model.Add(textsw[i] == frames_available_w[i] - titlesw[i]).OnlyEnforceIf(titles_style_h_bool[i].Not())
        model.AddDivisionEquality(textsr[i], char_count * text_font_width_size, textsw[i])
        model.Add(moresheight[i] == text_font_height_size * textsr[i] - titlesh[i]).OnlyEnforceIf(titles_style_h_bool[i].Not())
        model.AddMultiplicationEquality(moresarea[i], [moresheight[i], textsw[i]])
        model.AddDivisionEquality(textsh[i], moresarea[i], frames_available_w[i])
        ##head
        if ishead:
            headw = model.NewIntVarFromDomain(cp_model.Domain.FromIntervals([[23*paper_params.paper_width, 35*paper_params.paper_width], [65*paper_params.paper_width, 75*paper_params.paper_width], [95*paper_params.paper_width, 105*paper_params.paper_width]]), 'headw')
            model.Add(frames_y[i] == paper_params.paper_height * 17)
            model.Add(frames_x[i] == 0)
            model.Add(frames_w[i] == headw)
            # model.Add(frames_w[i] >= paper_params.paper_width * (head_infer - 5))
            # model.Add(frames_w[i] <= paper_params.paper_width * (head_infer + 5))
        ##pic
        ##################图片高度
        if havegragh:
            #######图片
            thepic.append(i)
            ww = paper_width // 5
            model.Add(frames_w[i] >= ww)
            ############面积区间（a，b）
            a = int(13000*pic_infer[articles_seq[i]])
            b = int(5000*pic_infer[articles_seq[i]])
            model.Add(area_[i] <= a * paper_params.paper_height * paper_params.paper_width)
            model.Add(area_[i] >= b * paper_params.paper_height * paper_params.paper_width)
            model.AddMultiplicationEquality(area_[i],[pic_height[i],pic_width[i]])
            #######################################################################图片面积\比例
            model.Add(10*articles_dict[articles_seq[i]].pic[0][1]*pic_width[i] >= 8*articles_dict[articles_seq[i]].pic[0][0]*pic_height[i])
            model.Add(10*articles_dict[articles_seq[i]].pic[0][1]*pic_width[i] <= 12*articles_dict[articles_seq[i]].pic[0][0]*pic_height[i])
            model.Add(pic_rr[i] == articles_dict[articles_seq[i]].pic[0][1]*pic_width[i]-articles_dict[articles_seq[i]].pic[0][0]*pic_height[i])
            model.AddAbsEquality(pic_ratio[i], pic_rr[i])
            model.Add(frames_available_w[i] >= pic_width[i])
            model.Add(frames_available_h[i] >= pic_height[i])
            model.AddDivisionEquality(tmppicheight[i], area_[i], frames_available_w[i])
            ###############
            if isgraghnews:
                model.Add(50*pic_width[i] >= 29*frames_w[i]).OnlyEnforceIf(picstyles_bool[i])
                model.Add(50*pic_width[i] <= 31*frames_w[i]).OnlyEnforceIf(picstyles_bool[i])
                model.Add(5*(atitles_height[i] + ftitles_height[i] + ytitles_height[i] + texts_height[i]) <= 2*frames_h[i]).OnlyEnforceIf(picstyles_bool[i])
                model.Add(frames_available_w[i] >= frames_available_h[i]).OnlyEnforceIf(picstyles_bool[i])
                model.Add(articles_height[i] == pic_height[i]).OnlyEnforceIf(picstyles_bool[i])
                #################
                model.Add(frames_available_w[i] + 1 <= frames_available_h[i]).OnlyEnforceIf(picstyles_bool[i].Not())
                model.Add(atitles_height[i] + ftitles_height[i] + ytitles_height[i] + texts_height[i] + tmppicheight[i] == articles_height[i]).OnlyEnforceIf(titles_style_h_bool[i]).OnlyEnforceIf(picstyles_bool[i].Not())
                model.Add(articles_height[i] == titlesh[i] + textsh[i] + tmppicheight[i]).OnlyEnforceIf(titles_style_h_bool[i].Not()).OnlyEnforceIf(picstyles_bool[i].Not())
            else:
                model.Add(atitles_height[i] + ftitles_height[i] + ytitles_height[i] + texts_height[i] + tmppicheight[i] == articles_height[i]).OnlyEnforceIf(titles_style_h_bool[i])
                model.Add(articles_height[i] == titlesh[i] + textsh[i] + tmppicheight[i]).OnlyEnforceIf(titles_style_h_bool[i].Not())
        else:
            model.Add(atitles_height[i] + ftitles_height[i] + ytitles_height[i] + texts_height[i] == articles_height[i]).OnlyEnforceIf(titles_style_h_bool[i])
            model.Add(articles_height[i] == titlesh[i] + textsh[i]).OnlyEnforceIf(titles_style_h_bool[i].Not())
            model.Add(area_[i]==0)
            model.Add(pic_ratio[i]==0)
    ##################################################################################################################################
    #增加约束（frame）
    # print('-'*30,'^结构约束^','-'*30)
    # for i,j in frame_cond.__dict__.items():
    #     print(i,":  ",j)
    # print('-'*30,'v结构约束v','-'*30)
    #######################################
    # for i in range(1, article_count + 1):
    #     model.Add(frames_w[i] >= paper_width//4)
    #     model.Add(frames_h[i] >= paper_height//20)
    #     for j in range(i+1, article_count + 1):
    #         if articles_dict[articles_seq[i]].isgraghnews or articles_dict[articles_seq[j]].isgraghnews or articles_dict[articles_seq[i]].ishead or articles_dict[articles_seq[j]].ishead:
    #             continue
    #         if articles_dict[articles_seq[i]].level > articles_dict[articles_seq[j]].level:
    #             model.Add(frames_x[i]+frames_y[i] >= frames_x[j]+frames_y[j]-(paper_width+paper_height)//10)
    #         elif articles_dict[articles_seq[i]].level < articles_dict[articles_seq[j]].level:
    #             model.Add(frames_x[i]+frames_y[i] <= frames_x[j]+frames_y[j]+(paper_width+paper_height)//10)
    #######################################
    #版面结构约束
    #头版结构
    model.Add(frames_x[0] == 0)
    model.Add(frames_y[0] == 0)
    model.Add(frames_w[0] == paper_width)
    model.Add(frames_h[0] == 17*paper_height//100)
    model.Add(combinational_frames_x['0'] == 0)
    model.Add(combinational_frames_y['0'] == 17*paper_height//100)
    model.Add(combinational_frames_w['0'] == paper_width)
    model.Add(combinational_frames_h['0'] == paper_height - 17*paper_height//100)
    ###x=x
    for index_ in frame_cond.x_equal_x:
        for i in range(len(index_) - 1):
            if type(index_[i]) == str and type(index_[i+1]) == str:
                model.Add(combinational_frames_x[index_[i]] == combinational_frames_x[index_[i+1]])
            elif type(index_[i]) == str and type(index_[i+1]) == int:
                model.Add(combinational_frames_x[index_[i]] == frames_x[index_[i+1]])
            elif type(index_[i]) == int and type(index_[i+1]) == str:
                model.Add(frames_x[index_[i]] == combinational_frames_x[index_[i+1]])
            elif type(index_[i]) == int and type(index_[i+1]) == int:
                model.Add(frames_x[index_[i]] == frames_x[index_[i+1]])
    ###y=y
    for index_ in frame_cond.y_equal_y:
        for i in range(len(index_) - 1):
            if type(index_[i]) == str and type(index_[i+1]) == str:
                model.Add(combinational_frames_y[index_[i]] == combinational_frames_y[index_[i+1]])
            elif type(index_[i]) == str and type(index_[i+1]) == int:
                model.Add(combinational_frames_y[index_[i]] == frames_y[index_[i+1]])
            elif type(index_[i]) == int and type(index_[i+1]) == str:
                model.Add(frames_y[index_[i]] == combinational_frames_y[index_[i+1]])
            elif type(index_[i]) == int and type(index_[i+1]) == int:
                model.Add(frames_y[index_[i]] == frames_y[index_[i+1]])
    ###x+w=x
    for i,j in frame_cond.xw_equal_x:
        if type(i) == str and type(j) == str:
            model.Add(combinational_frames_x[i] + combinational_frames_w[i] == combinational_frames_x[j])
        elif type(i) == str and type(j) == int:
            model.Add(combinational_frames_x[i] + combinational_frames_w[i] == frames_x[j])
        elif type(i) == int and type(j) == str:
            model.Add(frames_x[i] + frames_w[i] == combinational_frames_x[j])
        elif type(i) == int and type(j) == int:
            model.Add(frames_x[i] + frames_w[i] == frames_x[j])
    ###y+h=y
    for i,j in frame_cond.yh_equal_y:
        if type(i) == str and type(j) == str:
            model.Add(combinational_frames_y[i] + combinational_frames_h[i] == combinational_frames_y[j])
        elif type(i) == str and type(j) == int:
            model.Add(combinational_frames_y[i] + combinational_frames_h[i] == frames_y[j])
        elif type(i) == int and type(j) == str:
            model.Add(frames_y[i] + frames_h[i] == combinational_frames_y[j])
        elif type(i) == int and type(j) == int:
            model.Add(frames_y[i] + frames_h[i] == frames_y[j])
    ###x+w=x+w
    for index_ in frame_cond.xw_equal_xw:
        for i in range(len(index_) - 1):
            if type(index_[i]) == str and type(index_[i+1]) == str:
                model.Add(combinational_frames_x[index_[i]] + combinational_frames_w[index_[i]] == combinational_frames_x[index_[i+1]] + combinational_frames_w[index_[i+1]])
            elif type(index_[i]) == str and type(index_[i+1]) == int:
                model.Add(combinational_frames_x[index_[i]] + combinational_frames_w[index_[i]] == frames_x[index_[i+1]] + frames_w[index_[i+1]])
            elif type(index_[i]) == int and type(index_[i+1]) == str:
                model.Add(frames_x[index_[i]] + frames_w[index_[i]] == combinational_frames_x[index_[i+1]] + combinational_frames_w[index_[i+1]])
            elif type(index_[i]) == int and type(index_[i+1]) == int:
                model.Add(frames_x[index_[i]] + frames_w[index_[i]] == frames_x[index_[i+1]] + frames_w[index_[i+1]])
    ###y+h=y+h
    for index_ in frame_cond.yh_equal_yh:
        for i in range(len(index_) - 1):
            if type(index_[i]) == str and type(index_[i+1]) == str:
                model.Add(combinational_frames_y[index_[i]] + combinational_frames_h[index_[i]] == combinational_frames_y[index_[i+1]] + combinational_frames_h[index_[i+1]])
            elif type(index_[i]) == str and type(index_[i+1]) == int:
                model.Add(combinational_frames_y[index_[i]] + combinational_frames_h[index_[i]] == frames_y[index_[i+1]] + frames_h[index_[i+1]])
            elif type(index_[i]) == int and type(index_[i+1]) == str:
                model.Add(frames_y[index_[i]] + frames_h[index_[i]] == combinational_frames_y[index_[i+1]] + combinational_frames_h[index_[i+1]])
            elif type(index_[i]) == int and type(index_[i+1]) == int:
                model.Add(frames_y[index_[i]] + frames_h[index_[i]] == frames_y[index_[i+1]] + frames_h[index_[i+1]])
    #######################################
    #######################################
    #关于目标函数
    ##1.比例
    pp = paper_width // 5
    hh = paper_height // 10
    for i in range(article_count + 1):
        model.Add(100*frames_w[i] <= ratio_[1] * frames_h[i] - 100 * M * (isgoodh_frames[i] - 1))
        model.Add(100*frames_h[i] <= ratio_[1] * frames_w[i] - 100 * M * (isgoodv_frames[i] - 1))
        model.Add(ratio_[0] * frames_h[i] + 100 * M * (isgoodh_frames[i] - 1) <= 100*frames_w[i])
        model.Add(ratio_[0] * frames_w[i] + 100 * M * (isgoodv_frames[i] - 1) <= 100*frames_h[i])
        ####################
        model.Add(100*frames_w[i] >= ratio1_[0]*frames_h[i]).OnlyEnforceIf(isgoodh_frames1[i])
        model.Add(100*frames_w[i] <= ratio1_[1]*frames_h[i]).OnlyEnforceIf(isgoodh_frames1[i])
        model.Add(100*frames_h[i] >= ratio1_[0]*frames_w[i]).OnlyEnforceIf(isgoodv_frames1[i])
        model.Add(100*frames_h[i] <= ratio1_[1]*frames_w[i]).OnlyEnforceIf(isgoodv_frames1[i])
        #
        model.Add(100*frames_w[i] >= ratio21_[0]*frames_h[i]).OnlyEnforceIf(isgoodh_frames21[i])
        model.Add(100*frames_w[i] <= ratio21_[1]*frames_h[i]).OnlyEnforceIf(isgoodh_frames21[i])
        model.Add(100*frames_h[i] >= ratio21_[0]*frames_w[i]).OnlyEnforceIf(isgoodv_frames21[i])
        model.Add(100*frames_h[i] <= ratio21_[1]*frames_w[i]).OnlyEnforceIf(isgoodv_frames21[i])
        #
        model.Add(100*frames_w[i] >= ratio31_[0]*frames_h[i]).OnlyEnforceIf(isgoodh_frames31[i])
        model.Add(100*frames_w[i] <= ratio31_[1]*frames_h[i]).OnlyEnforceIf(isgoodh_frames31[i])
        model.Add(100*frames_h[i] >= ratio31_[0]*frames_w[i]).OnlyEnforceIf(isgoodv_frames31[i])
        model.Add(100*frames_h[i] <= ratio31_[1]*frames_w[i]).OnlyEnforceIf(isgoodv_frames31[i])
        #
        model.Add(100*frames_w[i] >= ratio22_[0]*frames_h[i]).OnlyEnforceIf(isgoodh_frames22[i])
        model.Add(100*frames_w[i] <= ratio22_[1]*frames_h[i]).OnlyEnforceIf(isgoodh_frames22[i])
        model.Add(100*frames_h[i] >= ratio22_[0]*frames_w[i]).OnlyEnforceIf(isgoodv_frames22[i])
        model.Add(100*frames_h[i] <= ratio22_[1]*frames_w[i]).OnlyEnforceIf(isgoodv_frames22[i])
        #
        model.Add(100*frames_w[i] >= ratio32_[0]*frames_h[i]).OnlyEnforceIf(isgoodh_frames32[i])
        model.Add(100*frames_w[i] <= ratio32_[1]*frames_h[i]).OnlyEnforceIf(isgoodh_frames32[i])
        model.Add(100*frames_h[i] >= ratio32_[0]*frames_w[i]).OnlyEnforceIf(isgoodv_frames32[i])
        model.Add(100*frames_h[i] <= ratio32_[1]*frames_w[i]).OnlyEnforceIf(isgoodv_frames32[i])
        #
        model.Add(100*frames_w[i] >= ratio4_[0]*frames_h[i]).OnlyEnforceIf(isgoodh_frames4[i])
        model.Add(100*frames_w[i] <= ratio4_[1]*frames_h[i]).OnlyEnforceIf(isgoodh_frames4[i])
        model.Add(100*frames_h[i] >= ratio4_[0]*frames_w[i]).OnlyEnforceIf(isgoodv_frames4[i])
        model.Add(100*frames_h[i] <= ratio4_[1]*frames_w[i]).OnlyEnforceIf(isgoodv_frames4[i])
        ############## 
        model.Add(frames_w[i] >= pp)
        model.Add(frames_h[i] >= hh)
    ##2.留白高度-=-=-=-
    ####################
    model.Add(sum(frames_pad_height) <= maxblank )
    model.Maximize(4*sum(isgoodv_frames1) + 4*sum(isgoodh_frames1) +3*sum(isgoodv_frames21) + 3*sum(isgoodh_frames21) +3*sum(isgoodv_frames22) + 3*sum(isgoodh_frames22) +2*sum(isgoodv_frames31) + 2*sum(isgoodh_frames31) +2*sum(isgoodv_frames32) + 2*sum(isgoodh_frames32) +sum(isgoodv_frames4) + sum(isgoodh_frames4))
    #创建求解器并求解#####################################################################
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 4
    status = solver.Solve(model)
    ret = [[] for i in range(article_count+1)]
    if status == cp_model.OPTIMAL:
        # print('Maximum of objective function: %i' % solver.ObjectiveValue())
        ret.append(articles_seq_list)
        ret.append(solver.ObjectiveValue())
        for i in range(article_count+1):
            # print("pic_rr%d" % i, solver.Value(pic_rr[i]))
            # print("pic_ratio%d" % i, solver.Value(pic_ratio[i]))
            # print("==="*15 + "frame%d" % i + "==="*15)
            # print("x_%d: " % i, solver.Value(frames_x[i]) / 100)
            # print("y_%d: " % i, solver.Value(frames_y[i]) / 100)
            # print("w_%d: " % i, solver.Value(frames_w[i]) / 100)
            # print("h_%d: " % i, solver.Value(frames_h[i]) / 100)
            # print("留白高度_%d: " % i, solver.Value(frames_pad_height[i]) / 100)
            # print("文章高度_%d: " % i, solver.Value(articles_height[i]) / 100)
            # print("可用高度_%d: " % i, solver.Value(frames_available_h[i]) / 100)
            # print("可用宽度_%d: " % i, solver.Value(frames_available_w[i]) / 100)
            # print("长宽合适_%d: " % i, solver.Value(isgoodh_frames[i]) + solver.Value(isgoodv_frames[i]))
            # if i > 0 and articles_dict[articles_seq[i]].have_pics:
            #     print("矩形高度_%d: " % i, solver.Value(frames_h[i]) / 100)
            #     print("矩形宽度_%d: " % i, solver.Value(frames_w[i]) / 100)
            #     print("可用高度_%d: " % i, solver.Value(frames_available_h[i]) / 100)
            #     print("可用宽度_%d: " % i, solver.Value(frames_available_w[i]) / 100)
            #     print("图片高度_%d " % i, solver.Value(pic_height[i]) / 100)
            #     print("图片宽度_%d " % i, solver.Value(pic_width[i]) / 100)
            #     print("图片方式_%d " % i, solver.Value(picstyles_bool[i]))
            #     print("图片比例_%d " % i, solver.Value(pic_height[i]) / solver.Value(pic_width[i]))
            #     print("图片比例_%d " % i, articles_dict[articles_seq[i]].pic[0][1] / articles_dict[articles_seq[i]].pic[0][0])
            #     print("图片面积_%d " % i, solver.Value(area_[i]))
            #######
            # if solver.Value(titles_style_h_bool[i]):
            #     print("标题方式_%d: " % i, "横标题")
            #     print("大标题字号%d: " % i, solver.Value(atitle_font_pts[i]))
            #     if solver.Value(atitles_rows_bool[i]):
            #         print("大标题行数_%d: " % i, 1)
            #     else:
            #         print("大标题行数_%d: " % i, 2)
            #     if solver.Value(ftitles_height[i]) > 0:
            #         if solver.Value(ftitles_rows_bool[i]):
            #             print("副标题行数_%d: " % i, 1)
            #         else:
            #             print("副标题行数_%d: " % i, 2)
            #     else:
            #         print("副标题行数_%d: " % i, 0)
            #     if solver.Value(ytitles_height[i]) > 0:
            #         if solver.Value(ytitles_rows_bool[i]):
            #             print("引标题行数_%d: " % i, 1)
            #         else:
            #             print("引标题行数_%d: " % i, 2)
            #     else:
            #         print("引标题行数_%d: " % i, 0)
            #     print("大标题高度_%d: ", solver.Value(atitles_height[i]) / 100)
            #     print("副标题高度_%d: ", solver.Value(ftitles_height[i]) / 100)
            #     print("引标题高度_%d: ", solver.Value(ytitles_height[i]) / 100)
            #     print("标题高度_%d: ", (solver.Value(atitles_height[i]) + solver.Value(ftitles_height[i]) + solver.Value(ytitles_height[i]))  / 100)
            #     print("正文高度_%d: ", solver.Value(texts_height[i]) / 100)
            # else:
            #     print("标题方式_%d: " % i, "竖标题")
            #     print("大标题字号%d: " % i, solver.Value(atitle_font_pts[i]))
            #     if solver.Value(atitles_rows_bool[i]):
            #         print("大标题列数_%d: " % i, 1)
            #     else:
            #         print("大标题列数_%d: " % i, 2)
            #     if solver.Value(ftitles_height[i]) > 0:
            #         if solver.Value(ftitles_rows_bool[i]):
            #             print("副标题列数_%d: " % i, 1)
            #         else:
            #             print("副标题列数_%d: " % i, 2)
            #     else:
            #         print("副标题列数_%d: " % i, 0)
            #     if solver.Value(ytitles_height[i]) > 0:
            #         if solver.Value(ytitles_rows_bool[i]):
            #             print("引标题列数_%d: " % i, 1)
            #         else:
            #             print("引标题列数_%d: " % i, 2)
            #     else:
            #         print("引标题列数_%d: " % i, 0)
            #     print("大标题高度_%d: " % i, solver.Value(atitles_height[i]) / 100)
            #     print("大标题宽度_%d: " % i, solver.Value(atitles_w[i]) / 100)
            #     print("副标题高度_%d: " % i, solver.Value(ftitles_height[i]) / 100)
            #     print("副标题宽度_%d: " % i, solver.Value(ftitles_w[i]) / 100)
            #     print("引标题高度_%d: " % i, solver.Value(ytitles_height[i]) / 100)
            #     print("引标题宽度_%d: " % i, solver.Value(ytitles_w[i]) / 100)
            #     print("标题高度_%d: " % i, solver.Value(titlesh[i]) / 100)
            #     print("标题宽度_%d: " % i, solver.Value(titlesw[i]) / 100)
            #     print("正文高度_%d: " % i, solver.Value(textsh[i]) / 100)
            # print("正文栏数_%d: " % i, solver.Value(texts_columns[i]))
            #######
            #######
            ret[i] = [solver.Value(frames_x[i])/paper_params.paper_width,solver.Value(frames_y[i])/paper_params.paper_height,solver.Value(frames_w[i])/paper_params.paper_width,solver.Value(frames_h[i])/paper_params.paper_height,solver.Value(atitle_font_pts[i]),solver.Value(atitles_rows_bool[i]),solver.Value(ftitles_rows_bool[i]),solver.Value(ytitles_rows_bool[i]),solver.Value(titles_style_h_bool[i])]
        # for i in range(5):
        #     print(solver.Value(levels_font[i]))
        # print(level_title_font_range)
        return ret
    # else:
    #     print("no optimal solution")
        


if __name__ == '__main__':
    filepath = "./testdocx/jh2.docx"
    # s = "C25(R68()())(R42()(R64()(C64()())))"
    s = "C70(R38()(R56()(R75()())))(R63()())"#page结构字符串，通过模型推断得到
    s = "C1(R1()(R1()(R1()())))(R1()())"#page结构字符串，通过模型推断得到
    # start = time.time()
    #####################################################
    frame_cond = frameString2Framecond(s)#page结构对象
    head_infer = 70#head大小位置
    pic_infer = 0.12#pic大小
    paper_params = Paper_Params()#paper设置参数
    articles_dict = get_article_dic(filepath)#新闻文章字典
    tmp = [1,2,3,4,5,5,7,4,4,4]
    articles_dict[1].ishead = True
    for key in articles_dict:
        # print(key, '------'*100)
        articles_dict[key].level = tmp.pop(0)
        articles_dict[key].isgraghnews = False
        if articles_dict[key].have_pics:
            if articles_dict[key].count_paras_char < 200:  
                articles_dict[key].isgraghnews = True
        # for k,v in articles_dict[key].__dict__.items():
        #     print(k,":  ",v)
    seqs = [seq for seq in permutations(range(1,7)) if seq[0]==1]
    #######################
    sss = []
    for seq in seqs:
        if sum([abs(i-j) for i,j in enumerate(seq)]) <= 10:
            sss.append(seq)
    #######################
    seqs = sss
    start = time.time()
    count = 0
    for articles_seq_list in seqs:#新闻矩形匹配序列
        ret = main(frame_cond, articles_seq_list, head_infer, pic_infer, articles_dict, paper_params,1000)
        if ret:
            print(ret)
            count += 1
        if count > 10:
            break
        # print(ret)
        # visulizeThePage(ret[:7])
    print("time:", time.time() - start)
    print(count)