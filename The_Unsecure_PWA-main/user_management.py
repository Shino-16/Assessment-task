import sqlite3 as sql
import bcrypt
import time
import random

from flask import Flask, request, redirect, url_for, render_template  # Added redirect and url_for

app = Flask(__name__)

def insertUser(username, password, DoB, email):
    """ Insert a new user with a hashed password """
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    
    # Hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    
    cur.execute(
        "INSERT INTO users (username, password, dateOfBirth, email) VALUES (?, ?, ?, ?)",  # Fixed column name
        (username, hashed_password, DoB, email),
    )
    con.commit()
    con.close()

def retrieveUsers(username, password):
    """ Verify user login by checking hashed password """
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    
    # Fetch user record
    cur.execute("SELECT password FROM users WHERE username = ?", (username,))
    record = cur.fetchone()
    
    if not record:
        con.close()
        return False  # User does not exist

    stored_hashed_password = record[0]

    # Verify password
    if bcrypt.checkpw(password.encode(), stored_hashed_password):
        # Update visitor log
        with open("visitor_log.txt", "r") as file:
            number = int(file.read().strip())
            number += 1
        with open("visitor_log.txt", "w") as file:
            file.write(str(number))

        # Simulate response time
        time.sleep(random.randint(80, 90) / 1000)

        con.close()
        return True
    else:
        con.close()
        return False

def insertFeedback(feedback):
    """ Store feedback securely """
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    cur.execute("INSERT INTO feedback (feedback) VALUES (?)", (feedback,))
    con.commit()
    con.close()

def listFeedback():
    """ Retrieve and display feedback securely """
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    data = cur.execute("SELECT * FROM feedback").fetchall()
    con.close()
    
    with open("templates/partials/success_feedback.html", "w") as f:
        for row in data:
            f.write("<p>\n")
            f.write(f"{row[1]}\n")
            f.write("</p>\n")

