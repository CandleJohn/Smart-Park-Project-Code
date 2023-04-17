#!/usr/bin/python
from picamera import PiCamera # To take picture of license plate
import RPi.GPIO as GPIO # Interface for ultrasonic sensor
import time # required for sensor calculation and booking
import pyrebase # Firebase connection
import cv2 # Computer vision library
import imutils # Resize image and contours
import numpy as np # require for mask
import pytesseract # python tesseract OCR wrapper
from PIL import Image
from datetime import datetime, timedelta # required for booking date
import requests # requests to Express API
import re # cleaning OCR output

#config for pyrebase and initialize db
config = {
    "apiKey" : "AIzaSyC5upBHcRIrC-jh7uzW3O90JU93WIkCAkU",
    "authDomain" : "smartpark-4fb2b.firebaseapp.com",
    "databaseURL" : "https://smartpark-4fb2b-default-rtdb.europe-west1.firebasedatabase.app/",
    "storageBucket" : "smartpark-4fb2b.appspot.com"
    }
    
firebase = pyrebase.initialize_app(config)
db = firebase.database()

carPark = "carPark1"
space = "space1"

# Set the GPIO mode
GPIO.setmode(GPIO.BOARD)

# Set the pin numbers for the ultrasonic sensor
TRIG = 7
ECHO = 11

# Set the distance range (in cm)
min_distance = 1
max_distance = 20

# Set up the GPIO pins
GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)

camera = PiCamera()
camera.rotation = 180
'''
This function is the base of the Device script. Every 2 seconds a pulse is sent out from the ultrasonic sensor with the time
the pulse was sent and when it was returned both being recorded. The difference in these times is then multiplied by 17150 to
get the distance in cm.
If the distance is inside the set range of min and max distance, The Pi camera will take a picture and the read_license_plate is
called.
'''
def check_space():
    time.sleep(2)

    # Send a 10us pulse to the TRIG pin
    GPIO.output(TRIG, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIG, GPIO.LOW)

    # Measure the duration of the pulse on the ECHO pin
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    # Calculate the distance
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150

    # Check if the distance is within range
    if distance > min_distance and distance < max_distance:
        print("Object is within range (%.2f cm)" % distance)
        camera.capture("img.jpg")
        print("Picture taken")
        read_license_plate()
    else:
        print("No object in range")

'''
This function uses the pyrebase configuration defined above to update values in the Firebase Realtime database used by the mobile application
'''
def update_realtime_db(licensePlate, occ):
	data = {"name": "1", "registration":licensePlate, "occupied":occ}
	db.child("carPark1").child("space1").update(data)

'''
This function finds the vehicle id for a vehicle in the MySQL database. This function uses the requests library to
send a request to the Express web service using the registration read by the read_license_plate function.
If the registration read is in the database the booking function is called passing along the vehicle id to 
associate the booking with a driver in the database.
'''
def check_valid_reg(licensePlate):
	url = 'http://172.20.10.2:5002/checkRegistration'
	
	data = {'registration': licensePlate }
	response = requests.post(url, data=data)
	if response.text is not None:
		update_realtime_db(licensePlate, True)
		response_data = response.json()
		driverId = response_data[0]['driver_id']
		vehicleId = response_data[0]['vehicle_id']
		booking(driverId, vehicleId)
	else:
		update_realtime_db("", True)

'''
This function gets the values for the bookings table in the MySQL database and uses the requests library to send the information
to the database. The occupied variable is used to control and time how long a vehicle is parked in a space. The same method is used
to check if a vehicle is still occupying the space. Once the vehicle has left the end time is stored, the realtime database is updated,
and the function leaves the loop to calculate the duration of the parking. The cost is then assigned from this duration.
'''
def booking(driverId, vehicle_id):
	occupied = True
	# Convert minutes and hours to seconds
	minutes_30 = 30 * 60
	hours_2 = 2 * 60 * 60
	hours_4 = 4 * 60 * 60
	start = datetime.now()
	date = start.strftime("%Y-%m-%d")
	while occupied is True:
		time.sleep(2)

		# Send a 10us pulse to the TRIG pin
		GPIO.output(TRIG, GPIO.HIGH)
		time.sleep(0.00001)
		GPIO.output(TRIG, GPIO.LOW)

		# Measure the duration of the pulse on the ECHO pin
		while GPIO.input(ECHO) == 0:
			pulse_start = time.time()
		while GPIO.input(ECHO) == 1:
			pulse_end = time.time()

		# Calculate the distance
		pulse_duration = pulse_end - pulse_start
		distance = pulse_duration * 17150

		# Check if the distance is within range
		if distance > min_distance and distance < max_distance:
			print("Vehicle parked")
		else:
			update_realtime_db("", False)
			occupied = False
			end = datetime.now()
			print("Booking added")

	duration = end - start
	if duration.total_seconds() < minutes_30:
		cost = 0 # short term no cost
	elif duration.total_seconds() < hours_2:
		cost = 2 # hourly rate
	elif duration.total_seconds() < hours_4:
		cost = 4 # hourly rate
	else:
		cost = 8 # day rate
	
	duration_seconds = duration.total_seconds()
	hours = int(duration_seconds // 3600)
	minutes = int((duration_seconds % 3600) // 60)
	seconds = int(duration_seconds % 60)

	formatted_duration = "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)
	
	url = 'http://172.20.10.2:5002/addBooking'
	
	data = {'bookingDate': date,'bookingCost': cost, 'bookingDuration': formatted_duration, 'vehicleId': vehicle_id }
	response = requests.post(url, data=data)

'''
This is the main function that reads the license plate in the image taken by the check_space function.
The image is read in as an image object by OpenCV. It is then resized and converted to greyscale to simplify
the further processing functions by reducing the image to a single channel of representation where each pixel
now only ranges from 0(black) to 255(white). BilateralFilter is used to smooth/blur an image while preserving the edges
this is useful as the edged around the license plate will remain but any obscure areas will be smoothed over.
Canny is an edge detection algorithm that finds areas in an image where the intensity changes abbrubtly. This is useful
in the system as the function can detect the borders of the license plate along with the characters as the license plate would be white
with the characters and border being black. The findContours function finds contours (i.e., the outlines of objects) in the input edged image. 
It takes three arguments: the input image, the contour retrieval mode (in this case, cv2.RETR_TREE which retrieves all of the contours and 
 reconstructs a full hierarchy of nested contours), and the contour approximation method (in this case, cv2.CHAIN_APPROX_SIMPLE which
 compresses horizontal, diagonal, and vertical segments and leaves only their end points).
As we need a full rectangle to find the license plate area, the for loop goes through each of the found contour to find a closed contour.
Once an appropriate contour is found it is cropped and sent to the Tesseract OCR. The output is then used in the check_valid_reg function.
'''
def read_license_plate():
	image = cv2.imread("001.jpg")
	image = imutils.resize(image, width=600)
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	gray = cv2.bilateralFilter(gray, 11, 17, 17)
	edged = cv2.Canny(gray, 30, 200)
	cv2.imshow("edged", edged)
	cnts = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]
	screenCnt = None
	for c in cnts:
		peri = cv2.arcLength(c, True)
		approx = cv2.approxPolyDP(c, 0.018 * peri, True)
		if len(approx) == 4:
			screenCnt = approx
			break
	
	mask = np.zeros(gray.shape, np.uint8)
	new_image = cv2.drawContours(mask, [screenCnt], 0, 255, -1,)
	new_image = cv2.bitwise_and(image, image, mask=mask)
	
	(x,y) = np.where(mask == 255)
	(topx, topy) = (np.min(x), np.min(y))
	(bottomx, bottomy) = (np.max(x), np.max(y))
	Cropped = gray[topx:bottomx+1, topy:bottomy+1]
	cv2.imshow("edged", Cropped)
	text = pytesseract.image_to_string(Cropped, config='-c tessedit_char_whitelist=01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ --psm 11')
	text = re.sub(r'[^A-Z0-9]','',text)
	print(text)
	check_valid_reg(text)

while True:
	check_space()