#Import necessary libraries
from flask import Flask, render_template, redirect, url_for, request
import cv2
import pyodbc
#Initialize the Flask app



def execute_sql(query):
    connection = pyodbc.connect('Driver={SQL Server};'
                      'Server=.;'
                      'Database=IncidentRecord;'
                      'Trusted_Connection=yes;')

    cursor = connection.cursor()
    cursor.execute(query)

    return cursor.fetchall()
# cursor.execute('SELECT * FROM [History]')
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
    historyData = execute_sql('Select H.HistoryID, C.LicensePlate, H.EnterTimestamp, H.ExitTimestamp, H.Activity FROM History H JOIN Car C ON H.CarID = C.CarID')
    incidentData = execute_sql('Select I.IncidentID, C.LicensePlate, CUS.FirstName, CUS.LastName, I.Type, I.StartTimestamp, I.EndTimestamp, I.Status, U.FirstName, U.LastName, I.Description FROM Incident I JOIN Car C ON I.CarID = C.CarID JOIN Customer CUS ON C.CustomerID = CUS.CustomerID JOIN [User] U ON U.UserID = I.UserID')
    carData = execute_sql('Select C.CarID, C.LicensePlate, CUS.FirstName, CUS.LastName, CUS.Phone, H.EnterTimestamp, I.Type FROM Car C JOIN Customer CUS ON C.CustomerID = CUS.CustomerID JOIN Incident I ON C.CarID = I.CarID JOIN History H ON C.CarID = H.CarID')
    
    return render_template('home.html', historyData = historyData, incidentData = incidentData, carData = carData)


@app.route('/login', methods=['GET', 'POST'])
def logout():
    userData = execute_sql('Select * from [User]')
    
    return render_template('login.html', userData = userData)