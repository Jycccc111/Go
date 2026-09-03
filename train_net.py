import io
import gc
import requests
from huggingface_hub import HfApi
import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
import numpy as np

from huggingface_hub import hf_hub_url

import torch.nn.functional as F
import random

# =========================
# Residual Block
# =========================

class ResBlock(nn.Module):

    def __init__(self, channels):
        super().__init__()

        self.conv1 = nn.Conv2d(
            channels,
            channels,
            kernel_size=3,
            padding=1
        )

        self.bn1 = nn.BatchNorm2d(channels)

        self.conv2 = nn.Conv2d(
            channels,
            channels,
            kernel_size=3,
            padding=1
        )

        self.bn2 = nn.BatchNorm2d(channels)

    def forward(self, x):

        identity = x

        x = self.conv1(x)
        x = self.bn1(x)
        x = F.relu(x)

        x = self.conv2(x)
        x = self.bn2(x)

        # Residual connection
        x = x + identity

        x = F.relu(x)

        return x
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
                in_channels=7,
                out_channels=64,
                kernel_size=3,
                padding=1
            ),

            nn.BatchNorm2d(64),
            nn.ReLU(),

            # ResNet
            ResBlock(64),
            ResBlock(64),
            ResBlock(64),
            ResBlock(64),
            ResBlock(64),
            ResBlock(64),

            # Policy head
            nn.Flatten(),

            nn.Linear(
                64 * 19 * 19,
                361
            )
        )
        self.optimizer = torch.optim.Adam(
            self.parameters(),
            lr=0.001
        )
    def load(self, filename):
        checkpoint = torch.load(
            filename,
            map_location=device
        )

        self.network.load_state_dict(
            checkpoint["model_state_dict"]
        )

        self.optimizer.load_state_dict(
            checkpoint["optimizer_state_dict"]
        )

        return checkpoint["epoch"]
    def forward(self, x):

        return self.network(x)


    # ======================================
    # Training
    # ======================================

    def fit(
            self,
            epochs,
            files,
            data_repo_id,
            model_repo_id
    ):
        api = HfApi()
        criterion = nn.CrossEntropyLoss()

        for epoch in range(epochs):

            total_loss = 0
            total_batches = 0

            print()
            print(
                f"========== Epoch {epoch + 1} =========="
            )
            epoch_files = files.copy()
            random.shuffle(epoch_files)
            for i, filename in enumerate(epoch_files):

                print(
                    f"[{i + 1}/{len(files)}] "
                    f"正在读取: {filename}"
                )

                # ==================================
                # 从 Hugging Face 获取文件
                # ==================================

                data = np.load(filename)

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
                    batch_size=2048,
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

                    self.optimizer.zero_grad()

                    loss.backward()

                    self.optimizer.step()

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
            checkpoint = {
                "epoch": epoch + 1,
                "model_state_dict": self.network.state_dict(),
                "optimizer_state_dict": self.optimizer.state_dict(),
                "loss": average_loss
            }

            filename = f"checkpoint_epoch_{epoch + 1}.pth"

            torch.save(checkpoint, filename)
            api.upload_file(
                path_or_fileobj=filename,
                path_in_repo=filename,
                repo_id=model_repo_id,
                repo_type="model"
            )
            print("已上传到 Hugging Face")

        # ======================================
        # 保存模型
        # ======================================

        torch.save(
            self.state_dict(),
            "policy_network.pth"
        )
        api.upload_file(
            path_or_fileobj="policy_network.pth",
            path_in_repo="policy_network.pth",
            repo_id=model_repo_id,
            repo_type="model"
        )
        print(
            "\n模型已经保存为 "
            "policy_network.pth"
        )
