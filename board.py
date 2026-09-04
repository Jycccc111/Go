import numpy as np
import copy




def create_a_game():
    board = np.ones((21, 21),dtype=int)*2
    board[1:20,1:20] = 0
    return board

def adjacent(object1,object2):
    if object1[-1] == object2[-1]:
        if ((object1[0] - object2[0]) == 1 or (object1[0] - object2[0]) == -1) and ((object1[1] - object2[1]) == 0):
            return True
        elif ((object1[1] - object2[1]) == 1 or (object1[1] - object2[1]) == -1) and ((object1[0] - object2[0]) == 0):
            return True
    return False

def update_clusters(position,clusters,color):
    local_clusters = clusters.copy()
    cluster = []
    position.append(color)
    entity = position
    cluster_found = False
    if not clusters:
        local_clusters.append(cluster)
        local_clusters[0].append(entity)
    else:
        i = 0

        added_index = []
        while i < len(clusters):
            j = 0
            while j < len(clusters[i]):
                is_same_cluster = adjacent(entity,clusters[i][j])
                if is_same_cluster and not cluster_found:
                    cluster_found = True
                    local_clusters[i].append(entity)
                    current_cluster = i
                if is_same_cluster and cluster_found:
                    if current_cluster != i:
                        added_index.append(i)
                        local_clusters[current_cluster].extend(clusters[i])
                        break
                j += 1
            i += 1
        if not cluster_found:
            local_clusters.append(cluster)
            local_clusters[i].append(entity)
        if not added_index:
            return local_clusters
        for i in sorted(added_index, reverse=True):
            del local_clusters[i]
    return local_clusters

def findair(board,position):
    x = position[0]
    y = position[1]
    if board[x+1,y] == 0 or board[x-1,y] == 0 or board[x,y+1] == 0 or board[x,y-1] == 0:
        return True
    return False

def find_num_air(board,positions,air_count):
    airlist = []
    air_count = np.zeros([19,19],dtype = int)
    for x,y,z in positions:
        if board[x + 1, y] == 0 and [x + 1, y] not in airlist:
            airlist.append([x + 1, y])
        if board[x-1,y] == 0 and [x-1,y] not in airlist:
            airlist.append([x-1,y])
        if board[x,y+1] == 0 and [x,y+1]  not in airlist:
            airlist.append([x,y+1])
        if board[x,y-1] == 0 and [x,y-1]not in airlist:
            airlist.append([x,y-1])
    num_air = len(airlist)
    for x, y,z in positions:
        air_count[x-1,y-1] = num_air
    return air_count



def tryeat(board,clusters,color):
    count = 0
    eaten = False
    self_eaten = False
    error = False
    i = 0
    dead_index1 = -1
    dead_index2 = []
    while i < len(clusters):
        j = 0
        alive = False
        while j < len(clusters[i]):
            air = findair(board, clusters[i][j])
            if air:
                alive = True
                break
            j += 1
        if not alive:
            x, y, color1 = clusters[i][0]
            if color == color1:
                self_eaten = True
                dead_index1 = i

            else:
                eaten = True
                dead_index2.append(i)
        i += 1
    if (not eaten) and self_eaten:
        error = True
    if not error and self_eaten:
        if color1 == 1:
            last1 = []
            for x, y, z in clusters[dead_index1]:
                last1.append([x, y])
        else:
            last2 = []
            for x, y, z in clusters[dead_index1]:
                last2.append([x, y])
    if eaten:
        for i in sorted(dead_index2, reverse=True):
            count = 0
            for x, y, color in clusters[i]:
                #board[x, y] = 0
                count += 1
            #del clusters[i]

    return error, count
def eat(board,clusters,color,last1,last2):

    eaten = False
    self_eaten = False
    error = False
    i = 0
    lasteated2 = []
    lasteated1 = []
    dead_index1 = -1
    dead_index2 = []
    while i < len(clusters):
        j = 0
        alive = False
        while j < len(clusters[i]):
            air = findair(board,clusters[i][j])
            if air:
                alive = True
                break
            j += 1
        if not alive:
            x,y,color1 = clusters[i][0]
            if color == color1:
                self_eaten = True
                dead_index1 = i

            else:
                eaten = True
                dead_index2.append(i)
                if color1 == -1:
                    last1 = []
                else:
                    last2 = []
        i += 1
    if (not eaten) and self_eaten:
        error = True
        print("error1")
    if not error and self_eaten:
        if color1 == 1:
            last1 = []
            for x,y,z in clusters[dead_index1]:
                last1.append([x,y])
        else:
            last2 = []
            for x, y, z in clusters[dead_index1]:
                last2.append([x, y])
    if eaten:
        for i in sorted(dead_index2, reverse=True):
            count = 0
            for x, y, color in clusters[i]:
                board[x, y] = 0
                if color == 1:
                    last1.append([x, y])
                else:
                    last2.append([x, y])
                count += 1
            del clusters[i]
            if count == 1:
                if color == 1:
                    lasteated1 = [x,y]
                else:
                    lasteated2 = [x,y]


    return error, clusters, board,lasteated1,lasteated2,last1,last2
def get_group_and_liberties(board, x, y):
    """
    从 (x, y) 开始寻找整个棋块，并返回：
    group: 棋块中的所有位置
    liberties: 棋块所有不同的气
    """

    color = board[x, y]

    if color == 0 or color == 2:
        return [], set()

    group = []
    liberties = set()

    stack = [(x, y)]
    visited = {(x, y)}

    while stack:
        cx, cy = stack.pop()

        group.append((cx, cy))

        for nx, ny in (
            (cx + 1, cy),
            (cx - 1, cy),
            (cx, cy + 1),
            (cx, cy - 1)
        ):

            value = board[nx, ny]

            if value == 0:
                liberties.add((nx, ny))

            elif value == color and (nx, ny) not in visited:
                visited.add((nx, ny))
                stack.append((nx, ny))

    return group, liberties

class GoGame:

    def __init__(self):

        self.board=create_a_game()

        self.clusters=[]

        self.count=1

        self.lasteated1=[]

        self.lasteated2=[]

        self.lasteaten1 = []

        self.lasteaten2 = []

        self.lastmove = 22,22

        self.history = np.zeros((19, 19),dtype=int)

        self.aircount = np.zeros((19, 19), dtype=int)

    def add_stone(self, x, y, color):

        self.board[x, y] = color

        self.clusters = update_clusters(
            [x, y],
            self.clusters,
            color
        )

    def move(self, x, y, color=None,loading = False):

        temp_clusters = self.clusters.copy()

        error1=False
        error2=False
        error3=False


        position=[x,y]


        if self.board[x,y]!=0:
            error3=True

        if color is None:
            if self.count % 2 == 1:

                color = 1

                if self.lasteated1 == position:
                    error2 = True

            else:

                color = -1

                if self.lasteated2 == position:
                    error2 = True

        if not(error2 or error3):
            if loading:
                temp_board = self.board.copy()
                temp_board[x, y] = color

                temp_clusters = update_clusters(
                    position,
                    temp_clusters,
                    color
                )

                error1, temp_clusters, temp_board, q, w, e, r = eat(
                    temp_board,
                    temp_clusters,
                    color,
                    self.lasteaten1,
                    self.lasteaten2
                )

            else:
                self.board[x,y]=color
                temp_clusters=update_clusters(
                    position,
                    self.clusters,
                    color
                )


                error1,temp_clusters,self.board,self.lasteated1,self.lasteated2,self.lasteaten1,self.lasteaten2=eat(
                    self.board,
                    temp_clusters,
                    color,
                    self.lasteaten1,
                    self.lasteaten2
                )

        if error1 or error2:

            self.board[x,y]=0

            return False,self.lasteaten1,self.lasteaten2

        else:

            self.clusters=temp_clusters
            self.history[x - 1, y - 1] = self.count
            if not error3:
                self.count+=1
            self.lastmove = x-1,y-1

            return True,self.lasteaten1,self.lasteaten2,self.history

    def getinfo(self):
        self.aircount = np.zeros((19, 19), dtype=int)
        for i in self.clusters:
            find_num_air(self.board,i,self.aircount)
        return self.aircount

    def trymove(self, x, y, color=None):

        # =====================================
        # 1. 确定颜色
        # =====================================

        if color is None:

            if self.count % 2 == 1:
                color = 1

                # Ko
                if self.lasteated1 == [x, y]:
                    return False, 0

            else:
                color = -1

                # Ko
                if self.lasteated2 == [x, y]:
                    return False, 0

        # =====================================
        # 2. 位置不是空的
        # =====================================

        if self.board[x, y] != 0:
            return False, 0

        # =====================================
        # 3. 临时棋盘
        # =====================================

        temp_board = self.board.copy()

        # 模拟落子
        temp_board[x, y] = color

        opponent = -color

        captured = 0

        # =====================================
        # 4. 检查四个相邻的敌方棋块
        # =====================================

        checked_opponent = set()

        neighbors = (
            (x + 1, y),
            (x - 1, y),
            (x, y + 1),
            (x, y - 1)
        )

        for nx, ny in neighbors:

            # 不是敌人
            if temp_board[nx, ny] != opponent:
                continue

            # 这个棋块已经检查过
            if (nx, ny) in checked_opponent:
                continue

            # 找整个敌方棋块
            group, liberties = get_group_and_liberties(
                temp_board,
                nx,
                ny
            )

            # 标记这个棋块已经检查
            checked_opponent.update(group)

            # =================================
            # 没有气 -> 提子
            # =================================

            if len(liberties) == 0:

                captured += len(group)

                for gx, gy in group:
                    temp_board[gx, gy] = 0

        # =====================================
        # 5. 检查自己的棋块有没有气
        # =====================================

        my_group, my_liberties = get_group_and_liberties(
            temp_board,
            x,
            y
        )

        # =====================================
        # 6. 没有气 -> 自杀
        # =====================================

        if len(my_liberties) == 0:
            return False, 0

        # =====================================
        # 7. 合法
        # =====================================

        return True, captured

