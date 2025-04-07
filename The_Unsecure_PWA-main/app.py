from flask import Flask, render_template, request, redirect, session
import pyotp
import qrcode
import base64
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Route for login
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    # Store user data in session
    session['username'] = username
    session['email'] = email
    # Generate a secret key for 2FA
    session['2fa_secret'] = pyotp.random_base32()
    return redirect('/enable_2fa')

# Route to display the 2FA enable page
@app.route('/enable_2fa')
def enable_2fa():
    secret = session.get('2fa_secret')
    if not secret:
        return redirect('/')
    totp = pyotp.TOTP(secret)
    qr_code_data = totp.provisioning_uri(session['email'], issuer_name="YourAppName")
    qr = qrcode.make(qr_code_data)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_code = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return render_template('enable_2fa.html', qr_code=qr_code)

# Route to verify OTP
@app.route('/verify_2fa', methods=['POST'])
def verify_2fa():
    otp = request.form['otp']
    secret = session.get('2fa_secret')
    totp = pyotp.TOTP(secret)
    if totp.verify(otp):
        return redirect('/success')
    else:
        return "Invalid OTP. Please try again.", 401

# Route for success page
@app.route('/success')
def success():
    username = session.get('username')
    return render_template('success.html', value=username)

if __name__ == '__main__':
    app.run(debug=True)
