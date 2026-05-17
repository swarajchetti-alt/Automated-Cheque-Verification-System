def get_regions(img,imgd):
    return {
        "date":     imgd[45:110,   1150:1550],
        "payee":    img[130:195,  115:1100],
        "amount_words": img[200:263,  210:1100],
        "amount_fig": img[262:333,  1215:1525],
        "account_no":  img[345:405,  205:515],
        "micr":         img[400:600,  310:1700],
        "signature":    img[400:500, 1000:1700],
    }