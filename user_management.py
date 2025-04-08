import sqlite3 as sql  # Library for SQLite database operations
import bcrypt  # Library for hashing passwords
import time  # Library for adding delays
import random  # Library for generating random numbers

from flask import Flask, request, redirect, url_for, render_template  # Flask utilities

app = Flask(__name__)

def insertUser(username, password, DoB, email):
    """ Insert a new user with a hashed password """
    # Connect to the SQLite database
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    
    # Hash the password for secure storage
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    
    # Insert the user details into the database
    cur.execute(
        "INSERT INTO users (username, password, dateOfBirth, email) VALUES (?, ?, ?, ?)",
        (username, hashed_password, DoB, email),
    )
    con.commit()  # Commit the transaction
    con.close()  # Close the database connection

def retrieveUsers(username, password):
    """ Verify user login by checking hashed password """
    # Connect to the SQLite database
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    
    # Fetch the hashed password for the given username
    cur.execute("SELECT password FROM users WHERE username = ?", (username,))
    record = cur.fetchone()
    
    if not record:
        con.close()
        return False  # User does not exist

    stored_hashed_password = record[0]

    # Verify the provided password against the stored hash
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
    # Connect to the SQLite database
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    
    # Filter feedback to remove non-numeric characters
    f = filter(str.isdecimal, feedback)
    s1 = "".join(f)
    print(s1)
    
    # Insert the sanitized feedback into the database
    cur.execute(f"INSERT INTO feedback (feedback) VALUES ('{s1}')")
    con.commit()
    con.close()

def listFeedback():
    """ Retrieve and display feedback securely """
    # Connect to the SQLite database
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    
    # Fetch all feedback records
    data = cur.execute("SELECT * FROM feedback").fetchall()
    con.close()
    
    # Write feedback to an HTML file for display
    with open("templates/partials/success_feedback.html", "w") as f:
        for row in data:
            f.write("<p>\n")
            f.write(f"{row[1]}\n")
            f.write("</p>\n")

