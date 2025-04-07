from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
import user_management as dbHandler
import pyotp
import qrcode
import base64
from io import BytesIO
from flask import session

# Code snippet for logging a message
# app.logger.critical("message")

app = Flask(__name__)
app.secret_key = "your_unique_secret_key"  # Add this line


@app.route("/success.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
def addFeedback():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)
    if request.method == "POST":
        feedback = request.form["feedback"]
        dbHandler.insertFeedback(feedback)
        dbHandler.listFeedback()
        return render_template("/success.html", state=True, value="Back")
    else:
        dbHandler.listFeedback()
        return render_template("/success.html", state=True, value="Back")


@app.route("/signup.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
def signup():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        DoB = request.form["dob"]
        email = request.form["email"]
        dbHandler.insertUser(username, password, DoB, email)
        return render_template("/index.html")
    else:
        return render_template("/signup.html")


@app.route("/index.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        isLoggedIn = dbHandler.retrieveUsers(username, password)
        if isLoggedIn:
            dbHandler.listFeedback()
            return render_template("/success.html", value=username, state=isLoggedIn)
        else:
            return render_template("/index.html")
    else:
        return render_template("/index.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    email = request.form["email"]
    isLoggedIn = dbHandler.retrieveUsers(username, password)
    if isLoggedIn:
        # Generate a 2FA secret and store it in the session
        session["username"] = username
        session["email"] = email
        session["2fa_secret"] = pyotp.random_base32()
        return redirect("/enable_2fa")
    else:
        return render_template("/index.html", error="Invalid credentials")

@app.route("/enable_2fa")
def enable_2fa():
    secret = session.get("2fa_secret")
    if not secret:
        return redirect("/")
    totp = pyotp.TOTP(secret)
    qr_code_data = totp.provisioning_uri(session["email"], issuer_name="YourAppName")
    qr = qrcode.make(qr_code_data)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_code = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return render_template("enable_2fa.html", qr_code=qr_code)

@app.route("/verify_2fa", methods=["POST"])
def verify_2fa():
    otp = request.form["otp"]
    secret = session.get("2fa_secret")
    totp = pyotp.TOTP(secret)
    if totp.verify(otp):
        return redirect("/success.html")
    else:
        return render_template("enable_2fa.html", error="Invalid OTP")


if __name__ == "__main__":
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
    app.run(debug=True, host="0.0.0.0", port=5000)