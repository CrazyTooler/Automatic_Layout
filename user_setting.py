class Paper_Params:
    def __init__(self) -> None:
        self.paper_width = 320#paper宽度（320mm）
        self.paper_height = 500#paper高度（500mm）
        self.frame_width_gap = 5#文章距离两侧边框的距离左右为(5mm)
        self.frame_height_gap = 2#文章距离两侧边框的距离上下为(0mm)
        self.title_subtitle_gap = 3#主标题与子标题之间的距离(3mm)
        self.title_text_gap = 5#标题区域与正文区域之间的距离(5mm)
        self.column_gap = 5#栏距5mm（单位：mm）
        self.pt = 35 ##100*0.35pt与mm换算（单位：0.01mm）1pt = 0.35mm
        self.level_font_gap = 4 ##不同等级标题之间至少4pt差距
        self.subtitle_font_pt = 21#副标题字号(单位：pt)
        self.text_font_width_pt = 9#正文字符宽度（单位：pt）
        self.text_font_height_pt = 13#正文字符高度（单位：pt）10pt外加行高
        self.level1_title_font = [30, 60]#新闻等级下标题字号范围
        self.level2_title_font = [30, 55]
        self.level3_title_font = [30, 50]
        self.level4_title_font = [30, 45]
        self.level5_title_font = [30, 40]
        self.ratio = [0.56, 0.68]
        self.ratio21 = [0.69, 0.8]
        self.ratio22 = [0.45, 0.55]
        self.ratio31 = [0.81, 1]
        self.ratio32 = [0.31, 0.44]
        self.ratio4 = [0.01, 0.3]
