from itertools import permutations
import matplotlib.pyplot as plt
import numpy as np
from user_setting import Paper_Params
from ortools.sat.python import cp_model
from str2tree import Frame_cond, frameString2Framecond
from process_docx_ import get_article_dic, Article
import time
# import zzz
# import tools1

def main(frame_cond:Frame_cond, articles_seq_list:tuple, head_infer, pic_infer, articles_dict:dict, paper_params:Paper_Params):
    """以frame_cond为矩形约束，文章大小列表articles_seq_list的条件下，进行矩形划分"""
    #建立模型
    model = cp_model.CpModel()
    article_count = len(articles_seq_list)
    articles_seq = [0] + list(articles_seq_list)
    ###################################################
    #######已知条件（统一单位0.01mm）
    paper_width = 100 * paper_params.paper_width                                                       #paper宽度（默认320mm）
    paper_height = 100 * paper_params.paper_height                                                     #paper高度（默认500mm）
    ##################################################################################################################
    #创建变量
    #frame变量
    frames_x = [model.NewIntVar(0, paper_width, "frames_x_%d" % i) for i in range(article_count + 1)]#x坐标
    frames_y = [model.NewIntVar(0, paper_height, "frames_y_%d" % i) for i in range(article_count + 1)]#y坐标
    frames_w = [model.NewIntVar(5000, paper_width, "frames_w_%d" % i) for i in range(article_count + 1)]#w宽度
    frames_h = [model.NewIntVar(5000, paper_height, "frames_h_%d" % i) for i in range(article_count + 1)]#h高度
    combinational_frames_x = {str(i) : model.NewIntVar(0, paper_width, "combinational_frames_x_%d" % i) for i in range(article_count - 1)}
    combinational_frames_y = {str(i) : model.NewIntVar(0, paper_height, "combinational_frames_y_%d" % i) for i in range(article_count - 1)}
    combinational_frames_w = {str(i) : model.NewIntVar(0, paper_width, "combinational_frames_w_%d" % i) for i in range(article_count - 1)}
    combinational_frames_h = {str(i) : model.NewIntVar(0, paper_height, "combinational_frames_h_%d" % i) for i in range(article_count - 1)}
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
    for i in range(1, article_count + 1):
        model.Add(frames_w[i] >= paper_width//4)
        model.Add(frames_h[i] >= paper_height//20)
        if articles_dict[articles_seq[i]].ishead:
            model.Add(frames_y[i] == paper_params.paper_height * 17)
            continue
        for j in range(i+1, article_count + 1):
            if articles_dict[articles_seq[i]].isgraghnews or articles_dict[articles_seq[j]].isgraghnews or articles_dict[articles_seq[j]].ishead:
                continue
            if articles_dict[articles_seq[i]].level > articles_dict[articles_seq[j]].level:
                model.Add(2*frames_x[i]+frames_w[i]+2*frames_y[i]+frames_h[i] >= 2*frames_x[j]+frames_w[j]+2*frames_y[j]+frames_h[j]-2*(paper_width+paper_height)//15)
            elif articles_dict[articles_seq[i]].level < articles_dict[articles_seq[j]].level:
                model.Add(2*frames_x[i]+frames_w[i]+2*frames_y[i]+frames_h[i] <= 2*frames_x[j]+frames_w[j]+2*frames_y[j]+frames_h[j]-2*(paper_width+paper_height)//15)
    #######################################
    #关于目标函数
    model.Maximize(sum(frames_x))
    #创建求解器并求解#####################################################################
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 8
    status = solver.Solve(model)
    ret = [[] for i in range(article_count+1)]
    if status == cp_model.OPTIMAL :
        ret.append(articles_seq_list)
        ret.append(solver.ObjectiveValue())
        for i in range(article_count+1):
            ret[i] = [solver.Value(frames_x[i])/paper_params.paper_width,solver.Value(frames_y[i])/paper_params.paper_height,solver.Value(frames_w[i])/paper_params.paper_width,solver.Value(frames_h[i])/paper_params.paper_height]
        return ret
    

if __name__ == '__main__':
    start = time.time()
    ret = []
    filepath = "./testdocx/jh2.docx"
    S = ['C1(R1()(R1()()))(R1()(R1()()))', 'C1(R1()())(R1()(R1()(C1()())))','C1(R1()(R1()(R1()())))(R1()())','C1(R1()(R1(C1()())()))(R1()())','R1()(C1(R1()(R1()()))(R1()()))','C1(R1()())(R1()(R1()(R1()())))','C1(R1()(R1()(C1()())))(R1()())']
    # #####################################################
    # paper_params = Paper_Params()#paper设置参数
    # articles_dict = zzz.preproArtDict(filepath, [1,2,3,4,5,6,7])
    # for k,v in articles_dict[1].__dict__.items():
    #     print(k,':',v)
    # article_count = len(articles_dict)
    # seqs = [seq for seq in permutations(range(1,article_count+1))]
    # print(len(seqs)*len(S))
    # for s in S:
    #     ret = []
    #     frame_cond = frameString2Framecond(s)#page结构对象
    #     for seq in seqs:
    #         t = main(frame_cond, seq, 0, 0, articles_dict, paper_params)
    #         if t:
    #             ret.append(t)
    #             # print(t)
    #             # tools1.visulizeThePage(t[:7])
    #     print(len(ret))
    #     # break
    # # visulizeThePage(ret[:7])
    # print("time:", time.time() - start)
