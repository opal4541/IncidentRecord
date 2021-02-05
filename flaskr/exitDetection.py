from flask import Flask, render_template, redirect, url_for, request, session
import cv2
import pyodbc
import numpy as np
import imutils
import pytesseract
import datetime

connection = pyodbc.connect('Driver={SQL Server};'
                            'Server=.;'
                            'Database=IncidentRecord;'
                            'Trusted_Connection=yes;')
cursor = connection.cursor()

app = Flask(__name__, static_folder='static')

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


def detectExitLicensePlate(video):
    # Using array instead of connect to the database
    licensePlateData = getLicensePlates()

    # step1 arduino side send video stream on rtsp
    # step2 read video strean from arduino rtsp
    stream = cv2.VideoCapture(video, cv2.CAP_FFMPEG)
    # stream = cv2.VideoCapture('carGate.mp4')

    passed = 0
    count = 0
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

        cv2.imshow('IP Camera stream', img)
        
        if licenseText != temp:
            licenseText=temp
            print("License Plate is " + licenseText)
            # Step5 use for loop to compare value in the array licensePlateData
           
            addExitHistory(licenseText)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()


def getLicensePlates():
    licensePlates = cursor.execute('SELECT LicensePlate FROM Car')
    licensePlates = cursor.fetchall()
    return licensePlates


def getCarID(licensePlate):
    carID = cursor.execute('SELECT C.CarID FROM Car C WHERE C.LicensePlate = ?', licensePlate)
    carID = cursor.fetchone()
    return carID[0]


def addExitHistory(licensePlate):
    found = False
    exitTime = datetime.datetime.now()
    exitTime = exitTime.strftime("%Y-%m-%d %H:%M:%S")
    carID = getCarID(licensePlate)
    
    history = cursor.execute('SELECT TOP 1 HistoryID FROM History WHERE CarID = ? ORDER BY HistoryID DESC', carID)
    history = cursor.fetchone()
    cursor.execute('UPDATE History SET ExitTimestamp = ? WHERE HistoryID = ?', exitTime, history[0])
    cursor.commit()
    return True

detectExitLicensePlate('static/sidevid.mp4')