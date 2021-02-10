from flask import Flask, render_template, redirect, url_for, request, session, Response, jsonify
import cv2
import pyodbc
import numpy as np
import imutils
import pytesseract
import datetime
import threading
import argparse
import json
from imutils.video import VideoStream
from flask_socketio import SocketIO, emit


connection = pyodbc.connect('Driver={SQL Server};'
                            'Server=.;'
                            'Database=IncidentRecord;'
                            'Trusted_Connection=yes;')
cursor = connection.cursor()

app = Flask(__name__, static_folder='static')
app.secret_key = '123456789'
socketio = SocketIO(app)


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


def genEnterVid():
    while True:
        frame = cv2.imread('static/enterVideo/enter.jpg')

        r, jpeg = cv2.imencode('.jpg', frame)

        frame = jpeg.tobytes()
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/entervideo_feed')
def entervideo_feed():
    return Response(genEnterVid(), mimetype='multipart/x-mixed-replace; boundary=frame')


def genExitVid():
    while True:
        frame = cv2.imread('static/exitVideo/exit.jpg')

        r, jpeg = cv2.imencode('.jpg', frame)

        frame = jpeg.tobytes()
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/exitvideo_feed')
def exitvideo_feed():
    return Response(genExitVid(), mimetype='multipart/x-mixed-replace; boundary=frame')


# tempEnterTime = ''
# def getEnterTime():
#     global tempEnterTime
#     enterTime = cursor.execute('SELECT TOP 1 H.EnterTimestamp FROM History H ORDER BY H.HistoryID DESC')
#     enterTime = cursor.fetchone()
    
#     if tempEnterTime != enterTime:
#         tempEnterTime = str(enterTime[0])

#     return tempEnterTime

# def genEnterTime():
#     yield getEnterTime()

# @app.route('/entertime_feed')
# def entertime_feed():
#     return Response(genEnterTime(), mimetype='text') 

# tempEnterLicense = ''
# def getEnterLicense():
#     global tempEnterLicense
#     enterLicense = cursor.execute('SELECT TOP 1 C.LicensePlate FROM History H JOIN Car C ON H.CarID = C.CarID ORDER BY H.HistoryID DESC')
#     enterLicense = cursor.fetchone()

#     if tempEnterLicense != enterLicense:
#         tempEnterLicense = enterLicense[0]

#     return str(tempEnterLicense)

# def genEnterLicense():
#     yield getEnterLicense()

# @app.route('/enterlicense_feed')
# def enterlicense_feed():
#     return Response(genEnterLicense(), mimetype='text') 

# def genEnter():
#     enter = []
#     enterLicense = cursor.execute('SELECT TOP 1 C.LicensePlate, H.EnterTimestamp FROM History H JOIN Car C ON H.CarID = C.CarID ORDER BY H.HistoryID DESC')
#     enterLicense = cursor.fetchone()
#     for e in enterLicense:
#         enter.append(str(e))
    
#     enter_json = json.dumps(enter)
#     print(enter_json)
#     return enter_json

# genEnter()
# @app.route('/enter_feeed')
# def enter_feed():
#     return Response(genEnter(), mimetype='applicant/json')


@app.route('/addactivity', methods=['POST','GET'])
def addActivity():
    if request.method == 'POST':
        historyID = request.form['hisid']
        licenseplate = request.form['licenseplateaddact']
        EnterTime = request.form['entertimeaddact']
        ExitTime = request.form['exittimeaddact']
        activity = request.form['activityaddact']

        cursor.execute('UPDATE History SET Activity = ? WHERE HistoryID = ?', (activity,historyID))
        connection.commit()
        return redirect(url_for('home'))


@app.route('/addincidentfromhistory',methods=['POST','GET'])
def addIncidentFromHistory():
    if request.method == 'POST': 
        licenseplate = request.form['licenseplateaddincfromhis']
        fname = request.form['cusfirstnameaddincfromhis']
        lname = request.form['cuslastnameaddincfromhis']
        typeinc = request.form['typeaddincfromhis']
        description = request.form['descriptionaddincfromhis']
        
        carid = cursor.execute('SELECT CarID FROM Car WHERE LicensePlate = ? ', (licenseplate))
        carid = cursor.fetchone()
        userid = cursor.execute("SELECT UserID From [User] WHERE [User].FirstName = ? AND [User].LastName = ?", (session['firstname'], session['lastname']))
        userid = cursor.fetchone()
        cusid = cursor.execute('SELECT CustomerID From Customer WHERE FirstName = ? AND LastName = ?', (fname, lname))
        cusid = cursor.fetchone()
        incid = cursor.execute('SELECT IncidentID From Incident WHERE CarID = ? AND Status = ?', (carid[0], 'Active'))
        incid = cursor.fetchone()
        time = datetime.datetime.now()
        time = time.strftime("%Y-%m-%d %H:%M:%S")

        if incid:
            cursor.execute('UPDATE Incident SET EndTimeStamp = ?, Status = ? WHERE IncidentID = ?', (time, 'Inactive', incid[0]))
            connection.commit()
            return redirect(url_for('home'))

        if cusid:
            cursor.execute('INSERT INTO Incident(CarID, UserID, Description, Type, StartTimestamp, Status) VALUES (?, ?, ?, ?, ?, ?)', (carid[0], userid[0], description, typeinc, time, "Active"))
            connection.commit()
            return redirect(url_for('home'))
        else:
            # ถ้าไม่มี customer name อยู่ใน customer db ให้เอา cus id ที่เชื่อมกับ car id มาอัพเดทชื่อเอา
            cusidnew = cursor.execute('SELECT CustomerID From Car WHERE CarID = ?', (carid[0]))
            cusidnew = cursor.fetchone()
            cursor.execute('UPDATE Customer SET FirstName = ?, LastName = ? WHERE CustomerID = ?', (fname, lname, cusidnew[0]))
            cursor.execute('INSERT INTO Incident(CarID, UserID, Description, Type, StartTimestamp, Status) VALUES (?, ?, ?, ?, ?, ?)', (carid[0], userid[0], description, typeinc, time, "Active"))
                
        connection.commit()
        return redirect(url_for('home'))


@app.route('/editincident',methods=['POST','GET'])
def editIncident():
    if request.method == 'POST':
        incidentID = request.form['incid']
        licenseplate = request.form['licenseplateeditinc']
        fname = request.form['cusfirstnameeditinc']
        lname = request.form['cuslastnameeditinc']
        typeinc = request.form['typeeditinc']
        description = request.form['descriptioneditinc']
        
        carid = cursor.execute('SELECT CarID FROM Car WHERE Car.LicensePlate = ? ', (licenseplate))
        carid = cursor.fetchone()
        userid = cursor.execute("SELECT UserID From [User] WHERE [User].FirstName = ? AND [User].LastName = ?", (session['firstname'], session['lastname']))
        userid = cursor.fetchone()
        cusid = cursor.execute('SELECT CustomerID From Customer WHERE FirstName = ? AND LastName = ?', (fname, lname))
        cusid = cursor.fetchone()

        if carid:
            if cusid:
                cursor.execute('UPDATE Car SET CustomerID = ? WHERE CarID = ?', (cusid[0], carid[0]))
                cursor.execute('UPDATE Incident SET CarID = ?, UserID = ?, Type = ?, Description = ? WHERE IncidentID = ?', (carid[0], userid[0], typeinc, description, incidentID))
                connection.commit()
                return redirect(url_for('home'))
            else:
                # if the name was not input
                if fname == None:
                    cursor.execute('INSERT INTO Customer(FirstName, LastName) VALUES ("", "")')
                    connection.commit()
                    customerID = cursor.execute('SELECT TOP 1 CustomerID FROM Customer ORDER BY CustomerID DESC')
                    customerID = cursor.fetchone()
                    cursor.execute('UPDATE Car SET CustomerID = ? WHERE CarID = ?', (customerID[0], carid[0]))
                    cursor.execute('UPDATE Incident SET CarID = ?, UserID = ?, Type = ?, Description = ? WHERE IncidentID = ?', (carid[0], userid[0], typeinc, description, incidentID))
                    connection.commit()
                    return redirect(url_for('home'))
                # the name input
                else:
                    cursor.execute('INSERT INTO Customer(FirstName, LastName) VALUES (?,?)', (fname, lname))
                    customerID = cursor.execute('SELECT TOP 1 CustomerID FROM Customer ORDER BY CustomerID DESC')
                    customerID = cursor.fetchone()
                    cursor.execute('UPDATE Car SET CustomerID = ? WHERE CarID = ?', (customerID[0], carid[0]))
                    cursor.execute('UPDATE Incident SET CarID = ?, UserID = ?, Type = ?, Description = ? WHERE IncidentID = ?', (carid[0], userid[0], typeinc, description, incidentID))
                    connection.commit()
                    return redirect(url_for('home'))
        else:
            # the car does not exist but cus exist
            if cusid:
                cursor.execute('INSERT INTO Car(LicensePlate, CustomerID) VALUES(?, ?)', (licenseplate, cusid[0]))
                newcarID = cursor.execute('SELECT TOP 1 CarID FROM Car ORDER BY CarID DESC')
                newcarID = cursor.fetchone()
                cursor.execute('UPDATE Incident SET CarID = ?, UserID = ?, Type = ?, Description = ? WHERE IncidentID = ?', (newcarID[0], userid[0], typeinc, description, incidentID))
                connection.commit()
                return redirect(url_for('home'))
            else:
                # car and cus not exist
                # if the name was not input
                if fname == None:
                    cursor.execute('INSERT INTO Customer(FirstName, LastName) VALUES ("", "")')
                    customerID = cursor.execute('SELECT TOP 1 CustomerID FROM Customer ORDER BY CustomerID DESC')
                    customerID = cursor.fetchone()
                    cursor.execute('INSERT INTO Car(LicensePlate, CustomerID) VALUES (?,?)', (licenseplate,customerID[0]))
                    newcarID = cursor.execute('SELECT TOP 1 CarID FROM Car ORDER BY CarID DESC')
                    newcarID = cursor.fetchone()
                    cursor.execute('UPDATE Incident SET CarID = ?, UserID = ?, Type = ?, Description = ? WHERE IncidentID = ?', (newcarID[0], userid[0], typeinc, description, incidentID))
                    connection.commit()
                    return redirect(url_for('home'))
                # the name input
                else:
                    cursor.execute('INSERT INTO Customer(FirstName, LastName) VALUES (?,?)', (fname, lname))
                    customerID = cursor.execute('SELECT TOP 1 CustomerID FROM Customer ORDER BY CustomerID DESC')
                    customerID = cursor.fetchone()
                    cursor.execute('INSERT INTO Car(LicensePlate, CustomerID) VALUES (?,?)', (licenseplate,customerID[0]))
                    newcarID = cursor.execute('SELECT TOP 1 CarID FROM Car ORDER BY CarID DESC')
                    newcarID = cursor.fetchone()
                    cursor.execute('UPDATE Incident SET CarID = ?, UserID = ?, Type = ?, Description = ? WHERE IncidentID = ?', (newcarID[0], userid[0], typeinc, description, incidentID))
                    connection.commit()
                    return redirect(url_for('home'))

        cursor.execute('UPDATE Incident SET CarID = ?, UserID = ?, Type = ?, Description = ? WHERE IncidentID = ?', (carid[0], userid[0], typeinc, description, incidentID))
        connection.commit()
        return redirect(url_for('home'))
    

@app.route('/deactivate', methods=['POST'])
def deactivate():
    if request.method == 'POST':
        incidentID = request.form['incid']
        time = datetime.datetime.now()
        time = time.strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("UPDATE Incident SET EndTimeStamp = ?, Status = ? WHERE IncidentID = ?", (time, "Inactive", incidentID))
        connection.commit()
        return home()


@app.route('/addincident', methods = ['POST'])
def addIncident():
    if request.method == "POST":
        licenseplate = request.form['licenseplateaddinc']
        fname = request.form['cusfirstnameaddinc']
        lname = request.form['cuslastnameaddinc']
        typeinc = request.form['typeaddinc']
        description = request.form['descriptionaddinc']

        carid = cursor.execute('SELECT CarID FROM Car WHERE LicensePlate = ? ', (licenseplate))
        carid = cursor.fetchone()
        cusid = cursor.execute("SELECT CustomerID From Customer WHERE FirstName = ? AND LastName = ?", (fname, lname))
        cusid = cursor.fetchone()
        userid = cursor.execute("SELECT UserID From [User] WHERE [User].FirstName = ? AND [User].LastName = ?", (session['firstname'], session['lastname']))
        userid = cursor.fetchone()
        time = datetime.datetime.now()
        time = time.strftime("%Y-%m-%d %H:%M:%S")

        # if the licenseplate existing
        if carid:
            # if the license plate already have incident, then it will deactivate the old one
            incid = cursor.execute('SELECT IncidentID From Incident WHERE CarID = ? AND Status = ?', (carid[0], 'Active'))
            incid = cursor.fetchone()    
            if incid:
                cursor.execute('UPDATE Incident SET EndTimeStamp = ?, Status = ? WHERE IncidentID = ?', (time, 'Inactive', incid[0]))
                connection.commit()
            # if the licenseplate exist then customer also exist, then update the customerid
            if cusid:
                cursor.execute('UPDATE Car SET CustomerID = ? WHERE CarID = ?', (cusid, carid))
                cursor.execute("INSERT INTO Incident(CarID, UserID, Description, Type, StartTimestamp, Status) VALUES (?, ?, ?, ?, ?, ?)", (carid[0], userid[0], description, typeinc, time, "Active"))
                connection.commit()
                return redirect(url_for('home'))
            else:
                # if the name was not input
                if fname == None:
                    cursor.execute('INSERT INTO Customer(FirstName, LastName) VALUES ("", "")')
                    connection.commit()
                    customerID = cursor.execute('SELECT TOP 1 CustomerID FROM Customer ORDER BY CustomerID DESC')
                    customerID = cursor.fetchone()
                    cursor.execute('UPDATE Car SET CustomerID = ? WHERE CarID = ?', (customerID[0], carid[0]))
                    cursor.execute('INSERT INTO Incident(CarID, UserID, Description, Type, StartTimestamp, Status) VALUES (?, ?, ?, ?, ?, ?)', (carid[0], userid[0], description, typeinc, time, "Active"))
                    connection.commit()
                    return redirect(url_for('home'))
                # the name input
                else:
                    cursor.execute('INSERT INTO Customer(FirstName, LastName) VALUES (?,?)', (fname, lname))
                    cursor.execute('UPDATE Car SET CustomerID = ? WHERE CarID = ?', (customerID[0], carid[0]))
                    cursor.execute('INSERT INTO Incident(CarID, UserID, Description, Type, StartTimestamp, Status) VALUES (?, ?, ?, ?, ?, ?)', (carid[0], userid[0], description, typeinc, time, "Active"))
                    connection.commit()
                    return redirect(url_for('home'))
        else:
            # the car does not exist but cus exist
            if cusid:
                cursor.execute('INSERT INTO Car(LicensePlate, CustomerID) VALUES(?, ?)', (licenseplate, cusid[0]))
                newcarID = cursor.execute('SELECT TOP 1 CarID FROM Car ORDER BY CarID DESC')
                newcarID = cursor.fetchone()
                cursor.execute('INSERT INTO Incident(CarID, UserID, Description, Type, StartTimestamp, Status) VALUES (?, ?, ?, ?, ?, ?)', (newcarID[0], userid[0], description, typeinc, time, "Active"))
                connection.commit()
                return redirect(url_for('home'))
            else:
                # car and cus not exist
                # if the name was not input
                if fname == None:
                    cursor.execute('INSERT INTO Customer(FirstName, LastName) VALUES ("", "")')
                    customerID = cursor.execute('SELECT TOP 1 CustomerID FROM Customer ORDER BY CustomerID DESC')
                    customerID = cursor.fetchone()
                    cursor.execute('INSERT INTO Car(LicensePlate, CustomerID) VALUES (?,?)', (licenseplate,customerID[0]))
                    newcarID = cursor.execute('SELECT TOP 1 CarID FROM Car ORDER BY CarID DESC')
                    newcarID = cursor.fetchone()
                    cursor.execute('INSERT INTO Incident(CarID, UserID, Description, Type, StartTimestamp, Status) VALUES (?, ?, ?, ?, ?, ?)', (newcarID[0], userid[0], description, typeinc, time, "Active"))
                    connection.commit()
                    return redirect(url_for('home'))
                # the name input
                else:
                    cursor.execute('INSERT INTO Customer(FirstName, LastName) VALUES (?,?)', (fname, lname))
                    customerID = cursor.execute('SELECT TOP 1 CustomerID FROM Customer ORDER BY CustomerID DESC')
                    customerID = cursor.fetchone()
                    cursor.execute('INSERT INTO Car(LicensePlate, CustomerID) VALUES (?,?)', (licenseplate,customerID[0]))
                    newcarID = cursor.execute('SELECT TOP 1 CarID FROM Car ORDER BY CarID DESC')
                    newcarID = cursor.fetchone()
                    cursor.execute('INSERT INTO Incident(CarID, UserID, Description, Type, StartTimestamp, Status) VALUES (?, ?, ?, ?, ?, ?)', (newcarID[0], userid[0], description, typeinc, time, "Active"))
                    connection.commit()
                    return redirect(url_for('home'))
        connection.commit()
        return redirect(url_for('home'))


@app.route('/editcar',methods=['POST','GET'])
def editCar():
    if request.method == 'POST':
        carID = request.form['carid']
        licenseplate = request.form['licenseplateeditcar']
        fname = request.form['cusfirstnameeditcar']
        lname = request.form['cuslastnameeditcar']
        phone = request.form['phoneeditcar']
        
        cusid = cursor.execute('SELECT Car.CustomerID From Car WHERE CarID = ?', (carID))
        cusid = cursor.fetchone()
        cursor.execute('UPDATE Customer SET FirstName = ?, LastName = ?, Phone = ? WHERE CustomerID = ?', (fname, lname, phone, cusid[0]))
        cursor.execute('UPDATE Car SET LicensePlate = ? WHERE CarID = ?', (licenseplate, carID))
        connection.commit()
        return redirect(url_for('home'))






