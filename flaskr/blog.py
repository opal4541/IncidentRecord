#Import necessary libraries
from flask import Flask, render_template, redirect, url_for, request
import cv2
#Initialize the Flask app
app = Flask(__name__, static_folder='static')


@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        if valid_login(request.form['username'],
                       request.form['password']):
            return log_the_user_in(request.form['username'])
        else:
            error = 'Invalid username/password'
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    return render_template('login.html', error=error)

@app.route('/camera')
def camera():
    return render_template('camera.html')

@app.route('/index')
def index():
    return render_template('index.html')
