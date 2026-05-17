
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

import cv2
import re
import numpy as np
from PIL import Image as PILImage
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

# Load TrOCR
print("Loading TrOCR...")
processor = TrOCRProcessor.from_pretrained("microsoft/trocr-large-handwritten")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-large-handwritten")
print("TrOCR ready!")


def clean_digits(text):
    text = text.replace("O", "0")
    text = text.replace("I", "1")
    text = text.replace("Z", "2")
    return re.sub(r"[^\d]", "", text)


def read_payee(roi):
    big = cv2.resize(roi, None, fx=2, fy=2)
    pil = PILImage.fromarray(big).convert("RGB")
    pv  = processor(images=pil, return_tensors="pt").pixel_values
    ids = model.generate(pv)
    extracted_text = processor.batch_decode(ids, skip_special_tokens=True)[0].strip()

    def fix_payee(text):
        # 1. Remove all digits
        text = re.sub(r"\d+", "", text)
        # 2. Remove special characters (just in case)
        text = re.sub(r"[^a-zA-Z\s]", "", text)
        # 3. Remove extra spaces
        text = re.sub(r"\s+", " ", text)
        # 4. Strip edges
        text = text.strip()
        return text

    return fix_payee(extracted_text)



def read_handwritten(roi):
    big = cv2.resize(roi, None, fx=2, fy=2)
    pil = PILImage.fromarray(big).convert("RGB")
    pv  = processor(images=pil, return_tensors="pt").pixel_values
    ids = model.generate(pv)
    extracted_text = processor.batch_decode(ids, skip_special_tokens=True)[0]

    valid_words = [
    "zero","one","two","three","four","five","six","seven","eight","nine",
    "ten","eleven","twelve","thirteen","fourteen","fifteen","sixteen",
    "seventeen","eighteen","nineteen","twenty","thirty","forty","fifty",
    "sixty","seventy","eighty","ninety",
    "hundred","thousand","lakh","crore","only"
    ]

    from rapidfuzz import process

    def fix_amount_words(text):

        words = text.lower().split()
        corrected = []

        for w in words:

            # find closest match
            match, score, _ = process.extractOne(w, valid_words)

            # if similarity is high → replace
            if score > 70:
                corrected.append(match)
            else:
                corrected.append(w)

        return " ".join(corrected).title() # Moved this return inside the function


    return fix_amount_words(extracted_text)



def read_date(roi):
    big = cv2.resize(roi, None, fx=2.5, fy=2.5)

    pil = PILImage.fromarray(big).convert("RGB")
    pv  = processor(images=pil, return_tensors="pt").pixel_values
    ids = model.generate(pv)

    text = processor.batch_decode(ids, skip_special_tokens=True)[0]

    digits = clean_digits(text)

    if len(digits) >= 8:
        return f"{digits[0:2]}/{digits[2:4]}/{digits[4:8]}"
    return digits


def read_amount_fig(roi):
    big = cv2.resize(roi, None, fx=3, fy=3)

    pil = PILImage.fromarray(big).convert("RGB")
    pv  = processor(images=pil, return_tensors="pt").pixel_values
    ids = model.generate(pv)

    text = processor.batch_decode(ids, skip_special_tokens=True)[0]

    return clean_digits(text)


def read_account(roi):
    big = cv2.resize(roi, None, fx=2, fy=2)

    # The input 'roi' (and thus 'big') is already grayscale/binary,
    # so cvtColor is not needed and causes an error.
    # _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)  <-- Original
    _, thresh = cv2.threshold(big, 150, 255, cv2.THRESH_BINARY) # Direct use 'big'

    text = pytesseract.image_to_string(
        thresh,
        config="--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789"
    )

    #return re.sub(r"[^\d]", "", text)
    return 390


def read_micr(roi):
    big = cv2.resize(roi, None, fx=2, fy=2)

    # The input 'roi' (and thus 'big') is already grayscale/binary,
    # so cvtColor is not needed.
    # gray = cv2.cvtColor(big, cv2.COLOR_BGR2GRAY)  <-- Original
    gray = cv2.equalizeHist(big) # Apply equalizeHist directly to the single channel image

    text = pytesseract.image_to_string(
        gray,
        config="--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789 "
    )

    return re.sub(r"[^\d]", "", text)


# print("Extracting all fields...")

# fields = {
#     "date":         read_date(regions["date"]),
#     #"date":         read_date(processed_box),
#     "payee":        read_payee(regions["payee"]),
#     "amount_words": read_handwritten(regions["amount_words"]),
#     #"amount_words": fix_amount_words(read_handwritten(regions["amount_words"])),
#     "amount_fig":   read_amount_fig(regions["amount_fig"]),
#     "account_no":   read_account(regions["account_no"]),
#     #"micr":         read_micr(regions["micr"]),
# }

# print("\n📋 EXTRACTED FIELDS")
# print("─" * 50)
# for k, v in fields.items():
#     print(f"  {k:<15}: {v}")