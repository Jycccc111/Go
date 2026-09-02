import torch
from torch import nn
import numpy as np
import torch.nn.functional as F

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



    def forward(self, x):
        return self.network(x)


device = torch.device(
    "mps"
    if torch.backends.mps.is_available()
    else "cpu"
)


model = Policy_network().to(device)

model.load_state_dict(
    torch.load(
        "policy_network.pth",
        map_location=device
    )
)
model.eval()



