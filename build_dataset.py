import os
import gc
import numpy as np

from huggingface_hub import (
    HfApi,
    hf_hub_download,
    list_repo_files
)

from data_loader import SGFLoader


# ==========================================
# Configuration
# ==========================================

DATA_REPO_ID = "Jycccc111/Go"

OUTPUT_REPO_ID = "Jycccc111/Go"

CHUNK_SIZE = 100_000

SAVE_DIR = "dataset"

os.makedirs(SAVE_DIR, exist_ok=True)


# ==========================================
# Get SGF files
# ==========================================

files = list_repo_files(
    repo_id=DATA_REPO_ID,
    repo_type="dataset"
)

sgf_files = [
    filename
    for filename in files
    if filename.lower().endswith(".sgf")
]

print("SGF数量:", len(sgf_files))


# ==========================================
# Hugging Face API
# ==========================================

api = HfApi()


# ==========================================
# Buffer
# ==========================================

all_states = []
all_moves = []
all_results = []

chunk_id = 0
total_positions = 0


# ==========================================
# Process
# ==========================================

for i, filename in enumerate(sgf_files):

    print()
    print(
        f"[{i + 1}/{len(sgf_files)}]"
        f" 正在读取: {filename}"
    )

    # ======================================
    # Download SGF
    # ======================================

    try:

        local_file = hf_hub_download(
            repo_id=DATA_REPO_ID,
            filename=filename,
            repo_type="dataset"
        )

    except Exception as e:

        print("下载失败:", e)
        continue


    # ======================================
    # Load SGF
    # ======================================

    try:

        loader = SGFLoader(local_file)

        loader.load()

    except Exception as e:

        print("跳过:", filename)
        print("错误:", e)
        continue


    # ======================================
    # Add to buffer
    # ======================================

    all_states.extend(loader.states)
    all_moves.extend(loader.actions)
    all_results.extend(loader.results)


    print(
        "当前 buffer:",
        len(all_states)
    )


    # ======================================
    # Release loader
    # ======================================

    del loader


    # ======================================
    # Create chunk
    # ======================================

    if len(all_states) >= CHUNK_SIZE:

        states = np.asarray(
            all_states,
            dtype=np.float32
        )

        moves = np.asarray(
            all_moves,
            dtype=np.int64
        )

        results = np.asarray(
            all_results,
            dtype=np.int8
        )


        assert len(states) == len(moves)
        assert len(states) == len(results)


        chunk_filename = (
            f"chunk_{chunk_id:05d}.npz"
        )

        local_chunk = os.path.join(
            SAVE_DIR,
            chunk_filename
        )


        # ==================================
        # Save
        # ==================================

        np.savez(
            local_chunk,
            states=states,
            moves=moves,
            results=results
        )


        print(
            "保存:",
            chunk_filename
        )

        print(
            "positions:",
            len(states)
        )


        # ==================================
        # Upload
        # ==================================

        api.upload_file(
            path_or_fileobj=local_chunk,
            path_in_repo=f"processed/{chunk_filename}",
            repo_id=OUTPUT_REPO_ID,
            repo_type="dataset"
        )


        print(
            "已上传:",
            chunk_filename
        )


        # ==================================
        # Statistics
        # ==================================

        total_positions += len(states)

        chunk_id += 1


        # ==================================
        # Clear memory
        # ==================================

        all_states.clear()
        all_moves.clear()
        all_results.clear()


        del states
        del moves
        del results


        # ==================================
        # Delete local file
        # ==================================

        os.remove(local_chunk)


        # ==================================
        # Garbage collection
        # ==================================

        gc.collect()


print()
print("==============================")
print("处理完成")
print(
    "总 positions:",
    total_positions
)
print("==============================")