from flask import Flask, render_template, redirect, url_for, request, session
import cv2
import pyodbc

connection = pyodbc.connect('Driver={SQL Server};'
                    'Server=.;'
                    'Database=IncidentRecord;'
                    'Trusted_Connection=yes;')
cursor = connection.cursor()


app = Flask(__name__, static_folder='static')
app.secret_key = '123456789'


@app.route('/login', methods=['POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        account = cursor.execute('SELECT * FROM [User] WHERE userName = ? AND password = ?', (username, password))
        account = cursor.fetchone()

        if account:
            session['loggedin'] = True
            session['userName'] = account[1]
            session['password'] = account[2]
            print(session['userName'])
            if(account[5] == 'Admin'):
                return redirect(url_for('home'))
            else:
                return redirect(url_for('user'))
        else:
            error = 'Incorrect username or password!'
        return render_template('login.html', error=error)

@app.route('/blacklist')
def blacklist():
    return render_template('blacklist.html')

@app.route('/user')
def user():
    return render_template('userHome.html')


@app.route('/')
def home():
    historyData = cursor.execute('Select H.HistoryID, C.LicensePlate, H.EnterTimestamp, H.ExitTimestamp, H.Activity FROM History H JOIN Car C ON H.CarID = C.CarID')
    historyData = cursor.fetchall()
    incidentData = cursor.execute('Select I.IncidentID, C.LicensePlate, CUS.FirstName, CUS.LastName, I.Type, I.StartTimestamp, I.EndTimestamp, I.Status, U.FirstName, U.LastName, I.Description FROM Incident I JOIN Car C ON I.CarID = C.CarID JOIN Customer CUS ON C.CustomerID = CUS.CustomerID JOIN [User] U ON U.UserID = I.UserID')
    incidentData = cursor.fetchall()
    carData = cursor.execute('Select C.CarID, C.LicensePlate, CUS.FirstName, CUS.LastName, CUS.Phone, H.EnterTimestamp, I.Type FROM Car C JOIN Customer CUS ON C.CustomerID = CUS.CustomerID JOIN Incident I ON C.CarID = I.CarID JOIN History H ON C.CarID = H.CarID')
    carData = cursor.fetchall()
    return render_template('home.html', historyData = historyData, incidentData = incidentData, carData = carData)


@app.route('/login', methods=['GET', 'POST'])
def logout():
    return render_template('login.html')