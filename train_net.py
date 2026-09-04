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
            ResBlock(64),
            ResBlock(64),
            nn.Conv2d(
                64,
                2,
                kernel_size=1
            ),
            nn.BatchNorm2d(2),
            nn.ReLU(),

            nn.Flatten(),

            nn.Linear(
                2 * 19 * 19,
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
            model_repo_id,
            val_ratio=0.2,
            batch_size=4096
    ):

        api = HfApi()

        criterion = nn.CrossEntropyLoss()

        # ==========================================
        # 划分 Train / Validation
        # ==========================================

        files = files.copy()
        random.shuffle(files)

        split = int(len(files) * (1 - val_ratio))

        train_files = files[:split]
        val_files = files[split:]

        print(
            f"Train chunks: {len(train_files)}"
        )

        print(
            f"Validation chunks: {len(val_files)}"
        )

        # ==========================================
        # Learning Rate Scheduler
        # ==========================================

        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer,
            mode="min",
            factor=0.5,
            patience=2,
            min_lr=1e-6
        )

        # ==========================================
        # Early Stopping
        # ==========================================

        best_val_loss = float("inf")

        patience = 5
        bad_epochs = 0

        # ==========================================
        # Epoch
        # ==========================================

        for epoch in range(epochs):

            print()
            print(
                f"========== Epoch {epoch + 1} =========="
            )

            # ======================================
            # TRAIN
            # ======================================

            self.train()

            random.shuffle(train_files)

            train_loss = 0
            train_samples = 0

            for i, filename in enumerate(train_files):

                print(
                    f"[Train {i + 1}/{len(train_files)}] "
                    f"正在读取: {filename}"
                )

                # -------------------------------
                # Load
                # -------------------------------

                data = np.load(filename)

                states = data["states"]
                actions = data["moves"]

                dataset = GoDataset(
                    states,
                    actions
                )

                loader = DataLoader(
                    dataset,
                    batch_size=batch_size,
                    shuffle=True
                )

                # -------------------------------
                # Training
                # -------------------------------

                for states_batch, actions_batch in loader:
                    states_batch = states_batch.to(device)
                    actions_batch = actions_batch.to(device)

                    self.optimizer.zero_grad()

                    output = self(states_batch)

                    loss = criterion(
                        output,
                        actions_batch
                    )

                    loss.backward()

                    self.optimizer.step()

                    batch_size_actual = states_batch.size(0)

                    train_loss += (
                            loss.item()
                            * batch_size_actual
                    )

                    train_samples += batch_size_actual

                print(
                    f"Chunk loss: {loss.item():.4f}"
                )

                # -------------------------------
                # Free memory
                # -------------------------------

                del data
                del states
                del actions
                del dataset
                del loader

                gc.collect()

                if torch.cuda.is_available():
                    torch.cuda.empty_cache()

            # ======================================
            # Average Train Loss
            # ======================================

            train_loss /= train_samples

            # ======================================
            # VALIDATION
            # ======================================

            self.eval()

            val_loss = 0
            val_samples = 0

            with torch.no_grad():

                for i, filename in enumerate(val_files):

                    print(
                        f"[Val {i + 1}/{len(val_files)}] "
                        f"正在读取: {filename}"
                    )

                    data = np.load(filename)

                    states = data["states"]
                    actions = data["moves"]

                    dataset = GoDataset(
                        states,
                        actions
                    )

                    loader = DataLoader(
                        dataset,
                        batch_size=batch_size,
                        shuffle=False
                    )

                    for states_batch, actions_batch in loader:
                        states_batch = states_batch.to(device)
                        actions_batch = actions_batch.to(device)

                        output = self(states_batch)

                        loss = criterion(
                            output,
                            actions_batch
                        )

                        batch_size_actual = states_batch.size(0)

                        val_loss += (
                                loss.item()
                                * batch_size_actual
                        )

                        val_samples += batch_size_actual

                    # -------------------------------
                    # Free memory
                    # -------------------------------

                    del data
                    del states
                    del actions
                    del dataset
                    del loader

                    gc.collect()

                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()

            # ======================================
            # Average Validation Loss
            # ======================================

            val_loss /= val_samples

            # ======================================
            # Learning Rate
            # ======================================

            scheduler.step(val_loss)

            current_lr = self.optimizer.param_groups[0]["lr"]

            print()
            print(
                f"Epoch {epoch + 1}"
            )

            print(
                f"Train Loss: {train_loss:.4f}"
            )

            print(
                f"Val Loss:   {val_loss:.4f}"
            )

            print(
                f"Learning Rate: {current_lr:.8f}"
            )

            # ======================================
            # Save Best Model + Last Model
            # ======================================

            # --------------------------------------
            # 判断是否是最佳模型
            # --------------------------------------

            is_best = val_loss < best_val_loss

            if is_best:

                best_val_loss = val_loss
                bad_epochs = 0

            else:

                bad_epochs += 1

                print(
                    f"Validation 没有改善 "
                    f"({bad_epochs}/{patience})"
                )

            # ======================================
            # 创建当前 Epoch checkpoint
            # ======================================

            checkpoint = {

                "epoch": epoch + 1,

                "model_state_dict":
                    self.network.state_dict(),

                "optimizer_state_dict":
                    self.optimizer.state_dict(),

                "best_val_loss":
                    best_val_loss,

                "train_loss":
                    train_loss,

                "val_loss":
                    val_loss,

                "learning_rate":
                    current_lr
            }

            # ======================================
            # 保存最新模型
            # 每个 Epoch 都保存
            # ======================================

            filename_last = "last_policy_network.pth"

            torch.save(
                checkpoint,
                filename_last
            )

            api.upload_file(
                path_or_fileobj=filename_last,
                path_in_repo=filename_last,
                repo_id=model_repo_id,
                repo_type="model"
            )

            print(
                "✓ 已保存最新模型"
            )

            # ======================================
            # 如果是最佳模型
            # ======================================

            if is_best:
                filename_best = "Test_best_policy_network.pth"

                torch.save(
                    checkpoint,
                    filename_best
                )

                api.upload_file(
                    path_or_fileobj=filename_best,
                    path_in_repo=filename_best,
                    repo_id=model_repo_id,
                    repo_type="model"
                )

                print(
                    "★ 保存新的最佳模型"
                )

            # ======================================
            # Early Stopping
            # ======================================

            if bad_epochs >= patience:
                print()
                print(
                    "Early stopping!"
                )

                break