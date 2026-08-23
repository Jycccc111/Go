import numpy as np
from data_loader import SGFLoader
def adjacent(object1,object2,isair):
    if not isair:
        if object1[-1] != object2[-1]:
            return False
    if ((object1[0] - object2[0]) == 1 or (object1[0] - object2[0]) == -1) and ((object1[1] - object2[1]) == 0):
        return True
    elif ((object1[1] - object2[1]) == 1 or (object1[1] - object2[1]) == -1) and ((object1[0] - object2[0]) == 0):
        return True
    return False
def create_airclusters(board):
    airclusters = []
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i,j] == 0:
                position = [i,j]
                airclusters = update_airs(position, airclusters)
    return airclusters
def create_clusters(board):
    clusters = []
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i,j] == 1 or board[i,j] == -1:
                position = [i,j]
                clusters = update_clusters(position, clusters,board[i,j])
    return clusters

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
                is_same_cluster = adjacent(entity,clusters[i][j],isair =False)
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

def update_airs(position,clusters):
    local_clusters = clusters.copy()
    cluster = []
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
                if len(clusters[i]) == 1:
                    [a] = clusters[i]
                    is_same_cluster = adjacent(entity, a,isair=True)
                else:
                    is_same_cluster = adjacent(entity,clusters[i][j],isair=True)
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

def load_info(filename):
    sgf_file = filename

    loader = SGFLoader(sgf_file)
    loader.load()
    board = loader.to_numpy()
    result = loader.result
    komi = loader.komi
    handicap = loader.handicap
    return board,result,komi,handicap

def check_single_point(position,board,clusters):
    output = 0
    link = []
    x,y = position
    is_black = False
    is_white = False
    for i in range(len(clusters)):
        cluster = clusters[i]
        if ([x+1,y,1] in cluster) or ([x+1,y,-1] in cluster):
            link.append(i)
            a,b,color = cluster[0]
            if color == 1:
                is_black = True
            else:
                is_white = True
        if ([x-1,y,1] in cluster) or ([x-1,y,-1] in cluster):
            link.append(i)
            a, b, color = cluster[0]
            if color == 1:
                is_black = True
            else:
                is_white = True
        if ([x,y+1,1] in cluster) or ([x,y+1,-1] in cluster):
            link.append(i)
            a, b, color = cluster[0]
            if color == 1:
                is_black = True
            else:
                is_white = True
        if ([x,y-1,1] in cluster) or ([x,y-1,-1] in cluster):
            link.append(i)
            a, b, color = cluster[0]
            if color == 1:
                is_black = True
            else:
                is_white = True
    if is_black and is_white:
        output = 0
    elif is_black:
        output = 1
    elif is_white:
        output = -1
    else:
        output = 2
    return output,link
def check_color_around(aircluster,board,clusters):
    i = 0
    is_black = False
    is_white = False
    is_mixed = False
    link = []
    while i < len(aircluster):
        index,temp_link= check_single_point(aircluster[i],board,clusters)
        link.extend(temp_link)
        if index == 1:
            is_black = True
        if index == -1:
            is_white = True
        if index == 0:
            is_mixed = True
        i += 1
    if is_black and is_white:
        return 0,link
    elif is_mixed:
        return 0,link
    elif is_black:
        return 1,link
    return -1,link

def check_alive(cluster,airclusters,board):
    num_eyes = 0
    Is_eye_list = np.zeros(len(airclusters))
    for x,y,color in cluster:
        for i in range(len(airclusters)):
            for j in range(len(airclusters[i])):
                is_same_cluster = adjacent([x,y], airclusters[i][j], isair=True)
                if is_same_cluster and Is_eye_list[i] == 0:
                    num_eyes += 1
                    Is_eye_list[i] = 1
    return num_eyes


def update_alive_info(alive_clusters,undefined_cluster_list,dead_clusters,alive_index,undefined_index,relation_mat,dead_index,pos):
    cluster_relation = np.dot(relation_mat.T, relation_mat)
    current_cluster = alive_clusters[pos]
    current_position = alive_index[pos]
    adjacent_list = [i for i, x in enumerate(cluster_relation[current_position]) if x > 0]
    for i in range(len(adjacent_list)):
        if adjacent_list[i] in undefined_index:
            position = undefined_index.index(adjacent_list[i])
            checked_cluster = undefined_cluster_list[position]
            a,b,color1 = current_cluster[0]
            c,d,color2 = checked_cluster[0]
            if color1 == color2:
                alive_clusters.append(checked_cluster)
                alive_index.append(adjacent_list[i])
            else:
                checked_cluster1 = checked_cluster.copy()
                for j in checked_cluster1:
                        j[-1] = -j[-1]
                dead_clusters.append(checked_cluster)
                dead_index.append(adjacent_list[i])
                alive_clusters.append(checked_cluster1)
                alive_index.append(adjacent_list[i])

            del undefined_cluster_list[position]
            del undefined_index[position]
    pos += 1
    if pos >= len(alive_clusters):
        return alive_clusters, undefined_cluster_list, dead_clusters, alive_index, undefined_index,relation_mat, dead_index

    else:
        return update_alive_info(alive_clusters, undefined_cluster_list, dead_clusters, alive_index, undefined_index,
                          relation_mat, dead_index,pos)
def find_air_numnber(board,cluster):
    num_air = 0
    air_found = []
    for x,y,color in cluster:
        if board[x+1,y] == 0 and [x+1,y] not in air_found:
            num_air+=1
            air_found.append([x+1,y])
        if board[x-1,y] == 0 and [x-1,y] not in air_found:
            num_air+=1
            air_found.append([x - 1, y])
        if board[x,y+1] == 0 and [x,y+1] not in air_found:
            num_air+=1
            air_found.append([x , y+ 1])
        if board[x,y-1] == 0 and [x,y-1] not in air_found:
            num_air+=1
            air_found.append([x , y- 1])
    return num_air
def find_all_air_number(board,clusters):
    air_num_list = []
    for i in range(len(clusters)):
        cluster = clusters[i]
        num_air = find_air_numnber(board,cluster)
        air_num_list.append(num_air)
    return air_num_list

def classifier(max_cluster,alive_clusters,dead_clusters,clusters):
    x,y,color1 = max_cluster[0]
    for cluster in clusters:
        x,y,color2 = cluster[0]
        if color1 == color2:
            alive_clusters.append(cluster)
        else:
            dead_clusters.append(cluster)
    return alive_clusters,dead_clusters
def find_combat_groups(combat_mat):

    n=len(combat_mat)

    visited=set()

    groups=[]


    def dfs(i,group):

        visited.add(i)
        group.append(i)

        for j in range(n):

            if combat_mat[i][j]==1 and j not in visited:

                dfs(j,group)



    for i in range(n):

        if i not in visited:

            group=[]

            dfs(i,group)

            groups.append(group)


    return groups
def cal_combat(alive_clusters, undefined_clusters,undefined_eye_list,board,undefined_mat,undefined_index):
    dead_clusters = []
    print(undefined_mat)
    double_alive_clusters = []
    combat_clusters_list=find_combat_groups(undefined_mat)
    print(combat_clusters_list)
    for group in combat_clusters_list:
        print("group:")
        for i in group:
            print(
                "local:",
                i,
                "real:",
                undefined_index[i]
            )
    for i in range(len(combat_clusters_list)):
        single_combat = combat_clusters_list[i]
        one_eye_group = []
        for j in single_combat:
            if undefined_eye_list[j] == 1:
                one_eye_group.append(j)
        if len(single_combat) == 2 and (not one_eye_group or len(one_eye_group) == 2):
            temp_clusters = []
            for j in single_combat:
                temp_clusters.append(undefined_clusters[j])
            air_num_list = find_all_air_number(board, temp_clusters)
            if air_num_list[0] == air_num_list[1] :
                double_alive_clusters.append(temp_clusters)
            else:
                if len(one_eye_group) == 1:
                    max_pos = one_eye_group[0]
                elif not one_eye_group:
                    temp_clusters = []
                    for j in single_combat:
                        temp_clusters.append(undefined_clusters[j])
                    air_num_list = find_all_air_number(board,temp_clusters)
                    max_index = np.argmax(air_num_list)
                    max_pos = single_combat[max_index]
                else:
                    temp_clusters = []
                    for j in one_eye_group:
                        temp_clusters.append(undefined_clusters[j])
                    air_num_list = find_all_air_number(board, temp_clusters)
                    max_index = np.argmax(air_num_list)
                    max_pos = one_eye_group[max_index]
                    max_cluster = undefined_clusters[max_pos]
                clusters = []
                for j in single_combat:
                    clusters.append(undefined_clusters[j])
                alive_clusters, dead_clusters = classifier(max_cluster,alive_clusters,dead_clusters,clusters)
        else:
            if len(one_eye_group) == 1:
                max_pos = one_eye_group[0]
            elif not one_eye_group:
                temp_clusters = []
                for j in single_combat:
                    temp_clusters.append(undefined_clusters[j])
                air_num_list = find_all_air_number(board,temp_clusters)
                max_index = np.argmax(air_num_list)
                max_pos = single_combat[max_index]
            else:
                temp_clusters = []
                for j in one_eye_group:
                    temp_clusters.append(undefined_clusters[j])
                air_num_list = find_all_air_number(board, temp_clusters)
                max_index = np.argmax(air_num_list)
                max_pos = one_eye_group[max_index]
            max_cluster = undefined_clusters[max_pos]
            clusters = []
            for j in single_combat:
                clusters.append(undefined_clusters[j])
            alive_clusters, dead_clusters = classifier(max_cluster, alive_clusters, dead_clusters, clusters)
    return alive_clusters,double_alive_clusters, dead_clusters

def ownership(airclusters,clusters,board):
    eye_type_index = np.zeros(len(airclusters))
    relation_mat = np.zeros([len(airclusters),len(clusters)])
    num_eye_list = np.zeros(len(clusters))
    black_eye_list = []
    white_eye_list = []
    undefined_list = []
    combat_mat = np.zeros([len(clusters), len(clusters)])
    air_link_list = []
    for i in range(len(airclusters)):
        air_type,link=check_color_around(airclusters[i],board,clusters)

        for j in link:
            relation_mat[i,j] = 1
        air_type, link = check_color_around(
            airclusters[i],
            board,
            clusters
        )
        link = list(set(link))
        air_link_list.append(link)

        if air_type == 1:
            black_eye_list.append(airclusters[i])
        elif air_type == -1:
            white_eye_list.append(airclusters[i])
        else:
            undefined_list.append(airclusters[i])
        eye_type_index[i] = air_type
    for link in air_link_list:

        for a in link:
            for b in link:

                if a != b:
                    combat_mat[a, b] = 1
    alive_clusters = []
    alive_index = []
    undefined_index = []
    undefined_cluster_list = []
    undefined_cluster_eye_list = []
    dead_clusters = []
    dead_index = []
    for i in range(len(clusters)):
        x,y,color = clusters[i][0]
        if color == 1:
            num_eyes = check_alive(clusters[i],black_eye_list,board)
        else:
            num_eyes = check_alive(clusters[i],white_eye_list,board)
        num_eye_list[i] = num_eyes
        if num_eyes > 1:
            alive_clusters.append(clusters[i])
            alive_index.append(i)
        else:
            undefined_cluster_list.append(clusters[i])
            undefined_index.append(i)
            undefined_cluster_eye_list.append(num_eyes)
    cluster_relation = np.dot(relation_mat.T, relation_mat)
    old_combat_mat = combat_mat.copy()
    alive_clusters, undefined_cluster_list, dead_clusters, alive_index, undefined_index,relation_mat, dead_index = update_alive_info(alive_clusters,undefined_cluster_list,dead_clusters,alive_index,undefined_index,relation_mat,dead_index,0)
    undefined_num_eye_list = []
    for i in undefined_index:
        undefined_num_eye_list.append(num_eye_list[i])
    print(undefined_index)
    undefined_mat = old_combat_mat[
        np.ix_(undefined_index, undefined_index)
    ]
    alive_clusters, double_alive_clusters, new_dead_clusters =cal_combat(alive_clusters, undefined_cluster_list, undefined_num_eye_list,board,undefined_mat,undefined_index)
    new_dead_clusters1 = new_dead_clusters.copy()
    dead_clusters.extend(new_dead_clusters1)
    for i in new_dead_clusters:
        for j in i:
            j[-1] = -j[-1]

    clusters_with_right_color = alive_clusters.copy()
    clusters_with_right_color.extend(new_dead_clusters)
    for group in double_alive_clusters:
        for cluster in group:
            clusters_with_right_color.append(cluster)
    black_eye_list = []
    white_eye_list = []
    undefined_list = []
    eye_type_index = np.zeros(len(airclusters))
    for i in range(len(airclusters)):

        air_type, link = check_color_around(
            airclusters[i],
            board,
            clusters_with_right_color
        )

        eye_type_index[i] = air_type

        if air_type == 1:
            black_eye_list.append(airclusters[i])

        elif air_type == -1:
            white_eye_list.append(airclusters[i])

        else:
            undefined_list.append(airclusters[i])

    return {

        "clusters": clusters_with_right_color,

        "airtype": eye_type_index.tolist(),

        "black_eye": black_eye_list,

        "white_eye": white_eye_list,

        "undefined": undefined_list,

        "dead": dead_clusters
    }


def cal_score(clusters_with_right_color, black_eye_list, white_eye_list, undefined_list):
    black_score = 0
    white_score = 0
    for i in clusters_with_right_color:
        for j in i:
            if j[-1] == 1:
                black_score+= 1
            else:
                white_score += 1
    for i in black_eye_list:
        for j in i:
            black_score += 1
    for i in white_eye_list:
        for j in i:
            white_score += 1
    for i in undefined_list:
        for j in i:
            white_score += 0.5
            black_score += 0.5
    return black_score,white_score
class judgeresult:
    def __init__(self, filename):

        self.filename = filename
        self.board = None
        self.komi = None
        self.handicap = None
        self.result = None
        self.airclusters = None
        self.clusters = None
        self.airtype = None
        self.black_score = 0
        self.white_score = 0
    def getinfo(self,board,komi,handicap):
        self.board = board
        self.komi = komi
        self.handicap = handicap

    def initialization(self):
        board,result,komi,handicap = load_info(self.filename)
        self.getinfo(board,komi,handicap)
        self.komi = float(self.komi)

    def cal_result(self):
        self.initialization()

        self.airclusters = create_airclusters(self.board)

        self.clusters = create_clusters(self.board)

        result = ownership(
            self.airclusters,
            self.clusters,
            self.board
        )

        self.airtype = result

        # 计算目数
        self.black_score, self.white_score = cal_score(
            result["clusters"],
            result["black_eye"],
            result["white_eye"],
            result["undefined"]
        )

        # 加贴目
        self.white_score += self.komi

        return result


if __name__ == "__main__":
    filename = "/Users/jiangyuncong/Downloads/games/AlphaGo/selfplay/1c.sgf"
    game = judgeresult(filename)
    game.cal_result()