from flask import Flask, render_template, redirect, url_for, request, session
import pyodbc
import datetime
from flask_socketio import SocketIO

connection = pyodbc.connect('Driver={SQL Server};'
                            'Server=.;'
                            'Database=IncidentRecord;'
                            'Trusted_Connection=yes;')
cursor = connection.cursor()

app = Flask(__name__, static_folder='static')
app.secret_key = '123456789'
socketio = SocketIO(app)
enImage = ''
enLicense = ''
enTime = ''
exImage = ''
exLicense = ''
exTime = ''


@socketio.on('connect', namespace='/userhome')
def connect_web():
    print('[INFO] userhome client connected: {}'.format(request.sid))


@socketio.on('disconnect', namespace='/userhome')
def disconnect_web():
    print('[INFO] userhome client disconnected: {}'.format(request.sid))


@socketio.on('connect', namespace='/home')
def connect_web():
    print('[INFO] home client connected: {}'.format(request.sid))


@socketio.on('disconnect', namespace='/home')
def disconnect_web():
    print('[INFO] home client disconnected: {}'.format(request.sid))


@socketio.on('connect', namespace='/enter')
def connect_cv():
    print('[INFO] Enter client connected: {}'.format(request.sid))


@socketio.on('disconnect', namespace='/enter')
def disconnect_cv():
    print('[INFO] Enter client disconnected: {}'.format(request.sid))


@socketio.on('connect', namespace='/exit')
def connect_cv():
    print('[INFO] Exit client connected: {}'.format(request.sid))


@socketio.on('disconnect', namespace='/exit')
def disconnect_cv():
    print('[INFO] Exit client disconnected: {}'.format(request.sid))


@socketio.on('enter2server', namespace='/enter')
def handle_cv_message(message):
    global enImage, enLicense, enTime
    enImage = message['enterimage']
    enLicense = message['enterlicense']
    enTime = message['entertime']
    print(enLicense)

    socketio.emit('server2web_user_enter', {
        'enterimage': enImage,
        'enterlicense': enLicense,
        'entertime': enTime
    },
                  namespace='/userhome')

    socketio.emit('server2web_home_enter', {
        'enterimage': enImage,
        'enterlicense': enLicense,
        'entertime': enTime
    },
                  namespace='/home')


@socketio.on('exit2server', namespace='/exit')
def handle_cv_message(message):
    global exImage, exLicense, exTime
    exImage = message['exitimage']
    exLicense = message['exitlicense']
    exTime = message['exittime']
    print(exLicense)

    socketio.emit('server2web_user_exit', {
        'exitimage': exImage,
        'exitlicense': exLicense,
        'exittime': exTime
    },
                  namespace='/userhome')

    socketio.emit('server2web_home_exit', {
        'exitimage': exImage,
        'exitlicense': exLicense,
        'exittime': exTime
    },
                  namespace='/home')


@app.route('/')
def home():
    if not session.get('loggedin'):
        return render_template('login.html')

    historyData = cursor.execute(
        'SELECT H.HistoryID, C.LicensePlate, H.EnterTimestamp, H.ExitTimestamp, H.Activity FROM History H JOIN Car C ON H.CarID = C.CarID ORDER BY H.HistoryID DESC'
    )
    historyData = cursor.fetchall()

    incidentData = cursor.execute(
        'SELECT I.IncidentID, C.LicensePlate, CUS.FirstName, CUS.LastName, I.Type, I.StartTimestamp, I.EndTimestamp, I.Status, U.FirstName, U.LastName, I.Description FROM Incident I JOIN Car C ON I.CarID = C.CarID JOIN Customer CUS ON C.CustomerID = CUS.CustomerID JOIN [User] U ON U.UserID = I.UserID'
    )
    incidentData = cursor.fetchall()

    carData = cursor.execute(
        'SELECT C.CarID, C.LicensePlate, Customer.FirstName, Customer.LastName, Customer.Phone, MAX(H.EnterTimestamp) FROM History H JOIN Car C ON H.CarID = C.CarID JOIN Customer ON C.CustomerID = Customer.CustomerID GROUP BY C.LicensePlate, C.CarID, C.CustomerID, Customer.FirstName, Customer.LastName, Customer.Phone'
    )
    carData = cursor.fetchall()

    if (session.get('type') != "admin"):
        return render_template('userHome.html',
                               historyData=historyData,
                               incidentData=incidentData,
                               carData=carData,
                               EnterImage=enImage,
                               EnterLicensePlate=enLicense,
                               EnterTime=enTime,
                               ExitImage=exImage,
                               ExitLicensePlate=exLicense,
                               ExitTime=exTime)

    return render_template('home.html',
                           historyData=historyData,
                           incidentData=incidentData,
                           carData=carData,
                           EnterImage=enImage,
                           EnterLicensePlate=enLicense,
                           EnterTime=enTime,
                           ExitImage=exImage,
                           ExitLicensePlate=exLicense,
                           ExitTime=exTime)


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def do_login():
    error = ""
    username = request.form['username']
    password = request.form['password']

    account = cursor.execute(
        'SELECT * FROM [User] WHERE userName = ? AND password = ?',
        (username, password))
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


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['loggedin'] = False
    return home()


@app.route('/addactivity', methods=['POST', 'GET'])
def addActivity():
    if request.method == 'POST':
        historyID = request.form['hisid']
        licenseplate = request.form['licenseplateaddact']
        EnterTime = request.form['entertimeaddact']
        ExitTime = request.form['exittimeaddact']
        activity = request.form['activityaddact']

        cursor.execute('UPDATE History SET Activity = ? WHERE HistoryID = ?',
                       (activity, historyID))
        connection.commit()
        return redirect(url_for('home'))


@app.route('/addincidentfromhistory', methods=['POST', 'GET'])
def addIncidentFromHistory():
    if request.method == 'POST':
        licenseplate = request.form['licenseplateaddincfromhis']
        fname = request.form['cusfirstnameaddincfromhis']
        lname = request.form['cuslastnameaddincfromhis']
        typeinc = request.form['typeaddincfromhis']
        description = request.form['descriptionaddincfromhis']

        carid = cursor.execute('SELECT CarID FROM Car WHERE LicensePlate = ? ',
                               (licenseplate))
        carid = cursor.fetchone()
        userid = cursor.execute(
            "SELECT UserID From [User] WHERE [User].FirstName = ? AND [User].LastName = ?",
            (session['firstname'], session['lastname']))
        userid = cursor.fetchone()
        cusid = cursor.execute(
            'SELECT CustomerID From Customer WHERE FirstName = ? AND LastName = ?',
            (fname, lname))
        cusid = cursor.fetchone()
        incid = cursor.execute(
            'SELECT IncidentID From Incident WHERE CarID = ? AND Status = ?',
            (carid[0], 'Active'))
        incid = cursor.fetchone()
        time = datetime.datetime.now()
        time = time.strftime("%Y-%m-%d %H:%M:%S")

        if incid:
            cursor.execute(
                'UPDATE Incident SET EndTimeStamp = ?, Status = ? WHERE IncidentID = ?',
                (time, 'Inactive', incid[0]))
            connection.commit()
            return redirect(url_for('home'))

        if cusid:
            cursor.execute(
                'INSERT INTO Incident(CarID, UserID, Description, Type, StartTimestamp, Status) VALUES (?, ?, ?, ?, ?, ?)',
                (carid[0], userid[0], description, typeinc, time, "Active"))
            connection.commit()
            return redirect(url_for('home'))
        else:
            # ถ้าไม่มี customer name อยู่ใน customer db ให้เอา cus id ที่เชื่อมกับ car id มาอัพเดทชื่อเอา
            cusidnew = cursor.execute(
                'SELECT CustomerID From Car WHERE CarID = ?', (carid[0]))
            cusidnew = cursor.fetchone()
            cursor.execute(
                'UPDATE Customer SET FirstName = ?, LastName = ? WHERE CustomerID = ?',
                (fname, lname, cusidnew[0]))
            cursor.execute(
                'INSERT INTO Incident(CarID, UserID, Description, Type, StartTimestamp, Status) VALUES (?, ?, ?, ?, ?, ?)',
                (carid[0], userid[0], description, typeinc, time, "Active"))

        connection.commit()
        return redirect(url_for('home'))


@app.route('/editincident', methods=['POST', 'GET'])
def editIncident():
    if request.method == 'POST':
        incidentID = request.form['incid']
        licenseplate = request.form['licenseplateeditinc']
        fname = request.form['cusfirstnameeditinc']
        lname = request.form['cuslastnameeditinc']
        typeinc = request.form['typeeditinc']
        description = request.form['descriptioneditinc']

        carid = cursor.execute(
            'SELECT CarID FROM Car WHERE Car.LicensePlate = ? ',
            (licenseplate))
        carid = cursor.fetchone()
        userid = cursor.execute(
            "SELECT UserID From [User] WHERE [User].FirstName = ? AND [User].LastName = ?",
            (session['firstname'], session['lastname']))
        userid = cursor.fetchone()
        cusid = cursor.execute(
            'SELECT CustomerID From Customer WHERE FirstName = ? AND LastName = ?',
            (fname, lname))
        cusid = cursor.fetchone()

        if carid:
            if cusid:
                cursor.execute('UPDATE Car SET CustomerID = ? WHERE CarID = ?',
                               (cusid[0], carid[0]))
                cursor.execute(
                    'UPDATE Incident SET CarID = ?, UserID = ?, Type = ?, Description = ? WHERE IncidentID = ?',
                    (carid[0], userid[0], typeinc, description, incidentID))
                connection.commit()
                return redirect(url_for('home'))
            else:
                # if the name was not input
                if fname == None:
                    cursor.execute(
                        'INSERT INTO Customer(FirstName, LastName) VALUES ("", "")'
                    )
                    connection.commit()
                    customerID = cursor.execute(
                        'SELECT TOP 1 CustomerID FROM Customer ORDER BY CustomerID DESC'
                    )
                    customerID = cursor.fetchone()
                    cursor.execute(
                        'UPDATE Car SET CustomerID = ? WHERE CarID = ?',
                        (customerID[0], carid[0]))
                    cursor.execute(
                        'UPDATE Incident SET CarID = ?, UserID = ?, Type = ?, Description = ? WHERE IncidentID = ?',
                        (carid[0], userid[0], typeinc, description,
                         incidentID))
                    connection.commit()
                    return redirect(url_for('home'))
                # the name input
                else:
                    cursor.execute(
                        'INSERT INTO Customer(FirstName, LastName) VALUES (?,?)',
                        (fname, lname))
                    customerID = cursor.execute(
                        'SELECT TOP 1 CustomerID FROM Customer ORDER BY CustomerID DESC'
                    )
                    customerID = cursor.fetchone()
                    cursor.execute(
                        'UPDATE Car SET CustomerID = ? WHERE CarID = ?',
                        (customerID[0], carid[0]))
                    cursor.execute(
                        'UPDATE Incident SET CarID = ?, UserID = ?, Type = ?, Description = ? WHERE IncidentID = ?',
                        (carid[0], userid[0], typeinc, description,
                         incidentID))
                    connection.commit()
                    return redirect(url_for('home'))
        else:
            # the car does not exist but cus exist
            if cusid:
                cursor.execute(
                    'INSERT INTO Car(LicensePlate, CustomerID) VALUES(?, ?)',
                    (licenseplate, cusid[0]))
                newcarID = cursor.execute(
                    'SELECT TOP 1 CarID FROM Car ORDER BY CarID DESC')
                newcarID = cursor.fetchone()
                cursor.execute(
                    'UPDATE Incident SET CarID = ?, UserID = ?, Type = ?, Description = ? WHERE IncidentID = ?',
                    (newcarID[0], userid[0], typeinc, description, incidentID))
                connection.commit()
                return redirect(url_for('home'))
            else:
                # car and cus not exist
                # if the name was not input
                if fname == None:
                    cursor.execute(
                        'INSERT INTO Customer(FirstName, LastName) VALUES ("", "")'
                    )
                    customerID = cursor.execute(
                        'SELECT TOP 1 CustomerID FROM Customer ORDER BY CustomerID DESC'
                    )
                    customerID = cursor.fetchone()
                    cursor.execute(
                        'INSERT INTO Car(LicensePlate, CustomerID) VALUES (?,?)',
                        (licenseplate, customerID[0]))
                    newcarID = cursor.execute(
                        'SELECT TOP 1 CarID FROM Car ORDER BY CarID DESC')
                    newcarID = cursor.fetchone()
                    cursor.execute(
                        'UPDATE Incident SET CarID = ?, UserID = ?, Type = ?, Description = ? WHERE IncidentID = ?',
                        (newcarID[0], userid[0], typeinc, description,
                         incidentID))
                    connection.commit()
                    return redirect(url_for('home'))
                # the name input
                else:
                    cursor.execute(
                        'INSERT INTO Customer(FirstName, LastName) VALUES (?,?)',
                        (fname, lname))
                    customerID = cursor.execute(
                        'SELECT TOP 1 CustomerID FROM Customer ORDER BY CustomerID DESC'
                    )
                    customerID = cursor.fetchone()
                    cursor.execute(
                        'INSERT INTO Car(LicensePlate, CustomerID) VALUES (?,?)',
                        (licenseplate, customerID[0]))
                    newcarID = cursor.execute(
                        'SELECT TOP 1 CarID FROM Car ORDER BY CarID DESC')
                    newcarID = cursor.fetchone()
                    cursor.execute(
                        'UPDATE Incident SET CarID = ?, UserID = ?, Type = ?, Description = ? WHERE IncidentID = ?',
                        (newcarID[0], userid[0], typeinc, description,
                         incidentID))
                    connection.commit()
                    return redirect(url_for('home'))

        cursor.execute(
            'UPDATE Incident SET CarID = ?, UserID = ?, Type = ?, Description = ? WHERE IncidentID = ?',
            (carid[0], userid[0], typeinc, description, incidentID))
        connection.commit()
        return redirect(url_for('home'))


@app.route('/deactivate', methods=['POST'])
def deactivate():
    if request.method == 'POST':
        incidentID = request.form['incid']
        time = datetime.datetime.now()
        time = time.strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "UPDATE Incident SET EndTimeStamp = ?, Status = ? WHERE IncidentID = ?",
            (time, "Inactive", incidentID))
        connection.commit()
        return home()


@app.route('/addincident', methods=['POST'])
def addIncident():
    if request.method == "POST":
        licenseplate = request.form['licenseplateaddinc']
        fname = request.form['cusfirstnameaddinc']
        lname = request.form['cuslastnameaddinc']
        typeinc = request.form['typeaddinc']
        description = request.form['descriptionaddinc']

        carid = cursor.execute('SELECT CarID FROM Car WHERE LicensePlate = ? ',
                               (licenseplate))
        carid = cursor.fetchone()
        cusid = cursor.execute(
            "SELECT CustomerID From Customer WHERE FirstName = ? AND LastName = ?",
            (fname, lname))
        cusid = cursor.fetchone()
        userid = cursor.execute(
            "SELECT UserID From [User] WHERE [User].FirstName = ? AND [User].LastName = ?",
            (session['firstname'], session['lastname']))
        userid = cursor.fetchone()
        time = datetime.datetime.now()
        time = time.strftime("%Y-%m-%d %H:%M:%S")

        # if the licenseplate existing
        if carid:
            # if the license plate already have incident, then it will deactivate the old one
            incid = cursor.execute(
                'SELECT IncidentID From Incident WHERE CarID = ? AND Status = ?',
                (carid[0], 'Active'))
            incid = cursor.fetchone()
            if incid:
                cursor.execute(
                    'UPDATE Incident SET EndTimeStamp = ?, Status = ? WHERE IncidentID = ?',
                    (time, 'Inactive', incid[0]))
                connection.commit()
            # if the licenseplate exist then customer also exist, then update the customerid
            if cusid:
                cursor.execute('UPDATE Car SET CustomerID = ? WHERE CarID = ?',
                               (cusid, carid))
                cursor.execute(
                    "INSERT INTO Incident(CarID, UserID, Description, Type, StartTimestamp, Status) VALUES (?, ?, ?, ?, ?, ?)",
                    (carid[0], userid[0], description, typeinc, time,
                     "Active"))
                connection.commit()
                return redirect(url_for('home'))
            else:
                # if the name was not input
                if fname == None:
                    cursor.execute(
                        'INSERT INTO Customer(FirstName, LastName) VALUES ("", "")'
                    )
                    connection.commit()
                    customerID = cursor.execute(
                        'SELECT TOP 1 CustomerID FROM Customer ORDER BY CustomerID DESC'
                    )
                    customerID = cursor.fetchone()
                    cursor.execute(
                        'UPDATE Car SET CustomerID = ? WHERE CarID = ?',
                        (customerID[0], carid[0]))
                    cursor.execute(
                        'INSERT INTO Incident(CarID, UserID, Description, Type, StartTimestamp, Status) VALUES (?, ?, ?, ?, ?, ?)',
                        (carid[0], userid[0], description, typeinc, time,
                         "Active"))
                    connection.commit()
                    return redirect(url_for('home'))
                # the name input
                else:
                    cursor.execute(
                        'INSERT INTO Customer(FirstName, LastName) VALUES (?,?)',
                        (fname, lname))
                    cursor.execute(
                        'UPDATE Car SET CustomerID = ? WHERE CarID = ?',
                        (customerID[0], carid[0]))
                    cursor.execute(
                        'INSERT INTO Incident(CarID, UserID, Description, Type, StartTimestamp, Status) VALUES (?, ?, ?, ?, ?, ?)',
                        (carid[0], userid[0], description, typeinc, time,
                         "Active"))
                    connection.commit()
                    return redirect(url_for('home'))
        else:
            # the car does not exist but cus exist
            if cusid:
                cursor.execute(
                    'INSERT INTO Car(LicensePlate, CustomerID) VALUES(?, ?)',
                    (licenseplate, cusid[0]))
                newcarID = cursor.execute(
                    'SELECT TOP 1 CarID FROM Car ORDER BY CarID DESC')
                newcarID = cursor.fetchone()
                cursor.execute(
                    'INSERT INTO Incident(CarID, UserID, Description, Type, StartTimestamp, Status) VALUES (?, ?, ?, ?, ?, ?)',
                    (newcarID[0], userid[0], description, typeinc, time,
                     "Active"))
                connection.commit()
                return redirect(url_for('home'))
            else:
                # car and cus not exist
                # if the name was not input
                if fname == None:
                    cursor.execute(
                        'INSERT INTO Customer(FirstName, LastName) VALUES ("", "")'
                    )
                    customerID = cursor.execute(
                        'SELECT TOP 1 CustomerID FROM Customer ORDER BY CustomerID DESC'
                    )
                    customerID = cursor.fetchone()
                    cursor.execute(
                        'INSERT INTO Car(LicensePlate, CustomerID) VALUES (?,?)',
                        (licenseplate, customerID[0]))
                    newcarID = cursor.execute(
                        'SELECT TOP 1 CarID FROM Car ORDER BY CarID DESC')
                    newcarID = cursor.fetchone()
                    cursor.execute(
                        'INSERT INTO Incident(CarID, UserID, Description, Type, StartTimestamp, Status) VALUES (?, ?, ?, ?, ?, ?)',
                        (newcarID[0], userid[0], description, typeinc, time,
                         "Active"))
                    connection.commit()
                    return redirect(url_for('home'))
                # the name input
                else:
                    cursor.execute(
                        'INSERT INTO Customer(FirstName, LastName) VALUES (?,?)',
                        (fname, lname))
                    customerID = cursor.execute(
                        'SELECT TOP 1 CustomerID FROM Customer ORDER BY CustomerID DESC'
                    )
                    customerID = cursor.fetchone()
                    cursor.execute(
                        'INSERT INTO Car(LicensePlate, CustomerID) VALUES (?,?)',
                        (licenseplate, customerID[0]))
                    newcarID = cursor.execute(
                        'SELECT TOP 1 CarID FROM Car ORDER BY CarID DESC')
                    newcarID = cursor.fetchone()
                    cursor.execute(
                        'INSERT INTO Incident(CarID, UserID, Description, Type, StartTimestamp, Status) VALUES (?, ?, ?, ?, ?, ?)',
                        (newcarID[0], userid[0], description, typeinc, time,
                         "Active"))
                    connection.commit()
                    return redirect(url_for('home'))
        connection.commit()
        return redirect(url_for('home'))


@app.route('/editcar', methods=['POST', 'GET'])
def editCar():
    if request.method == 'POST':
        carID = request.form['carid']
        licenseplate = request.form['licenseplateeditcar']
        fname = request.form['cusfirstnameeditcar']
        lname = request.form['cuslastnameeditcar']
        phone = request.form['phoneeditcar']

        cusid = cursor.execute(
            'SELECT Car.CustomerID From Car WHERE CarID = ?', (carID))
        cusid = cursor.fetchone()
        cursor.execute(
            'UPDATE Customer SET FirstName = ?, LastName = ?, Phone = ? WHERE CustomerID = ?',
            (fname, lname, phone, cusid[0]))
        cursor.execute('UPDATE Car SET LicensePlate = ? WHERE CarID = ?',
                       (licenseplate, carID))
        connection.commit()
        return redirect(url_for('home'))


if __name__ == '__main__':
    socketio.run(app=app, host='127.0.0.1', port=5000)
