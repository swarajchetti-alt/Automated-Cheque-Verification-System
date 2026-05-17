import cv2
import numpy as np

def preprocess(img):

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    denoised = cv2.fastNlMeansDenoising(gray, h=50)

    coords = np.column_stack(np.where(denoised > 0))
    angle = cv2.minAreaRect(coords)[-1]

    if angle < -45:
        angle = 90 + angle

    h, w = denoised.shape
    M = cv2.getRotationMatrix2D((w//2, h//2), angle, 1.0)

    deskewed = cv2.warpAffine(
        denoised, M, (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE
    )

    binary = cv2.adaptiveThreshold(
        deskewed, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )

    kernel = np.ones((2,2), np.uint8)
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

    return cleaned


def preprocess_date(img):

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    denoised = cv2.fastNlMeansDenoising(gray, h=10)

    coords = np.column_stack(np.where(denoised > 0))
    angle = cv2.minAreaRect(coords)[-1]

    if angle < -45:
        angle = 90 + angle

    h, w = denoised.shape
    M = cv2.getRotationMatrix2D((w//2, h//2), angle, 1.0)

    deskewed = cv2.warpAffine(
        denoised, M, (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE
    )

    binary = cv2.adaptiveThreshold(
        deskewed, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )

    kernel = np.ones((2,2), np.uint8)
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

    return cleaned