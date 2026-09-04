import numpy as np
import torch
from Policy_model import model,device
import copy
from board import GoGame


def encode_board(game, color, last_move, last1, last2):
    len_layer = 8
    size = game.size

    x = np.zeros(
        (23, size, size),
        dtype=np.int8
    )

    for i in range(size):
        for j in range(size):

            stone = game.board[i + 1][j + 1]

            if stone == 1:
                x[0, i, j] = 1

            elif stone == -1:
                x[1, i, j] = 1
            # available,count = self.game.trymove(i + 1,j + 1,color)
            # for a in range(len_layer):
            # x[8 + a , i , j ] = count
            # if available:
            # x[7, i, j] = 1
    if color == 1:
        x[2, :, :] = 1
    else:
        x[3, :, :] = 1
    i, j = last_move
    if not (i >= 20 and j >= 20):
        x[4, i, j] = 1
    for i, j in last1:
        x[5, i - 1, j - 1] = 1
    for i, j in last2:
        x[6, i - 1, j - 1] = 1
    temp = game.getinfo()
    for a in range(len_layer):
        x[7 + a, :, :] = temp
    for a in range(len_layer):
        x[15 + a, :, :] =game.history
    return x
def predict_move(game):
    state = encode_board(game,game.count,game.lastmove,game.lasteaten1,game.lasteaten2)
    state = torch.tensor(
        state,
        dtype = torch.float32
    )
    state = state.unsqueeze(0)

    state = state.to(device)

    with torch.no_grad():
        output = model(state)
    output = output.squeeze(0)
    candidates = []

    for x in range(19):
        for y in range(19):

            # 空位置才考虑
            if game.board[x + 1][y + 1] == 0:
                index = x * 19 + y

                candidates.append(
                    (output[index].item(), x, y)
                )

    # 按网络分数从高到低排序
    candidates.sort(
        reverse=True
    )

    # 从最高分开始找合法位置
    for score, x, y in candidates:
        board_x = x + 1
        board_y = y + 1

        # 已经有棋子
        if game.board[board_x, board_y] != 0:
            continue

        # 创建一个临时游戏
        test_game = copy.deepcopy(game)

        # 测试 AI 落子
        success = test_game.move(
            board_x,
            board_y
        )

        if success:
            return x, y

