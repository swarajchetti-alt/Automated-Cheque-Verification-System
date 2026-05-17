import os
import random
from PIL import Image
import torch
from torch.utils.data import Dataset
import torchvision.transforms as transforms

transform = transforms.Compose([
    transforms.Resize((105, 105)),
    transforms.ToTensor(),
])

class SignatureDataset(Dataset):
    def __init__(self, genuine_dir, forged_dir):
        valid_ext = (".png", ".jpg", ".jpeg")

        self.genuine = [
        os.path.join(genuine_dir, f)
        for f in os.listdir(genuine_dir)
        if f.lower().endswith(valid_ext)
        ]

        self.forged = [
        os.path.join(forged_dir, f)
        for f in os.listdir(forged_dir)
        if f.lower().endswith(valid_ext)
        ]

    def __len__(self):
        return len(self.genuine)

    def __getitem__(self, idx):
        img1_path = self.genuine[idx]

        if random.random() > 0.5:
            img2_path = random.choice(self.genuine)
            label = 1
        else:
            img2_path = random.choice(self.forged)
            label = 0

        img1 = Image.open(img1_path).convert("L")
        img2 = Image.open(img2_path).convert("L")

        img1 = transform(img1)
        img2 = transform(img2)

        return img1, img2, torch.tensor(label, dtype=torch.float32)