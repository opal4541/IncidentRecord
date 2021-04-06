import cv2
import pyodbc
import numpy as np
import imutils
import pytesseract
import datetime
import socketio
import base64
import time

connection = pyodbc.connect('Driver={SQL Server};'
                            'Server=.;'
                            'Database=IncidentRecord;'
                            'Trusted_Connection=yes;')
cursor = connection.cursor()
sio = socketio.Client()


@sio.event
def connect():
    print('[INFO] Successfully connected to server.')


@sio.event
def connect_error():
    print('[INFO] Failed to connect to server.')


@sio.event
def disconnect():
    print('[INFO] Disconnected from server.')


class EnterClient(object):
    def __init__(self, server_addr):
        self.server_addr = server_addr
        self.server_port = 5000

    def setup(self):
        print('[INFO] Connecting to server http://{}:{}...'.format(
            self.server_addr, self.server_port))
        sio.connect('http://{}:{}'.format(self.server_addr, self.server_port),
                    namespaces=['/enter'])
        time.sleep(1)
        print('my sid is ', sio.sid)
        return self

    def _convert_image_to_jpeg(self, image):
        frame = cv2.imencode('.jpg', image)[1].tobytes()
        frame = base64.b64encode(frame).decode('utf-8')
        return "data:image/jpeg;base64,{}".format(frame)

    def send_data(self, frame, enterlicense, entertime):
        sio.emit('enter2server', {
            'enterimage': self._convert_image_to_jpeg(frame),
            'enterlicense': enterlicense,
            'entertime': entertime
        },
                 namespace='/enter')

    def check_exit(self):
        pass

    def close(self):
        sio.disconnect()


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
    widthA = np.sqrt(((br[0] - bl[0])**2) + ((br[1] - bl[1])**2))
    widthB = np.sqrt(((tr[0] - tl[0])**2) + ((tr[1] - tl[1])**2))
    maxWidth = max(int(widthA), int(widthB))
    heightA = np.sqrt(((tr[0] - br[0])**2) + ((tr[1] - br[1])**2))
    heightB = np.sqrt(((tl[0] - bl[0])**2) + ((tl[1] - bl[1])**2))
    maxHeight = max(int(heightA), int(heightB))
    dst = np.array([[0, 0], [maxWidth - 1, 0], [maxWidth - 1, maxHeight - 1],
                    [0, maxHeight - 1]],
                   dtype="float32")
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    return warped


def most_frequent(List):
    List = list(filter(None, List))
    if List != []:
        return max(set(List), key=List.count)
    else:
        return "None"


# detectEnterLicensePlate
def main(video, server_addr):
    streamer = EnterClient(server_addr).setup()

    licensePlateData = getLicensePlates()
    stream = cv2.VideoCapture(video, cv2.CAP_FFMPEG)
    licenseText = '-'
    temp = '-'
    digitsocr = []

    while True:
        r, img = stream.read()
        ratio = img.shape[0] / 500.0
        orig = img.copy()
        img = imutils.resize(img, height=500)

        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blur, 30, 200)
        contours = cv2.findContours(edged.copy(), cv2.RETR_TREE,
                                    cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

        for c in contours:

            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.01 * peri, True)

            if len(approx) == 4:
                screenCnt = approx

                cv2.drawContours(img, [screenCnt], -1, (0, 255, 255), 3)
                warped = four_point_transform(orig,
                                              screenCnt.reshape(4, 2) * ratio)
                warped = imutils.resize(warped, height=100)
                license_img = warped

                custom_config = r'-l tha -c tessedit_char_whitelist= 0123456789กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรลวศษสหฬอฮ --psm 6'

                ocr_result = pytesseract.image_to_string(
                    license_img,
                    config=custom_config + 'Thai' + 'Thaiitalic' +
                    'tha.psl.bold.italic' + 'psl-bold')
                res = (ocr_result.strip())[0:10]

                res = res.translate({
                    ord(i): None
                    for i in
                    '|-=+[]\n(*)%|"{<>}/?!.«,;: “๐abcdefghijklmnopqrstuvwxyz/ุ๑๒๓๔ู฿๕๖๗๘๙"ๆ้ไำะัโเ๊ีาิแ์ื็'
                })
                if len(res) in range(4, 8):
                    digitsocr.append(res)
                    freq = most_frequent(digitsocr)
                    temp = freq

        if licenseText != temp:
            licenseText = temp
            print("License Plate is " + licenseText)
            enterTime = datetime.datetime.now()
            enterTime = enterTime.strftime("%Y-%m-%d %H:%M:%S")
            print(enterTime)
            addEnterHistory(licenseText, enterTime)
            cv2.imwrite('static/enterVideo/enter.jpg', img)
            streamer.send_data(img, licenseText, enterTime)


def getLicensePlates():
    licensePlates = cursor.execute('SELECT LicensePlate FROM Car')
    licensePlates = cursor.fetchall()
    return licensePlates


def getCarID(licensePlate):
    carID = cursor.execute(
        'SELECT C.CarID FROM Car C WHERE C.LicensePlate = ?', licensePlate)
    carID = cursor.fetchone()
    return carID[0]


def addEnterHistory(licensePlate, time):
    found = False
    enterTime = time
    licensePlates = getLicensePlates()

    for i in licensePlates:
        if licensePlate == i[0]:
            found = True
            break

    if found == True:
        carID = cursor.execute(
            'SELECT C.CarID FROM Car C WHERE C.LicensePlate = ?', licensePlate)
        carID = cursor.fetchone()
        cursor.execute(
            'INSERT INTO History (CarID, EnterTimestamp) VALUES (?,?)',
            (carID[0], enterTime))
        cursor.commit()
        return True

    cursor.execute('INSERT INTO Car(LicensePlate) VALUES (?)', licensePlate)
    cursor.commit()

    carID = cursor.execute(
        'SELECT C.CarID FROM Car C WHERE C.LicensePlate = ?', licensePlate)
    carID = cursor.fetchone()

    cursor.execute('INSERT INTO Customer(FirstName, CarID) VALUES (?, ?)',
                   ("", carID[0]))
    cursor.commit()

    cursor.execute('INSERT INTO History (CarID, EnterTimestamp) VALUES (?,?)',
                   (carID[0], enterTime))
    cursor.commit()
    return True


if __name__ == "__main__":
    # main('rtsp://admin:sonofabird@192.168.1.4:10554/tcp/av0_0', '127.0.0.1')
    main('testalert1.mp4', '127.0.0.1')