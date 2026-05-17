import cv2
import numpy as np
import torch
import torch.nn.functional as F
import torchvision.transforms as transforms
from PIL import Image

from siamese_cnn_training.model import SiameseNetwork


# preprocessing
# def clean_signature(img):
#     _, thresh = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY_INV)
#     kernel = np.ones((2,2), np.uint8)
#     cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
#     return cleaned
def clean_signature(img):
    if img is None:
        raise ValueError("Image is empty!")

    _, thresh = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY_INV)
    kernel = np.ones((2,2), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    return cleaned

# transform
transform = transforms.Compose([
    transforms.Resize((105, 105)),
    transforms.ToTensor()
])

def to_tensor(img):
    pil = Image.fromarray(img)
    return transform(pil).unsqueeze(0)


# load model
def load_model():
    model = SiameseNetwork()
    model.load_state_dict(torch.load("siamese_cnn_training/siamese_model.pth", map_location="cpu"))
    model.eval()
    return model


# compare
def compare(model, img1, img2):
    sig1 = clean_signature(img1)
    sig2 = clean_signature(img2)

    t1 = to_tensor(sig1)
    t2 = to_tensor(sig2)

    with torch.no_grad():
        out1, out2 = model(t1, t2)
        dist = F.pairwise_distance(out1, out2)

    return dist.item()