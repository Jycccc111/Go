import numpy as np

def create_a_game():
    board = np.ones((21, 21), dtype=np.int8)*2
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
                        local_clusters[current_cluster].append(clusters[i])
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

def eat(board,clusters,color):
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
        i += 1
    if (not eaten) and self_eaten:
        error = True
        print("error1")
    if eaten:
        for i in sorted(dead_index2, reverse=True):
            count = 0
            for x, y, color in clusters[i]:
                board[x, y] = 0
                print(x,y,"iseated")
                count += 1
            del clusters[i]
            if count == 1:
                if color == 1:
                    lasteated1 = [x,y]
                else:
                    lasteated2 = [x,y]


    return error, clusters, board,lasteated1,lasteated2

class GoGame:

    def __init__(self):

        self.board=create_a_game()

        self.clusters=[]

        self.count=1

        self.lasteated1=[]

        self.lasteated2=[]

    def move(self,x,y):

        error1=False
        error2=False
        error3=False


        position=[x,y]


        if self.board[x,y]!=0:
            error3=True


        if self.count%2==1:

            color=1

            if self.lasteated1==position:
                error2=True

        else:

            color=-1

            if self.lasteated2==position:
                error2=True



        if not(error2 or error3):

            self.board[x,y]=color


            temp_clusters=update_clusters(
                position,
                self.clusters,
                color
            )


            error1,temp_clusters,self.board,self.lasteated1,self.lasteated2=eat(
                self.board,
                temp_clusters,
                color
            )


        if error1 or error2:

            self.board[x,y]=0

            return False


        else:

            self.clusters=temp_clusters

            if not error3:
                self.count+=1


            return True