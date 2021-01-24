from flask import Flask, render_template, redirect, url_for, request
import cv2
import pyodbc

def execute_sql(query):
    connection = pyodbc.connect('Driver={SQL Server};'
                      'Server=.;'
                      'Database=IncidentRecord;'
                      'Trusted_Connection=yes;')

    cursor = connection.cursor()
    cursor.execute(query)

    return cursor.fetchall()

def execute_sql_parameter(query, user, psw):
    connection = pyodbc.connect('Driver={SQL Server};'
                      'Server=.;'
                      'Database=IncidentRecord;'
                      'Trusted_Connection=yes;')

    cursor = connection.cursor()
    cursor.execute(query, user, psw)

    return cursor.fetchall()


app = Flask(__name__, static_folder='static')


@app.route('/login', methods=['POST'])
def login():
    error = None
    if request.method == 'POST':
        user = request.form['username']
        psw = request.form['password']

        userInfo = execute_sql_parameter('SELECT UserName, Password, UserType FROM [User] WHERE UserName = ? AND Password = ?' , user, psw)
        # trysql = execute_sql('SELECT UserName, Password, UserType FROM [User] WHERE UserName = ?', user)

        for i in userInfo:
            userName = i[0]
            userPassword = i[1]
            userType = i[2]

        if user != userName or psw != userPassword:
            error = 'Invalid Username or password. Please try again.'
        elif userType == 'Admin':
            return redirect(url_for('home'))
        else :
            return redirect(url_for('user'))

    return render_template('login.html', error=error)

        # user = cursor.execute('SELECT * FROM [User] WHERE UserName = %s AND Password = %s', username, password)
        # print(user)



        # # If account exists in accounts table in out database
        # if account:
        #     # Create session data, we can access this data in other routes
        #     session['loggedin'] = True
        #     session['id'] = account['id']
        #     session['username'] = account['username']

        #     # Redirect to home page
        #     return 'Logged in successfully!'
        # else:
        #     # Account doesnt exist or username/password incorrect
        #     msg = 'Incorrect username/password!'

@app.route('/blacklist')
def blacklist():
    return render_template('blacklist.html')

@app.route('/user')
def user():
    return render_template('userHome.html')


@app.route('/')
def home():
    historyData = execute_sql('Select H.HistoryID, C.LicensePlate, H.EnterTimestamp, H.ExitTimestamp, H.Activity FROM History H JOIN Car C ON H.CarID = C.CarID')
    incidentData = execute_sql('Select I.IncidentID, C.LicensePlate, CUS.FirstName, CUS.LastName, I.Type, I.StartTimestamp, I.EndTimestamp, I.Status, U.FirstName, U.LastName, I.Description FROM Incident I JOIN Car C ON I.CarID = C.CarID JOIN Customer CUS ON C.CustomerID = CUS.CustomerID JOIN [User] U ON U.UserID = I.UserID')
    carData = execute_sql('Select C.CarID, C.LicensePlate, CUS.FirstName, CUS.LastName, CUS.Phone, H.EnterTimestamp, I.Type FROM Car C JOIN Customer CUS ON C.CustomerID = CUS.CustomerID JOIN Incident I ON C.CarID = I.CarID JOIN History H ON C.CarID = H.CarID')
    
    return render_template('home.html', historyData = historyData, incidentData = incidentData, carData = carData)


@app.route('/login', methods=['GET', 'POST'])
def logout():
    return render_template('login.html')