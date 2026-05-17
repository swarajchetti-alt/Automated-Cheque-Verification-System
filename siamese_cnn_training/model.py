import torch.nn as nn

class SiameseNetwork(nn.Module):
    def __init__(self):
        super().__init__()

        self.cnn = nn.Sequential(
            nn.Conv2d(1, 64, 10),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(64, 128, 7),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(128, 128, 4),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(128, 256, 4),
            nn.ReLU()
        )

        self.fc = nn.Sequential(
            nn.Linear(256*6*6, 1024),
            nn.ReLU(),
            nn.Linear(1024, 256)
        )

    def forward_once(self, x):
        x = self.cnn(x)
        x = x.view(x.size(0), -1)
        return self.fc(x)

    def forward(self, x1, x2):
        return self.forward_once(x1), self.forward_once(x2)