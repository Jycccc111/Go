import torch
from torch import nn
import numpy as np
import torch.nn.functional as F
from huggingface_hub import hf_hub_download
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
class Policy_network(nn.Module):

    def __init__(self):

        super().__init__()

        self.network = nn.Sequential(

            nn.Conv2d(
                in_channels=23,
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
    def forward(self, x):
        return self.network(x)


device = torch.device(
    "cuda" if torch.cuda.is_available()
    else "mps" if torch.backends.mps.is_available()
    else "cpu"
)

model = Policy_network().to(device)

# 从 Hugging Face Model Hub 读取
model_path = hf_hub_download(
    repo_id="Jycccc111/Go-Policy",
    filename="Test_best_policy_network.pth"
)

print("Loading:", model_path)

checkpoint = torch.load(
    model_path,
    map_location=device
)

# 兼容两种保存方式
if "model_state_dict" in checkpoint:
    model.network.load_state_dict(checkpoint["model_state_dict"])
else:
    model.load_state_dict(checkpoint)

model.eval()

print("Policy Network loaded successfully!")



