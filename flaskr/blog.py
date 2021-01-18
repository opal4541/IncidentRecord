#Import necessary libraries
from flask import Flask, render_template, redirect, url_for, request
import cv2
import pyodbc
#Initialize the Flask app

conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=.;'
                      'Database=IncidentRecord;'
                      'Trusted_Connection=yes;')

cursor = conn.cursor()
cursor.execute('SELECT * FROM [User]')
# for row in cursor:
#     print(row)

app = Flask(__name__, static_folder='static')


@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        if valid_login(request.form['username'], request.form['password']):
            return log_the_user_in(request.form['username'])
        else:
            error = 'Invalid username/password'
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    return render_template('login.html', error=error)


@app.route('/camera')
def camera():
    return render_template('camera.html')


@app.route('/transaction')
def index():
    return render_template('transaction.html')


@app.route('/blacklist')
def blacklist():
    return render_template('blacklist.html')


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def logout():

    return render_template('login.html')