import os
import numpy as np

from data_loader import SGFLoader


def find_sgf_files(root):

    files = []

    for path, dirs, filenames in os.walk(root):

        for filename in filenames:

            if filename.endswith(".sgf"):

                files.append(
                    os.path.join(path, filename)
                )

    return files


# =========================
# 配置
# =========================

ROOT = "/Users/jiangyuncong/Downloads/games"

SAVE_DIR = "dataset"

CHUNK_SIZE = 100_000


# =========================
# 创建保存目录
# =========================

os.makedirs(SAVE_DIR, exist_ok=True)


# =========================
# 找到所有 SGF
# =========================

files = find_sgf_files(ROOT)

print("SGF数量:", len(files))


# =========================
# 当前 chunk
# =========================

all_states = []
all_moves = []
all_results = []

chunk_id = 0
total_positions = 0


# =========================
# 开始读取
# =========================

for i, filename in enumerate(files):

    loader = SGFLoader(filename)

    try:
        loader.load()

    except Exception as e:

        print(
            "跳过文件:",
            filename,
            "错误:",
            e
        )

        continue


    all_states.extend(loader.states)

    all_moves.extend(loader.actions)

    all_results.extend(loader.results)


    # =========================
    # 达到 chunk 大小
    # =========================

    if len(all_states) >= CHUNK_SIZE:

        states = np.asarray(
            all_states,
            dtype=np.uint8
        )

        moves = np.asarray(
            all_moves,
            dtype=np.int16
        )

        results = np.asarray(
            all_results,
            dtype=np.int8
        )


        assert len(states) == len(moves)
        assert len(states) == len(results)


        np.savez(
            os.path.join(
                SAVE_DIR,
                f"chunk_{chunk_id:05d}.npz"
            ),
            states=states,
            moves=moves,
            results=results
        )


        total_positions += len(states)


        print(
            f"保存 chunk {chunk_id}:",
            len(states),
            "positions",
            "总计:",
            total_positions
        )


        chunk_id += 1


        # =========================
        # 清空 RAM
        # =========================

        all_states.clear()
        all_moves.clear()
        all_results.clear()


# =========================
# 保存最后不足一个 chunk 的数据
# =========================

if all_states:

    states = np.asarray(
        all_states,
        dtype=np.uint8
    )

    moves = np.asarray(
        all_moves,
        dtype=np.int16
    )

    results = np.asarray(
        all_results,
        dtype=np.int8
    )


    assert len(states) == len(moves)
    assert len(states) == len(results)


    np.savez(
        os.path.join(
            SAVE_DIR,
            f"chunk_{chunk_id:05d}.npz"
        ),
        states=states,
        moves=moves,
        results=results
    )


    total_positions += len(states)


print()
print("完成")
print("总 positions:", total_positions)
print("保存目录:", SAVE_DIR)