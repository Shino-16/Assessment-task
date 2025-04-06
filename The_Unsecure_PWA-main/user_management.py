import sqlite3 as sql
import time
import random
from werkzeug.security import generate_password_hash, check_password_hash

def insertUser(username, password, DoB):
    hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    cur.execute(
        "INSERT INTO users (username, password, dateOfBirth) VALUES (?, ?, ?)",
        (username, hashed_password, DoB),
    )
    con.commit()
    con.close()

def retrieveUsers(username, password):
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cur.fetchone()
    if user is None:
        con.close()
        return False
    else:
        stored_password = user[2]  # Assuming password is the third column
        if check_password_hash(stored_password, password):
            # Plain text log of visitor count as requested by Unsecure PWA management
            with open("visitor_log.txt", "r") as file:
                number = int(file.read().strip())
                number += 1
            with open("visitor_log.txt", "w") as file:
                file.write(str(number))
            # Simulate response time of heavy app for testing purposes
            time.sleep(random.randint(80, 90) / 1000)
            con.close()
            return True
        else:
            con.close()
            return False

def insertFeedback(feedback):
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    cur.execute("INSERT INTO feedback (feedback) VALUES (?)", (feedback,))
    con.commit()
    con.close()

def listFeedback():
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    data = cur.execute("SELECT * FROM feedback").fetchall()
    con.close()
    f = open("templates/partials/success_feedback.html", "w")
    for row in data:
        f.write("<p>\n")
        f.write(f"{row[1]}\n")
        f.write("</p>\n")
    f.close()
