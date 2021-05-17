import cv2
import numpy as np
import imutils
import pytesseract
from PIL import Image, ImageEnhance,ImageFont, ImageDraw
from selenium import webdriver
import time

# use function to convert image for finding license plate easier
def convertImage(image):
    gray = cv2.cvtColor(image,cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray,(5,5),0)
    canny = cv2.Canny(blur,100,200)
    return canny

def write_tt_text(image,x,y,text):
    try:
        win_text=text.decode('UTF-8')
        win_text=win_text+unichr(0x0020)+unichr(0x0020)
    except:
        win_text=text+'  '
    Font1 = ImageFont.truetype("THSarabunNew Bold.ttf", 25)
    image_pil = Image.new("RGB",(150,50),(0,0,0))
    draw = ImageDraw.Draw(image_pil)
    draw.text((5,5),win_text,(255,255,255),font=Font1)
    del draw
    cv_image = np.array(image_pil) 
    cv_image = cv_image[:, :, ::-1].copy() 
    imageout = image.copy()    
    if y>=0 and x>=0:
        if x+150<=imageout.shape[1] and y+50<=imageout.shape[0]:
            imageout[0+y:0+y+50 , 0+x:0+x+150] = cv_image
    return imageout

def most_frequent(List): 
    List = list(filter(None, List))
    if List != []:
        return max(set(List), key = List.count) 
    else:
        return "None"

# Using array instead of connect to the database
licensePlateArr = ["ฌง5289","อ5257","6กผ4163","9กต7707","5กค5174","4กต29",
"ฎห7898","7กข9959","งน9535","ฎท5296","บว1360","ญฮ6000","9กณ8320","วก3773"] 

# step1 arduino side send video stream on rtsp
# step2 read video strean from arduino rtsp
stream = cv2.VideoCapture('rtsp://192.168.1.3:8554/mjpeg/1', cv2.CAP_FFMPEG)
# stream = cv2.VideoCapture('carGate.mp4')

# open servo web
driver = webdriver.Chrome()
driver.get('http://192.168.1.9')

found = 0
passed = 0
count = 0
licenseText = '-'
temp= '-'
digitsocr = []

while True:
    # step3 capture image when detect license plate
    r, img = stream.read()
    time.sleep(0.2)    
    cv2.imshow('IP Camera stream', img)
    processed_img = convertImage(img)
    original_img = img.copy()
    contour_img = processed_img.copy()

    contours, heirarchy = cv2.findContours(contour_img,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

    for contour in contours:
        p = cv2.arcLength(contour,True)
        approx = cv2.approxPolyDP(contour,0.02*p,True)

        if len(approx) == 4:
            x,y,w,h = cv2.boundingRect(contour)
            license_img = original_img[y:y+h,x:x+w]
            cv2.imshow("License Detected : ",license_img)
            cv2.drawContours(img, [contour],-1,(0,255,255),3)

            custom_config = r'-l tha -c tessedit_char_whitelist= 0123456789กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรลวศษสหฬอฮ --psm 6'
            ocr_result = pytesseract.image_to_string(license_img, config=custom_config + 'Thai' + 'Thaiitalic')
            res = (ocr_result.strip())[0:10]

            res = res.translate({ord(i): None for i in '|-=+[]\n(*)%|"{<>}/.« abcdefghijklmnopqrstuvwxyz/ุ๑๒๓๔ู฿๕๖๗๘๙"ๆไำะัโเ๊ีาิแ์ื'})
            if len(res) in range(4,8):
                digitsocr.append(res)
                freq = most_frequent(digitsocr)
                temp = freq
    
    if licenseText != temp:
        licenseText = temp 
        print("License Plate is " + licenseText)
        # Step5 use for loop to compare value in the array licensePlateArr
        for i in licensePlateArr:
            if i == licenseText:
                print("Pass")
                # step6 if found that licese plate chage found to 1
                found = 1
                
                # step7 control servo via web app
                # also have to write auduino side to get command via web app
                button = driver.find_element_by_name('seron')
                button.click()
                
            
        if found == 0 and licenseText != '-':
            print("Reject")
        else:
            found = 0

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

driver.close()
cv2.destroyAllWindows()
