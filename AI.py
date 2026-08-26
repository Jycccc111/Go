import numpy as np
import torch
from Policy_model import model,device
import copy
from board import GoGame
def encode_board(board):

    state = np.zeros(
        (3, 19, 19),
        dtype=np.float32
    )

    for i in range(19):
        for j in range(19):

            if board[i + 1, j + 1] == 1:
                state[0, i, j] = 1

            elif board[i + 1, j + 1] == -1:
                state[1, i, j] = 1

    return state

def predict_move(game):
    board = game.board
    state = encode_board(board)
    state = torch.tensor(
        state,
        dtype = torch.float32
    )
    state = state.unsqueeze(0)

    state = state.to(device)

    with torch.no_grad():
        output = model(state)

    candidates = []

    for x in range(19):
        for y in range(19):

            # 空位置才考虑
            if board[x + 1][y + 1] == 0:
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

