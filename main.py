from flask import Flask, render_template, request, redirect, session
import user_management as dbHandler  # Custom module for database operations
import pyotp  # Library for generating and verifying one-time passwords (OTP)
import qrcode  # Library for generating QR codes
import base64  # Library for encoding QR code images
from io import BytesIO  # Library for handling in-memory binary streams

app = Flask(__name__)
app.secret_key = "your_unique_secret_key"  # Secret key for session management (used for cookies and sessions)

# Route for login
@app.route("/login", methods=["POST"])
def login():
    # Handles user login by verifying credentials
    username = request.form["username"]
    password = request.form["password"]
    email = request.form["email"]
    isLoggedIn = dbHandler.retrieveUsers(username, password)  # Check if user exists and password is correct
    if isLoggedIn:
        # If login is successful, generate a 2FA secret and store it in the session
        session["username"] = username
        session["email"] = email
        session["2fa_secret"] = pyotp.random_base32()  # Generate a random base32 secret for 2FA
        return redirect("/enable_2fa")  # Redirect to the 2FA enable page
    else:
        # If login fails, return to the login page with an error message
        return render_template("/index.html", error="Invalid credentials")

# Route to display the 2FA enable page
@app.route("/enable_2fa", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
def enable_2fa():
    # Handles the generation and display of the QR code for 2FA
    if request.method == "GET" and request.args.get("url"):
        # Redirect if a URL parameter is provided
        url = request.args.get("url", "")
        return redirect(url, code=302)
    if request.method == "POST":
        # Generate and display the QR code for 2FA
        secret = session.get("2fa_secret")  # Retrieve the 2FA secret from the session
        if not secret:
            return redirect("/")  # Redirect to home if no secret is found
        totp = pyotp.TOTP(secret)  # Create a TOTP object using the secret
        qr_code_data = totp.provisioning_uri(session["email"], issuer_name="YourAppName")  # Generate provisioning URI
        qr = qrcode.make(qr_code_data)  # Generate QR code
        buffer = BytesIO()  # Create an in-memory binary stream
        qr.save(buffer, format="PNG")  # Save the QR code as a PNG image in the stream
        qr_code = base64.b64encode(buffer.getvalue()).decode("utf-8")  # Encode the image in base64
        return render_template("enable_2fa.html", qr_code=qr_code)  # Render the 2FA page with the QR code
    else:
        # Handle other HTTP methods (fallback)
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

# Route to verify OTP
@app.route("/verify_2fa", methods=["POST"])
def verify_2fa():
    # Verifies the OTP entered by the user
    otp = request.form["otp"]  # Get the OTP from the form
    secret = session.get("2fa_secret")  # Retrieve the 2FA secret from the session
    totp = pyotp.TOTP(secret)  # Create a TOTP object using the secret
    if totp.verify(otp):  # Verify the OTP
        return redirect("/success.html")  # Redirect to the success page if OTP is valid
    else:
        return render_template("enable_2fa.html", error="Invalid OTP")  # Show an error if OTP is invalid

# Route for success page
@app.route("/success.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
def addFeedback():
    # Handles feedback submission and displays feedback
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)
    if request.method == "POST":
        feedback = request.form["feedback"]  # Get feedback from the form
        dbHandler.insertFeedback(feedback)  # Insert feedback into the database
        dbHandler.listFeedback()  # Retrieve and display all feedback
        return render_template("/success.html", state=True, value="Back")
    else:
        dbHandler.listFeedback()
        return render_template("/success.html", state=True, value="Back")

# Route for signup
@app.route("/signup.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
def signup():
    # Handles user signup by storing user details in the database
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        DoB = request.form["dob"]
        email = request.form["email"]
        dbHandler.insertUser(username, password, DoB, email)  # Insert user into the database
        return render_template("/index.html")  # Redirect to the login page
    else:
        return render_template("/signup.html")  # Render the signup page

# Route for home/index
@app.route("/index.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
@app.route("/", methods=["POST", "GET"])
def home():
    # Handles the home page and login functionality
    if request.method == "GET" and request.args.get("url"):
        url = request.args.get("url", "")
        return redirect(url, code=302)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        isLoggedIn = dbHandler.retrieveUsers(username, password)  # Verify user credentials
        if isLoggedIn:
            dbHandler.listFeedback()  # Retrieve feedback if login is successful
            return render_template("/success.html", value=username, state=isLoggedIn)
        else:
            return render_template("/index.html")  # Show login page if login fails
    else:
        return render_template("/index.html")  # Render the home page

if __name__ == "__main__":
    # Run the Flask application
    app.config["TEMPLATES_AUTO_RELOAD"] = True  # Automatically reload templates when they change
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0  # Disable caching for static files
    app.run(debug=True, host="0.0.0.0", port=5000)  # Run the app in debug mode on port 5000