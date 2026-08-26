import torch
from torch import nn
import numpy as np

class Policy_network(nn.Module):
    def __init__(self):
        super().__init__()

        self.network = nn.Sequential(
            nn.Conv2d(
                in_channels=3,
                out_channels=64,
                kernel_size=3,
                padding=1),
            nn.ReLU(),
            nn.Conv2d(
                in_channels=64,
                out_channels=64,
                kernel_size=3,
                padding=1),
            nn.ReLU(),
            nn.Conv2d(
                in_channels=64,
                out_channels=64,
                kernel_size=3,
                padding=1),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(
                64*19*19,361
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



