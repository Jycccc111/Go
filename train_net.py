import torch
from torch import nn
from torch.utils.data import Dataset,DataLoader
import numpy as np
import glob
#print(torch.backends.mps.is_available())
#device = torch.device(
    #"mps" if torch.backends.mps.is_available() else "cpu"
#)
#print("Using:", device)

device = torch.device(
    "cuda" if torch.cuda.is_available()
    else "mps" if torch.backends.mps.is_available()
    else "cpu"
)
print("Using:", device)
files = sorted(
    glob.glob("dataset/chunk_*.npz")
)

print("找到", len(files), "个数据文件")

class GoDataset(Dataset):
    def __init__(self,states,actions):
        self.state = torch.tensor(
            states,
            dtype=torch.float32
        )

        self.actions = torch.tensor(
            actions,
            dtype=torch.long
        )

    def __len__(self):
        return len(self.state)
    def __getitem__(self, index):
        return self.state[index],self.actions[index]



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
    def fit(self,epochs,files):
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(
            model.parameters(),
            lr=0.0001
        )
        for epoch in range(epochs):
            total_loss = 0
            for filename in files:
                print("正在读取:", filename)

                data = np.load(filename)

                states = data["states"]
                actions = data["moves"]

                dataset = GoDataset(
                    states,
                    actions
                )

                loader = DataLoader(
                    dataset,
                    batch_size=64,
                    shuffle=True
                )

                for batch_idx, (states_batch, actions_batch) in enumerate(loader):
                    states_batch = states_batch.to(device)
                    actions_batch = actions_batch.to(device)

                    output = model(states_batch)

                    loss = criterion(
                        output,
                        actions_batch
                    )

                    optimizer.zero_grad()

                    loss.backward()

                    optimizer.step()

                    total_loss = loss.item()
                print(
                    f"Epoch {epoch + 1}, "
                    f"Loss: {total_loss / len(loader):.4f}"
                )

        torch.save(
            model.state_dict(),
            "policy_network.pth"
        )


model = Policy_network().to(device)
model.load_state_dict(
    torch.load(
        "policy_network.pth",
        map_location=device
    )
)
# 切换到推理模式
model.eval()
print("模型加载成功")
