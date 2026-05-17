# ACVS - Automated Cheque Verification System 🚀

## Overview
ACVS is a Flask-based cheque verification application that extracts cheque fields using OCR, validates cheque details, and verifies signatures against stored reference signatures. It is designed for Indian cheque formats and includes user management with account balance checks.

## Key Features ✨
- ✅ Cheque image upload and field extraction
- ✅ Date validation (future date, expiry)
- ✅ Amount text vs figure verification
- ✅ Payee lookup from user database
- ✅ Signature verification using a Siamese CNN model
- ✅ Account balance check and rejection for insufficient funds
- ✅ User management: add, view, and delete users

## Repository Structure 📁
- `ACVS/app.py` - Flask application entrypoint
- `ACVS/src/` - application modules
  - `database.py` - SQLite user database operations
  - `preprocess.py` - cheque image preprocessing
  - `regions.py` - cheque field region extraction
  - `ocr.py` - OCR methods for cheque fields
  - `signature.py` - signature model loading and comparison
- `ACVS/templates/` - HTML templates for the UI
- `ACVS/static/style.css` - application styles
- `ACVS/uploads/` - uploaded cheque and signature images
- `ACVS/siamese_cnn_training/` - training code and signature model artifacts

## Requirements 🧩
Install Python dependencies from `ACVS/requirements.txt`:

```bash
pip install -r ACVS/requirements.txt
```

> Note: Tesseract OCR must be installed separately if not already available. On Windows, add the Tesseract executable path to your system PATH.

## Running the App ▶️
From the workspace root, run:

```bash
cd ACVS
python app.py
```

Then open the browser at `http://127.0.0.1:5000`.

## Usage 📝
1. Add a new user with account number, name, signature image, and initial balance.
2. Upload a cheque image on the home page.
3. The app performs:
   - 🔍 date validation
   - 💰 amount text/figure matching
   - 👤 payee lookup
   - ✍️ signature comparison
   - 💳 balance verification
4. The result is shown as `VERIFIED` or `REJECTED` with reasons.

## Notes 💡
- Uploaded files are saved to `ACVS/uploads/`.
- The signature model is loaded from `ACVS/src/signature.py`; a pre-trained model file is expected in the repo.
- The database is initialized automatically when the app starts.
