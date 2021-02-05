from flask import Flask, render_template, redirect, url_for, request, session, Response
import cv2
import pyodbc
import numpy as np
import imutils
import pytesseract
import datetime
import threading
from imutils.video import VideoStream


connection = pyodbc.connect('Driver={SQL Server};'
                            'Server=.;'
                            'Database=IncidentRecord;'
                            'Trusted_Connection=yes;')
cursor = connection.cursor()

app = Flask(__name__, static_folder='static')

app.secret_key = '123456789'

EnterTime = '2021-01-10 18:25:55'
ExitTime = '2021-01-10 18:25:55'
EnterLicensePlate = '5กศ8444'
ExitLicensePlate = 'ขอ5025'

outputFrame = None
lock = threading.Lock()
stream = VideoStream('static/sidevid.mp4').start()

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
    carDate = cursor.execute('SELECT C.CarID, C.LicensePlate, Customer.FirstName, Customer.LastName, Customer.Phone, MAX(H.EnterTimestamp) FROM History H JOIN Car C ON H.CarID = C.CarID JOIN Customer ON C.CustomerID = Customer.CustomerID Group By C.LicensePlate, C.CarID, C.CustomerID, Customer.FirstName, Customer.LastName, Customer.Phone')
    carData = cursor.fetchall()
    
   

    if(session.get('type') != "admin"):
        return render_template('userHome.html', historyData=historyData, incidentData=incidentData, carData=carData, EnterLicensePlate=EnterLicensePlate, EnterTime=EnterTime, ExitLicensePlate=ExitLicensePlate, ExitTime=ExitTime)
    
    return render_template('home.html', historyData=historyData, incidentData=incidentData, carData=carData, EnterLicensePlate=EnterLicensePlate, EnterTime=EnterTime, ExitLicensePlate=ExitLicensePlate, ExitTime=ExitTime)


@app.route('/logout', methods=['GET','POST'])
def logout():
    session['loggedin'] = False
    return home()


def order_points(pts):
	rect = np.zeros((4, 2), dtype="float32")
	s = pts.sum(axis=1)
	rect[0] = pts[np.argmin(s)]
	rect[2] = pts[np.argmax(s)]
	diff = np.diff(pts, axis=1)
	rect[1] = pts[np.argmin(diff)]
	rect[3] = pts[np.argmax(diff)]
	return rect


def four_point_transform(image, pts):
	rect = order_points(pts)
	(tl, tr, br, bl) = rect
	widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
	widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
	maxWidth = max(int(widthA), int(widthB))
	heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
	heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
	maxHeight = max(int(heightA), int(heightB))
	dst = np.array([
		[0, 0],
		[maxWidth - 1, 0],
		[maxWidth - 1, maxHeight - 1],
		[0, maxHeight - 1]], dtype="float32")
	M = cv2.getPerspectiveTransform(rect, dst)
	warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
	return warped


def most_frequent(List):
    List = list(filter(None, List))
    if List != []:
        return max(set(List), key=List.count)
    else:
        return "None"

def detectEnterLicensePlate():
    # Using array instead of connect to the database
    licensePlateData = getLicensePlates()

    # step1 arduino side send video stream on rtsp
    # step2 read video strean from arduino rtsp
    
    # stream = cv2.VideoCapture('carGate.mp4')
    global stream, outputFrame, lock
    licenseText = '-'
    time = ''
    temp = '-'
    digitsocr = []

    while True:
        # step3 capture image when detect license plate
        r, img = stream.read()
        ratio = img.shape[0] / 600.0
        orig = img.copy()
        img = imutils.resize(img, height=600)

        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blur, 30, 200)
        contours = cv2.findContours(
        edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

        for c in contours:

            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.01 * peri, True)

            if len(approx) == 4:
                screenCnt = approx

                # cv2.imshow("License Detected : ", license_img)
                cv2.drawContours(img, [screenCnt], -1, (0, 255, 255), 3)
                warped = four_point_transform(orig, screenCnt.reshape(4, 2) * ratio)
                # warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
                warped = imutils.resize(warped, height=100)
                license_img = warped
               
                # cv2.imshow("License Detected : ", license_img)

                custom_config = r'-l tha -c tessedit_char_whitelist= 0123456789กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรลวศษสหฬอฮ --psm 6'

                ocr_result=pytesseract.image_to_string(license_img, config=custom_config + 'Thai' + 'Thaiitalic'+'tha.psl.bold.italic'+'psl-bold')
                res=(ocr_result.strip())[0:10]

                res=res.translate(
                    {ord(i): None for i in '|-=+[]\n(*)%|"{<>}/?!.«,;: “๐abcdefghijklmnopqrstuvwxyz/ุ๑๒๓๔ู฿๕๖๗๘๙"ๆ้ไำะัโเ๊ีาิแ์ื'})
                if len(res) in range(4, 8):
                    digitsocr.append(res)
                    freq=most_frequent(digitsocr)
                    temp=freq
        
        with lock:
            outputFrame = img.copy

    #     cv2.imshow('IP Camera stream', img)
        
        if licenseText != temp:
            licenseText=temp
            print("License Plate is " + licenseText)
            # Step5 use for loop to compare value in the array licensePlateData
            addEnterHistory(licenseText)
           
    #     if cv2.waitKey(1) & 0xFF == ord('q'):
    #         break

    # cv2.destroyAllWindows()


def getLicensePlates():
    licensePlates = cursor.execute('SELECT LicensePlate FROM Car')
    licensePlates = cursor.fetchall()
    return licensePlates


def getCarID(licensePlate):
    carID = cursor.execute('SELECT C.CarID FROM Car C WHERE C.LicensePlate = ?', licensePlate)
    carID = cursor.fetchone()
    return carID[0]


def addEnterHistory(licensePlate):
    found = False
    enterTime = datetime.datetime.now()
    enterTime = enterTime.strftime("%Y-%m-%d %H:%M:%S")
    licensePlates = getLicensePlates()

    global EnterLicensePlate, EnterTime
    EnterLicensePlate = licensePlate
    EnterTime = enterTime
    

    for i in licensePlates:
        if licensePlate == i[0]:
            found = True
            break
    
    if found == True:
        carID = cursor.execute('SELECT C.CarID FROM Car C WHERE C.LicensePlate = ?', licensePlate)
        carID = cursor.fetchone()
        cursor.execute('INSERT INTO History (CarID, EnterTimestamp) VALUES (?,?)', (carID[0], enterTime))
        cursor.commit()
        return True

    cursor.execute('INSERT INTO Customer(FirstName) VALUES (?)', (""))
    cursor.commit()
    customerID = cursor.execute('SELECT TOP 1 CustomerID FROM Customer ORDER BY CustomerID DESC')
    customerID = cursor.fetchone()
    cursor.execute('INSERT INTO Car(CustomerID, LicensePlate) VALUES (?,?)', (customerID[0], licensePlate))
    cursor.commit()
    carID = cursor.execute('SELECT C.CarID FROM Car C WHERE C.LicensePlate = ?', licensePlate)
    carID = cursor.fetchone()
    cursor.execute('INSERT INTO History (CarID, EnterTimestamp) VALUES (?,?)', (carID[0], enterTime))
    cursor.commit()
    return True


def generate():
	# grab global references to the output frame and lock variables
	global outputFrame, lock
	# loop over frames from the output stream
	while True:
		# wait until the lock is acquired
		with lock:
			# check if the output frame is available, otherwise skip
			# the iteration of the loop
			if outputFrame is None:
				continue
			# encode the frame in JPEG format
			(flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
			# ensure the frame was successfully encoded
			if not flag:
				continue
		# yield the output frame in the byte format
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')

@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	return Response(generate(),mimetype = "multipart/x-mixed-replace; boundary=frame")



stream.stop()