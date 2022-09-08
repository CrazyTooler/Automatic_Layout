class Frame_cond:
    """矩形约束对象，用于描述ortools需要添加的矩形约束"""
    def __init__(self) -> None:
        self.x_equal_x = []
        self.y_equal_y = []
        self.xw_equal_xw = []
        self.yh_equal_yh = []
        self.xw_equal_x = []
        self.yh_equal_y = []
        self.pagetree = ""

class ManuTreeNode:
    def __init__(self, val=0, nodetype=None, sval=0, leftchild=None, rightchild=None) -> None:
        self.val = val
        self.type = nodetype
        self.serial = sval
        self.left = leftchild
        self.right = rightchild

def getTwochild(s):
    count = 0
    startIndex = []
    endIndex = []
    for i, ch in enumerate(s):
        if ch == '(':
            count += 1
            if count == 1:
                startIndex.append(i)
        elif ch == ')':
            count -= 1
            if count == 0:
                endIndex.append(i)
    return zip(startIndex, endIndex)

def str2_Tree(s:str) -> ManuTreeNode:
    if s == "":
        return None
    else:
        index1, index2 = getTwochild(s)
        val = int(s[1:index1[0]])
        root = ManuTreeNode(val=val, nodetype=s[0])
        root.left = str2_Tree(s[index1[0]+1 : index1[1]])
        root.right = str2_Tree(s[index2[0]+1 : index2[1]])
        return root

def preOrderInsert(root:ManuTreeNode):
    stk = [root]
    mserial = 0
    nserial = 1
    while stk:
        node = stk.pop()
        if node.type in "RC":
            node.serial = mserial
            mserial += 1
            if not node.left:
                node.left = ManuTreeNode(nodetype="N")
            if not node.right:
                node.right = ManuTreeNode(nodetype="N")
        elif node.type in "N":
            node.serial = nserial
            nserial += 1
        if node.right:
            stk.append(node.right)
        if node.left:
            stk.append(node.left)

def preOrderSearch(root:ManuTreeNode):
    if root:
        if root.type in "RC":
            print(root.serial)
        preOrderSearch(root.left)
        preOrderSearch(root.right)

def s2tree(s:str):
    root = str2_Tree(s)
    preOrderInsert(root)
    return root

def tree2framecond(root:ManuTreeNode, s:str) -> Frame_cond:
    frame_cond = Frame_cond()
    frame_cond.pagetree = s
    stk = [root]
    while stk:
        node = stk.pop()
        if node.type == 'R':
            if node.left.type in "RC" and node.right.type in "RC":
                frame_cond.x_equal_x.append((str(node.serial), str(node.left.serial), str(node.right.serial)))
                #####################################
                frame_cond.xw_equal_xw.append((str(node.serial), str(node.left.serial), str(node.right.serial)))
                #####################################
                frame_cond.y_equal_y.append((str(node.serial), str(node.left.serial)))
                #####################################
                frame_cond.yh_equal_y.append((str(node.left.serial), str(node.right.serial)))
                #####################################
                frame_cond.yh_equal_yh.append((str(node.serial), str(node.right.serial)))
            elif node.left.type not in "RC" and node.right.type in "RC":
                frame_cond.x_equal_x.append((str(node.serial), node.left.serial, str(node.right.serial)))
                #####################################
                frame_cond.xw_equal_xw.append((str(node.serial), node.left.serial, str(node.right.serial)))
                #####################################
                frame_cond.y_equal_y.append((str(node.serial), node.left.serial))
                #####################################
                frame_cond.yh_equal_y.append((node.left.serial, str(node.right.serial)))
                #####################################
                frame_cond.yh_equal_yh.append((str(node.serial), str(node.right.serial)))
            elif node.left.type in "RC" and node.right.type not in "RC":
                frame_cond.x_equal_x.append((str(node.serial), str(node.left.serial), node.right.serial))
                #####################################
                frame_cond.xw_equal_xw.append((str(node.serial), str(node.left.serial), node.right.serial))
                #####################################
                frame_cond.y_equal_y.append((str(node.serial), str(node.left.serial)))
                #####################################
                frame_cond.yh_equal_y.append((str(node.left.serial), node.right.serial))
                #####################################
                frame_cond.yh_equal_yh.append((str(node.serial), node.right.serial))
            else:
                frame_cond.x_equal_x.append((str(node.serial), node.left.serial, node.right.serial))
                #####################################
                frame_cond.xw_equal_xw.append((str(node.serial), node.left.serial, node.right.serial))
                #####################################
                frame_cond.y_equal_y.append((str(node.serial), node.left.serial))
                #####################################
                frame_cond.yh_equal_y.append((node.left.serial, node.right.serial))
                #####################################
                frame_cond.yh_equal_yh.append((str(node.serial), node.right.serial))
        elif node.type == 'C':
            if node.left.type in "RC" and node.right.type in "RC":
                frame_cond.x_equal_x.append((str(node.serial), str(node.left.serial)))
                #####################################
                frame_cond.xw_equal_x.append((str(node.left.serial), str(node.right.serial)))
                #####################################
                frame_cond.xw_equal_xw.append((str(node.serial), str(node.right.serial)))
                #####################################
                frame_cond.y_equal_y.append((str(node.serial), str(node.left.serial), str(node.right.serial)))
                #####################################
                frame_cond.yh_equal_yh.append((str(node.serial), str(node.left.serial), str(node.right.serial)))
            elif node.left.type not in "RC" and node.right.type in "RC":
                frame_cond.x_equal_x.append((str(node.serial), node.left.serial))
                #####################################
                frame_cond.xw_equal_x.append((node.left.serial, str(node.right.serial)))
                #####################################
                frame_cond.xw_equal_xw.append((str(node.serial), str(node.right.serial)))
                #####################################
                frame_cond.y_equal_y.append((str(node.serial), node.left.serial, str(node.right.serial)))
                #####################################
                frame_cond.yh_equal_yh.append((str(node.serial), node.left.serial, str(node.right.serial)))
            elif node.left.type in "RC" and node.right.type not in "RC":
                frame_cond.x_equal_x.append((str(node.serial), str(node.left.serial)))
                #####################################
                frame_cond.xw_equal_x.append((str(node.left.serial), node.right.serial))
                #####################################
                frame_cond.xw_equal_xw.append((str(node.serial), node.right.serial))
                #####################################
                frame_cond.y_equal_y.append((str(node.serial), str(node.left.serial), node.right.serial))
                #####################################
                frame_cond.yh_equal_yh.append((str(node.serial), str(node.left.serial), node.right.serial))
            else:
                frame_cond.x_equal_x.append((str(node.serial), node.left.serial))
                #####################################
                frame_cond.xw_equal_x.append((node.left.serial, node.right.serial))
                #####################################
                frame_cond.xw_equal_xw.append((str(node.serial), node.right.serial))
                #####################################
                frame_cond.y_equal_y.append((str(node.serial), node.left.serial, node.right.serial))
                #####################################
                frame_cond.yh_equal_yh.append((str(node.serial), node.left.serial, node.right.serial))
        ########################
        if node.right:
            stk.append(node.right)
        if node.left:
            stk.append(node.left)
    return frame_cond

def frameString2Framecond(s:str) -> Frame_cond:
    root = s2tree(s)
    return tree2framecond(root, s)

def main():
    root = s2tree("C25(R68()())(R42()(R64()(C64()())))")
    preOrderSearch(root)
    frame_cond = tree2framecond(root, "C25(R68()())(R42()(R64()(C64()())))")
    for k,v in frame_cond.__dict__.items():
        print(k, v)

if __name__ == "__main__":
    main()