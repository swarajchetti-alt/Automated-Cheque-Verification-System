import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
import torch.optim as optim

from dataset import SignatureDataset
from model import SiameseNetwork

# Paths
genuine_dir = "signatures/full_org"
forged_dir = "signatures/full_forg"

# Dataset
dataset = SignatureDataset(genuine_dir, forged_dir)
loader = DataLoader(dataset, batch_size=16, shuffle=True)

# Device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Model
model = SiameseNetwork().to(device)

# Loss
def contrastive_loss(out1, out2, label, margin=2.0):
    dist = F.pairwise_distance(out1, out2)
    loss = torch.mean(
        label * dist**2 +
        (1 - label) * torch.clamp(margin - dist, min=0)**2
    )
    return loss

# Optimizer
optimizer = optim.Adam(model.parameters(), lr=1e-4)

# Training
epochs = 10

for epoch in range(epochs):
    total_loss = 0

    for img1, img2, label in loader:
        img1, img2, label = img1.to(device), img2.to(device), label.to(device)

        optimizer.zero_grad()

        out1, out2 = model(img1, img2)
        loss = contrastive_loss(out1, out2, label)

        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    print(f"Epoch {epoch+1}, Loss: {total_loss/len(loader):.4f}")

# Save model
torch.save(model.state_dict(), "siamese_model.pth")
print("Model saved!")