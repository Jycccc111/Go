
from sgfmill import sgf
import numpy as np
from board import GoGame
from sgfmill import sgf_properties
class SGFLoader:

    def __init__(self, filename):

        self.filename = filename

        self.game = None
        self.size = 19
        self.result = None
        self.moves = []
        self.komi = None
        self.handicap = None
        self.lasteated1 = []
        self.lasteated2 = []
        self.states = []
        self.actions = []
        self.results = []

    def encode_board(self,color,last_move,last1,last2):
        size = self.size

        x = np.zeros(
            (7, size, size),
            dtype=np.uint8
        )

        for i in range(size):
            for j in range(size):

                stone = self.game.board[i + 1][j + 1]

                if stone == 1:
                    x[0, i, j] = 1

                elif stone == -1:
                    x[1, i, j] = 1
                #available,a,b = self.game.move(i + 1,j + 1,color,True)
                #if available:
                    #x[7, i, j] = 1
        if color == 1:
            x[2, :, :] = 1
        else:
            x[3, :, :] = 1
        i,j = last_move
        if not(i == 20 and j == 20):
            x[4, i, j] = 1
        for i,j in last1:
            x[5, i-1, j-1] = 1
        for i,j in last2:
            x[6, i-1, j-1] = 1
        return x
    def show_board(self, board):

        size = self.size

        letters = "ABCDEFGHJKLMNOPQRST"

        print("   " + " ".join(letters[:size]))

        star_points = {
            (4, 4), (4, 10), (4, 16),
            (10, 4), (10, 10), (10, 16),
            (16, 4), (16, 10), (16, 16)
        }

        for y in range(size):

            print(f"{y + 1:2d}", end=" ")

            for x in range(size):

                v = board[x + 1][y + 1]

                if v == 1:
                    c = "●"

                elif v == -1:
                    c = "○"

                elif (x + 1, y + 1) in star_points:
                    c = "☆"

                else:
                    c = "·"

                print(c, end=" ")

            print()
    def get_property(self, node, key):

        if key in node.properties():
            return node.get_raw(key)

        return None

    def to_numpy(self):

        self.size = self.game.board.shape[0] - 2

        board = np.copy(self.game.board)

        return board

    def load(self):

        with open(self.filename, "rb") as f:
            sgf_game = sgf.Sgf_game.from_bytes(f.read())

        root = sgf_game.get_root()
        if "SZ" in root.properties():

            size = root.get_raw("SZ")

            self.size = int(size)

        else:

            self.size = 19

        if self.size is not None:
            self.size = int(self.size)
        else:
            self.size = 19
        if self.size != 19:
            print(
                "跳过非19路:",
                self.filename,
                self.size
            )
            return self
        self.game = GoGame()
        if "RE" in root.properties():

            self.result = root.get_raw("RE").decode()

        else:

            self.result = None
        self.komi = (
            root.get_raw("KM")
            if "KM" in root.properties()
            else None
        )

        self.handicap = (
            root.get_raw("HA")
            if "HA" in root.properties()
            else None
        )
        last_move = 20, 20
        for node in sgf_game.get_main_sequence():
            if "AB" in node.properties():

                for x, y in node.get("AB"):
                    self.game.add_stone(
                        x + 1,
                        y + 1,
                        1
                    )

                # 2. 正常棋步
            color = None
            move = None

            if "B" in node.properties():

                color = "b"

                raw = node.get_raw("B")


            elif "W" in node.properties():

                color = "w"

                raw = node.get_raw("W")


            else:

                continue

            # pass
            if raw == b"":
                continue

            try:

                move = sgf_properties.interpret_go_point(
                    raw,
                    self.size
                )

            except ValueError:

                print(
                    "跳过非法棋步:",
                    raw,
                    self.filename
                )

                continue

            if move is None:
                continue

            x, y = move

            stone = 1 if color == "b" else -1
            state = self.encode_board(stone,last_move,self.lasteated1,self.lasteated2)
            last_move = [move[0],move[1]]
            self.states.append(state)

            action = y * self.size + x

            self.actions.append(action)

            ok,self.lasteated1,self.lasteated2=self.game.move(
                x + 1,
                y + 1,
                stone
            )

            if not ok:
                print(
                    "非法棋步:",
                    color,
                    x,
                    y
                )
                break

            self.moves.append(
                (color, (x, y))
            )


        z = self.parse_result()

        self.results = [
            z for _ in self.states
        ]

        return self

    def coord(self, point):

        if point is None:
            return None

        # sgfmill已经转换好了
        # 例如 (3,3)
        if isinstance(point, tuple):
            return point

        # 兼容原始SGF字符串
        # 例如 "dd"
        if isinstance(point, str):
            x = ord(point[0]) - ord('a')
            y = ord(point[1]) - ord('a')
            return x, y

        raise TypeError(
            f"未知坐标格式: {point}, 类型={type(point)}"
        )

    def print_board(self):

        symbols = {
            0: "0",
            1: "1",
            2: "-1"
        }


        for row in self.board:
            print(
                " ".join(
                    symbols[x]
                    for x in row
                )
            )

    def parse_result(self):

        if self.result is None:
            return 0

        if self.result.startswith("B"):
            return 1

        if self.result.startswith("W"):
            return -1

        return 0


# 测试

if __name__ == "__main__":

    sgf_file = "/Users/jiangyuncong/Downloads/games/AlphaGo/FanHui/1.sgf"


    loader = SGFLoader(sgf_file)

    loader.load()
    board = loader.to_numpy()
    loader.load()

    print(
        np.array(loader.states).shape
    )

    print(
        np.array(loader.actions).shape
    )

    print(
        np.array(loader.results).shape
    )
    print(board)

    print("棋盘大小:", loader.size)
    print("结果:", loader.result)
    print("贴目:", loader.komi)
    print("让子:", loader.handicap)

    print("棋步数:", len(loader.moves))
