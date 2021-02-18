from flask import Flask, render_template, redirect, url_for, request, session, json
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


@socketio.on('connect', namespace='/web')
def connect_web():
    print('[INFO] web client connected: {}'.format(request.sid))


@socketio.on('disconnect', namespace='/web')
def disconnect_web():
    print('[INFO] web client disconnected: {}'.format(request.sid))


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
    lastEnter = cursor.execute(
        'SELECT TOP 1 H.HistoryID, C.LicensePlate, H.EnterTimestamp, H.ExitTimestamp, H.Activity, CUS.FirstName, CUS.LastName, CUS.Phone FROM History H JOIN Car C ON H.CarID = C.CarID JOIN Customer CUS ON C.CarID = CUS.CarID ORDER BY H.HistoryID DESC'
    )
    lastEnter = cursor.fetchone()

    lastenter_list = []
    lastenter_dict = {
        'id': lastEnter[0],
        'licenseplate': lastEnter[1],
        'entertime': str(lastEnter[2]),
        'exittime': str(lastEnter[3]),
        'activity': str(lastEnter[4])
    }

    lastenter_list.append(lastenter_dict)
    lastenter_json = json.dumps(lastenter_list)
    socketio.emit('server2web_enter', {
        'enterimage': enImage,
        'enterlicense': enLicense,
        'entertime': enTime,
        'lastenter': lastenter_json
    },
                  namespace='/web')


@socketio.on('exit2server', namespace='/exit')
def handle_cv_message(message):
    global exImage, exLicense, exTime
    exImage = message['exitimage']
    exLicense = message['exitlicense']
    exTime = message['exittime']
    lastExit = cursor.execute(
        'SELECT TOP 1 H.HistoryID, H.ExitTimestamp FROM History H JOIN Car C ON H.CarID = C.CarID WHERE H.ExitTimestamp IS NOT NULL ORDER BY H.HistoryID DESC'
    )
    lastExit = cursor.fetchone()

    lastexit_list = []
    lastexit_dict = {'id': lastExit[0], 'exittime': str(lastExit[1])}

    lastexit_list.append(lastexit_dict)
    lastexit_json = json.dumps(lastexit_list)
    socketio.emit('server2web_exit', {
        'exitimage': exImage,
        'exitlicense': exLicense,
        'exittime': exTime,
        'lastexit': lastexit_json
    },
                  namespace='/web')


@app.route('/histable')
def hisTable():
    historyData = cursor.execute(
        'SELECT H.HistoryID, C.LicensePlate, H.EnterTimestamp, H.ExitTimestamp, H.Activity, CUS.FirstName, CUS.LastName, CUS.Phone FROM History H JOIN Car C ON H.CarID = C.CarID JOIN Customer CUS ON C.CarID = CUS.CarID ORDER BY H.HistoryID DESC'
    )
    historyData = cursor.fetchall()

    history_list = []
    history_dict = {}

    for history in historyData:
        history_dict = {
            'id': history[0],
            'licenseplate': str(history[1]),
            'entertime': str(history[2]),
            'exittime': str(history[3]),
            'activity': str(history[4]),
            'firstname': str(history[5]),
            'lastname': str(history[6]),
            'phone': str(history[7])
        }
        history_list.append(history_dict)

    return json.dumps(history_list)


@app.route('/inctable')
def incTable():
    incidentData = cursor.execute(
        'SELECT I.IncidentID, C.LicensePlate, CUS.FirstName, CUS.LastName, I.Type, I.StartTimestamp, I.EndTimestamp, I.Status, U.FirstName, U.LastName, I.Description, CUS.Phone FROM Incident I JOIN Car C ON I.CarID = C.CarID JOIN Customer CUS ON C.CarID = CUS.CarID JOIN [User] U ON U.UserID = I.UserID'
    )
    incidentData = cursor.fetchall()

    incident_list = []
    incident_dict = {}

    for incident in incidentData:
        incident_dict = {
            'id': incident[0],
            'licenseplate': str(incident[1]),
            'firstname': str(incident[2]),
            'lastname': str(incident[3]),
            'type': str(incident[4]),
            'starttime': str(incident[5]),
            'endtime': str(incident[6]),
            'status': str(incident[7]),
            'userfirstname': str(incident[8]),
            'userlastname': str(incident[9]),
            'description': str(incident[10]),
            'phone': str(incident[11])
        }
        incident_list.append(incident_dict)

    return json.dumps(incident_list)


@app.route('/cartable')
def carTable():
    carData = cursor.execute(
        'SELECT C.CarID, C.LicensePlate, CUS.FirstName, CUS.LastName, CUS.Phone, MAX(H.EnterTimestamp) FROM History H RIGHT JOIN Car C ON H.CarID = C.CarID JOIN Customer CUS ON C.CarID = CUS.CarID  GROUP BY C.LicensePlate, C.CarID, CUS.CarID, CUS.FirstName, CUS.LastName, CUS.Phone ORDER BY C.CarID'
    )
    carData = cursor.fetchall()

    car_list = []
    car_dict = {}

    for car in carData:
        car_dict = {
            'id': car[0],
            'licenseplate': str(car[1]),
            'firstname': str(car[2]),
            'lastname': str(car[3]),
            'phone': str(car[4]),
            'lastvisited': str(car[5])
        }
        car_list.append(car_dict)

    return json.dumps(car_list)


@app.route('/')
def home():
    if not session.get('loggedin'):
        return render_template('login.html')

    historyData = hisTable()
    incidentData = incTable()
    carData = carTable()

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


@app.route('/addactivity', methods=['POST'])
def addActivity():
    historyID = request.form['hisid']
    licenseplate = request.form['licenseplateaddact']
    EnterTime = request.form['entertimeaddact']
    ExitTime = request.form['exittimeaddact']
    activity = request.form['activityaddact']

    cursor.execute('UPDATE History SET Activity = ? WHERE HistoryID = ?',
                   (activity, historyID))
    connection.commit()

    activity = cursor.execute(
        'SELECT H.HistoryID, H.Activity FROM History H WHERE HistoryID = ?',
        historyID)
    activity = cursor.fetchone()

    socketio.emit('server2web_addact', {
        'id': activity[0],
        'activity': str(activity[1])
    },
                  namespace='/web')

    return redirect(url_for('home'))


@app.route('/addincidentfromhistory', methods=['POST'])
def addIncidentFromHistory():
    licenseplate = request.form['licenseplateaddincfromhis']
    fname = request.form['cusfirstnameaddincfromhis']
    lname = request.form['cuslastnameaddincfromhis']
    phone = request.form['phoneaddincfromhis']
    typeinc = request.form['typeaddincfromhis']
    description = request.form['descriptionaddincfromhis']

    if lname == "":
        lname = None
    if phone == "":
        phone = None

    carid = cursor.execute('SELECT CarID FROM Car WHERE LicensePlate = ? ',
                           (licenseplate))
    carid = cursor.fetchone()
    cusid = cursor.execute(
        "SELECT CustomerID From Customer CUS WHERE CUS.CarID = ?", (carid[0]))
    cusid = cursor.fetchone()
    userid = cursor.execute(
        "SELECT UserID From [User] WHERE [User].FirstName = ? AND [User].LastName = ?",
        (session['firstname'], session['lastname']))
    userid = cursor.fetchone()
    time = datetime.datetime.now()
    time = time.strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        'UPDATE Customer SET FirstName = ? , LastName = ?, Phone = ? WHERE CustomerID = ?',
        (fname, lname, phone, cusid[0]))
    connection.commit()
    cursor.execute(
        'INSERT INTO Incident(CarID, UserID, Description, Type, StartTimestamp, Status) VALUES (?, ?, ?, ?, ?, ?)',
        (carid[0], userid[0], description, typeinc, time, "Active"))
    connection.commit()

    incident = cursor.execute(
        'SELECT TOP 1 I.IncidentID, C.LicensePlate, CUS.FirstName, CUS.LastName, I.Type, I.StartTimestamp, I.EndTimestamp, I.Status, U.FirstName, U.LastName, I.Description, CUS.Phone FROM Incident I JOIN Car C ON I.CarID = C.CarID JOIN Customer CUS ON C.CarID = CUS.CarID JOIN [User] U ON U.UserID = I.UserID ORDER BY IncidentID DESC'
    )
    incident = cursor.fetchone()

    incident_list = []
    incident_dict = {
        'id': incident[0],
        'licenseplate': str(incident[1]),
        'firstname': str(incident[2]),
        'lastname': str(incident[3]),
        'type': str(incident[4]),
        'starttime': str(incident[5]),
        'endtime': str(incident[6]),
        'status': str(incident[7]),
        'userfirstname': str(incident[8]),
        'userlastname': str(incident[9]),
        'description': str(incident[10]),
        'phone': str(incident[11])
    }

    incident_list.append(incident_dict)
    incident_json = json.dumps(incident_list)

    socketio.emit('server2web_addincfromhis', {'lastincident': incident_json},
                  namespace='/web')

    return redirect(url_for('home'))


@app.route('/editincident', methods=['POST'])
def editIncident():
    incidentID = request.form['ideditinc']
    licenseplate = request.form['licenseplateeditinc']
    fname = request.form['cusfirstnameeditinc']
    lname = request.form['cuslastnameeditinc']
    typeinc = request.form['typeeditinc']
    phone = request.form['phoneeditinc']
    description = request.form['descriptioneditinc']

    if lname == "":
        lname = None
    if phone == "":
        phone = None

    cusid = cursor.execute(
        'SELECT CustomerID From Customer CUS JOIN Car C ON CUS.CarID = C.CarID WHERE C.LicensePlate = ?',
        (licenseplate))
    cusid = cursor.fetchone()

    userid = cursor.execute(
        "SELECT UserID From [User] WHERE [User].FirstName = ? AND [User].LastName = ?",
        (session['firstname'], session['lastname']))
    userid = cursor.fetchone()

    cursor.execute(
        'UPDATE Incident SET UserID = ?, Type = ?, Description = ? WHERE IncidentID = ?',
        (userid[0], typeinc, description, incidentID))
    connection.commit()

    cursor.execute(
        'UPDATE Customer SET FirstName = ?, LastName = ?, Phone = ? WHERE CustomerID = ?',
        (fname, lname, phone, cusid[0]))
    connection.commit()
    return redirect(url_for('home'))


@app.route('/deactivate', methods=['POST'])
def deactivate():
    incidentid = request.form['inciddeact']
    time = datetime.datetime.now()
    time = time.strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "UPDATE Incident SET EndTimeStamp = ?, Status = ? WHERE IncidentID = ?",
        (time, "Inactive", incidentid))
    connection.commit()
    return redirect(url_for('home'))


@app.route('/addincident', methods=['POST'])
def addIncident():
    licenseplate = request.form['licenseplateaddinc']
    fname = request.form['cusfirstnameaddinc']
    lname = request.form['cuslastnameaddinc']
    phone = request.form['phoneaddinc']
    typeinc = request.form['typeaddinc']
    description = request.form['descriptionaddinc']

    if lname == "":
        lname = None
    if phone == "":
        phone = None

    userid = cursor.execute(
        "SELECT UserID From [User] WHERE [User].FirstName = ? AND [User].LastName = ?",
        (session['firstname'], session['lastname']))
    userid = cursor.fetchone()
    time = datetime.datetime.now()
    time = time.strftime("%Y-%m-%d %H:%M:%S")

    carid = cursor.execute('SELECT CarID FROM Car WHERE LicensePlate = ? ',
                           (licenseplate))
    carid = cursor.fetchone()

    if carid:
        cursor.execute(
            'UPDATE Customer SET FirstName = ? , LastName = ?, Phone = ? WHERE CarID = ?',
            (fname, lname, phone, carid[0]))
        cursor.execute(
            'INSERT INTO Incident(CarID, UserID, Description, Type, StartTimestamp, Status) VALUES (?, ?, ?, ?, ?, ?)',
            (carid[0], userid[0], description, typeinc, time, "Active"))
        connection.commit()
        return redirect(url_for('home'))

    cursor.execute('INSERT INTO Car(LicensePlate) VALUES (?)', (licenseplate))
    connection.commit()

    carid = cursor.execute('SELECT CarID FROM Car WHERE LicensePlate = ?',
                           (licenseplate))
    carid = cursor.fetchone()

    cursor.execute(
        'INSERT INTO Customer(FirstName, LastName, Phone, CarID) VALUES (?, ?, ?, ?)',
        (fname, lname, phone, carid[0]))
    connection.commit()

    cursor.execute(
        'INSERT INTO Incident(CarID, UserID, Description, Type, StartTimestamp, Status) VALUES (?, ?, ?, ?, ?, ?)',
        (carid[0], userid[0], description, typeinc, time, "Active"))
    connection.commit()
    return redirect(url_for('home'))


@app.route('/editcar', methods=['POST'])
def editCar():
    carID = request.form['carideditcar']
    licenseplate = request.form['licenseplateeditcar']
    fname = request.form['cusfirstnameeditcar']
    lname = request.form['cuslastnameeditcar']
    phone = request.form['phoneeditcar']

    if phone == "":
        phone = None
    if lname == "":
        lname = None

    cursor.execute(
        'UPDATE Customer SET FirstName = ?, LastName = ?, Phone = ? WHERE CarID = ?',
        (fname, lname, phone, carID))
    cursor.execute('UPDATE Car SET LicensePlate = ? WHERE CarID = ?',
                   (licenseplate, carID))
    connection.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    socketio.run(app=app, host='127.0.0.1', port=5000)
