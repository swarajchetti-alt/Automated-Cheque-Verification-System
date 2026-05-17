from datetime import datetime
from word2number import w2n
from flask import Flask, render_template, request, redirect
import cv2
import os
from src.preprocess import preprocess,preprocess_date
from src.regions import get_regions
from src.ocr import (
    read_date,
    read_payee,
    read_handwritten,
    read_amount_fig,
    read_account
)
from src.signature import load_model, compare
from src.database import get_user, add_user, init_db, get_all_users, update_balance
from flask import send_from_directory

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# initialize DB + model
init_db()
model = load_model()


# 🔹 HOME (Cheque Verification)
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["cheque"]

        if file:
            path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(path)

            imgorg = cv2.imread(path)
            img=cv2.resize(imgorg,(1600,688))

            if img is None:
                return "❌ Image not found"

            processed = preprocess(img)
            imgd=preprocess_date(img)
            regions = get_regions(processed,imgd)

            # OCR
            date = read_date(regions["date"])
            payee = read_payee(regions["payee"])
            amount_words = read_handwritten(regions["amount_words"])
            amount_fig = read_amount_fig(regions["amount_fig"])
            account_no = read_account(regions["account_no"])

            # DB lookup
            # user = get_user(account_no)

            # if user:
            #     ref_path = user[2]
            #     ref_img = cv2.imread(ref_path, 0)

            #     cheque_sig = regions["signature"]
            #     distance = compare(model, cheque_sig, ref_img)

            #     result = "MATCH" if distance < 0.7 else "MISMATCH"
            # else:
            #     result = "ACCOUNT NOT FOUND"
            #     distance = None



            reasons = []

            # 🔹 DATE CHECK
            valid_date, msg = verify_date(date)
            if not valid_date:
                reasons.append("Date issue: " + msg)

            # 🔹 AMOUNT CHECK
            if not verify_amount(amount_words, amount_fig):
                reasons.append("Amount mismatch")

            # 🔹 USER CHECK 
            from src.database import get_user_by_name
            user = get_user_by_name(payee)

            if not user:
                reasons.append("User not found")

            # 🔹 SIGNATURE CHECK
            if user:
                ref_path = user[3]

                # fix path (remove accidental leading slash)
                ref_path = ref_path.lstrip("/")

                ref_img = cv2.imread(ref_path, 0)

                if ref_img is None:
                    print("❌ ERROR: Signature image not found at", ref_path)
                    return "Signature file missing"
                # ref_path = user[2]
                # ref_img = cv2.imread(ref_path, 0)

                cheque_sig = regions["signature"]
                distance = compare(model, cheque_sig, ref_img)

                if distance >1:
                    reasons.append("Signature mismatch")
            else:
                distance = None

            # 🔹 BALANCE CHECK
            if user:
                if not check_balance(user, amount_fig):
                    reasons.append("Insufficient balance (Cheque Bounce)")

            # 🔹 FINAL RESULT
            if len(reasons) == 0:
                result = "✅ VERIFIED"
                new_balance = user[4] - float(amount_fig)
                update_balance(user[1], new_balance)
            else:
                result = "❌ REJECTED"

            if user:
                payee = user[2]
                account_no = user[1]
                balance = user[4]
            else:
                payee = "Unknown"
                account_no = "N/A"
                balance = 0

            return render_template("index.html",
                                    date=date,
                                    payee=payee,
                                    #payee=user[2],
                                    amount_words=amount_words,
                                    amount_fig=amount_fig,
                                    account_no=account_no,
                                    result=result,
                                    reasons=reasons,
                                    distance=distance
                                )

    return render_template("index.html")


# 🔹 ADD USER
@app.route("/add_user", methods=["GET", "POST"])
def add_user_page():
    if request.method == "POST":
        account = request.form["account"]
        name = request.form["name"]
        signature = request.files["signature"]

        #sig_path = os.path.join("uploads", signature.filename)
        filename = signature.filename.replace(" ", "_")
        #filename = signature.filename

        # real path (for saving)
        save_path = os.path.join("uploads", filename)

        # url path (for browser)
        db_path = f"/uploads/{filename}"

        signature.save(save_path)
        balance=float(request.form["balance"])

        # store URL path in DB
        add_user(account, name, db_path, balance)
       

        return redirect("/view_users")

    return render_template("add_user.html")


# 🔹 VIEW USERS
@app.route("/view_users")
def view_users():
    users = get_all_users()
    return render_template("view_users.html", users=users)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

@app.route("/delete_user/<int:user_id>")
def delete_user_route(user_id):
    from src.database import delete_user
    delete_user(user_id)
    return redirect("/view_users")

# ✅ DATE CHECK
def verify_date(date_str):
    try:
        cheque_date = datetime.strptime(date_str, "%d/%m/%Y")
        today = datetime.today()

        if cheque_date > today:
            return False, "Future date"

        if (today - cheque_date).days > 90:
            return False, "Cheque expired"

        return True, "Valid"
    except:
        return False, "Invalid date format"


# ✅ AMOUNT CHECK

def verify_amount(words, figures):
    try:
        words = words.lower().replace("only", "").strip()

        # 🔥 Handle Indian units manually
        if "lakh" in words:
            parts = words.split("lakh")
            num_part = parts[0].strip()

            base = w2n.word_to_num(num_part)
            num = base * 100000

        elif "crore" in words:
            parts = words.split("crore")
            num_part = parts[0].strip()

            base = w2n.word_to_num(num_part)
            num = base * 10000000

        else:
            num = w2n.word_to_num(words)

        figures = figures.replace(",", "").strip()

        return int(num) == int(figures)

    except Exception as e:
        print("Amount conversion error:", e)
        return False
    
def check_balance(user, amount):
    try:
        balance = user[4]   # balance column
        amount = float(amount)

        if balance >= amount:
            return True
        else:
            return False
    except:
        return False
# print("WORDS:", words)
# print("FIG:", figures)
# print("CONVERTED:", num)
    
if __name__ == "__main__":
    app.run(debug=True)