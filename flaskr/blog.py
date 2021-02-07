from flask import Flask, render_template, redirect, url_for, request, session, Response
import cv2
import pyodbc
import numpy as np
import imutils
import pytesseract
import datetime
import threading
import argparse
from imutils.video import VideoStream


connection = pyodbc.connect('Driver={SQL Server};'
                            'Server=.;'
                            'Database=IncidentRecord;'
                            'Trusted_Connection=yes;')
cursor = connection.cursor()

app = Flask(__name__, static_folder='static')

app.secret_key = '123456789'


@app.route('/login', methods=['GET'])
def login():
    
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def do_login():
    error = ""
    username = request.form['username']
    password = request.form['password']

    account = cursor.execute(
        'SELECT * FROM [User] WHERE userName = ? AND password = ?', (username, password))
    account = cursor.fetchone()
    if account:
        session['loggedin'] = True
        session['firstname'] = account[3]
        session['lastname'] = account[4]
        session['type'] = account[5].lower()
        
        return redirect(url_for('home'))
    else:
        error = "Incorrect username or password!"
    return render_template('login.html', error=error)

@app.route('/logout', methods=['GET','POST'])
def logout():
    session['loggedin'] = False
    return home()

@app.route('/blacklist')
def blacklist():
    return render_template('blacklist.html')

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/')
def home():
    if not session.get('loggedin'):
        return render_template('login.html')

    historyData = cursor.execute('SELECT H.HistoryID, C.LicensePlate, H.EnterTimestamp, H.ExitTimestamp, H.Activity FROM History H JOIN Car C ON H.CarID = C.CarID')
    historyData = cursor.fetchall()
    incidentData = cursor.execute('SELECT I.IncidentID, C.LicensePlate, CUS.FirstName, CUS.LastName, I.Type, I.StartTimestamp, I.EndTimestamp, I.Status, U.FirstName, U.LastName, I.Description FROM Incident I JOIN Car C ON I.CarID = C.CarID JOIN Customer CUS ON C.CustomerID = CUS.CustomerID JOIN [User] U ON U.UserID = I.UserID')
    incidentData = cursor.fetchall()
    carDate = cursor.execute('SELECT C.CarID, C.LicensePlate, Customer.FirstName, Customer.LastName, Customer.Phone, MAX(H.EnterTimestamp) FROM History H JOIN Car C ON H.CarID = C.CarID JOIN Customer ON C.CustomerID = Customer.CustomerID GROUP BY C.LicensePlate, C.CarID, C.CustomerID, Customer.FirstName, Customer.LastName, Customer.Phone')
    carData = cursor.fetchall()
    enterData = cursor.execute('SELECT TOP 1 C.LicensePlate, H.EnterTimestamp FROM History H JOIN Car C ON H.CarID = C.CarID ORDER BY H.HistoryID DESC')
    enterData = cursor.fetchone()
    exitData = cursor.execute('SELECT TOP 1 C.LicensePlate, H.ExitTimestamp FROM History H JOIN Car C ON H.CarID = C.CarID WHERE H.ExitTimestamp IS NOT NULL ORDER BY H.HistoryID DESC')
    exitData = cursor.fetchone()
    
    if(session.get('type') != "admin"):
        return render_template('userHome.html', historyData=historyData, incidentData=incidentData, carData=carData, EnterLicensePlate=enterData[0], EnterTime=enterData[1], ExitLicensePlate=exitData[0], ExitTime=exitData[1])
    
    return render_template('home.html', historyData=historyData, incidentData=incidentData, carData=carData, EnterLicensePlate=enterData[0], EnterTime=enterData[1], ExitLicensePlate=exitData[0], ExitTime=exitData[1])


def genEnterVid():
    while True:
        frame = cv2.imread('static/enterVideo/enter.jpg')

        r, jpeg = cv2.imencode('.jpg', frame)

        frame = jpeg.tobytes()
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/enterVideo_feed')
def enterVideo_feed():
    return Response(genEnterVid(), mimetype='multipart/x-mixed-replace; boundary=frame')


def genExitVid():
    while True:
        frame = cv2.imread('static/exitVideo/exit.jpg')

        r, jpeg = cv2.imencode('.jpg', frame)

        frame = jpeg.tobytes()
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/exitVideo_feed')
def exitVideo_feed():
    return Response(genExitVid(), mimetype='multipart/x-mixed-replace; boundary=frame')
