import io
import gc
import requests

import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
import numpy as np

from huggingface_hub import hf_hub_url


# ==========================================
# Device
# ==========================================

device = torch.device(
    "cuda" if torch.cuda.is_available()
    else "mps" if torch.backends.mps.is_available()
    else "cpu"
)

print("Using:", device)


# ==========================================
# Dataset
# ==========================================

class GoDataset(Dataset):

    def __init__(self, states, actions):

        self.states = torch.tensor(
            states,
            dtype=torch.float32
        )

        self.actions = torch.tensor(
            actions,
            dtype=torch.long
        )

    def __len__(self):
        return len(self.states)

    def __getitem__(self, index):

        return (
            self.states[index],
            self.actions[index]
        )


# ==========================================
# Policy Network
# ==========================================

class Policy_network(nn.Module):

    def __init__(self):

        super().__init__()

        self.network = nn.Sequential(

            nn.Conv2d(
                in_channels=3,
                out_channels=64,
                kernel_size=3,
                padding=1
            ),

            nn.ReLU(),

            nn.Conv2d(
                in_channels=64,
                out_channels=64,
                kernel_size=3,
                padding=1
            ),

            nn.ReLU(),

            nn.Conv2d(
                in_channels=64,
                out_channels=64,
                kernel_size=3,
                padding=1
            ),

            nn.ReLU(),

            nn.Flatten(),

            nn.Linear(
                64 * 19 * 19,
                361
            )
        ]

    def forward(self, x):

        return self.network(x)


    # ======================================
    # Training
    # ======================================

    def fit(
        self,
        epochs,
        files,
        repo_id
    ):

        criterion = nn.CrossEntropyLoss()

        optimizer = torch.optim.Adam(
            self.parameters(),
            lr=0.0001
        )

        for epoch in range(epochs):

            total_loss = 0
            total_batches = 0

            print()
            print(
                f"========== Epoch {epoch + 1} =========="
            )

            for i, filename in enumerate(files):

                print(
                    f"[{i + 1}/{len(files)}] "
                    f"正在读取: {filename}"
                )

                # ==================================
                # 从 Hugging Face 获取文件
                # ==================================

                url = hf_hub_url(
                    repo_id=repo_id,
                    filename=filename,
                    repo_type="dataset"
                )

                response = requests.get(url)

                response.raise_for_status()

                # ==================================
                # 直接从内存读取 npz
                # 不保存到本地
                # ==================================

                data = np.load(
                    io.BytesIO(response.content)
                )

                states = data["states"]
                actions = data["moves"]

                # ==================================
                # 创建 Dataset
                # ==================================

                dataset = GoDataset(
                    states,
                    actions
                )

                loader = DataLoader(
                    dataset,
                    batch_size=64,
                    shuffle=True
                )

                # ==================================
                # Training
                # ==================================

                self.train()

                for states_batch, actions_batch in loader:

                    states_batch = states_batch.to(device)
                    actions_batch = actions_batch.to(device)

                    output = self(states_batch)

                    loss = criterion(
                        output,
                        actions_batch
                    )

                    optimizer.zero_grad()

                    loss.backward()

                    optimizer.step()

                    total_loss += loss.item()
                    total_batches += 1

                print(
                    f"Chunk loss: {loss.item():.4f}"
                )

                # ==================================
                # 释放当前 chunk
                # ==================================

                del response
                del data
                del states
                del actions
                del dataset
                del loader

                gc.collect()

                if torch.cuda.is_available():
                    torch.cuda.empty_cache()

            average_loss = (
                total_loss / total_batches
            )

            print(
                f"\nEpoch {epoch + 1} "
                f"average loss = "
                f"{average_loss:.4f}"
            )

        # ======================================
        # 保存模型
        # ======================================

        torch.save(
            self.state_dict(),
            "policy_network.pth"
        )

        print(
            "\n模型已经保存为 "
            "policy_network.pth"
        )
