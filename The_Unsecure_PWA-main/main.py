from flask import Flask, render_template, request, redirect, url_for, session
import userManagement as dbHandler
import pyotp
import pyqrcode
import os
import base64
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'my_secret_key'

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


@app.route("/index.html", methods=["POST", "GET"])
@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "GET":
        return render_template("index.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        isLoggedIn = dbHandler.retrieveUsers(username, password)
        if isLoggedIn:
            session['username'] = username
            session['user_secret'] = pyotp.random_base32()  # Generate a unique secret for the user
            return redirect(url_for('enable_2fa'))  # Redirect to 2FA page
        else:
            return render_template("index.html", error="Invalid credentials")
    return render_template("index.html")

@app.route("/enable_2fa", methods=["GET", "POST"])
def enable_2fa():
    user_secret = session.get('user_secret')
    if not user_secret:
        return redirect(url_for('home'))  # Redirect to home if no secret is found

    totp = pyotp.TOTP(user_secret)
    username = session.get('username', 'default_user')
    otp_uri = totp.provisioning_uri(name=username, issuer_name="YourAppName")
    qr_code = pyqrcode.create(otp_uri)
    stream = BytesIO()
    qr_code.png(stream, scale=5)
    qr_code_b64 = base64.b64encode(stream.getvalue()).decode('utf-8')

    if request.method == "POST":
        otp_input = request.form["otp"]
        if totp.verify(otp_input):
            return render_template("success.html", value=username, state=True)  # Redirect to success page
        else:
            return render_template("enable_2fa.html", qr_code=qr_code_b64, error="Invalid OTP. Please try again.")

    return render_template("enable_2fa.html", qr_code=qr_code_b64)

if __name__ == "__main__":
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
    app.run(debug=True, host="0.0.0.0", port=5000)
