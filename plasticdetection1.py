import cv2
import time
import lgpio
import threading
from flask import Flask, render_template, Response
from picamera2 import Picamera2
from yolov8 import YOLO  # Assumes custom class or use: from ultralytics import YOLO
from SimpleMFRC522 import SimpleMFRC522
from RPLCD.i2c import CharLCD
from smbus2 import SMBus

# Setup Flask
app = Flask(_name_)

# Servo Setup
SERVO_PIN = 17
gpio = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(gpio, SERVO_PIN)
DETECTION_TARGET = "bottle"
DETECTION_COUNT = 5
detection_counter = 0
servo_lock = threading.Lock()

# RFID Setup
reader = SimpleMFRC522()

# LCD Setup
lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1,
              cols=16, rows=2, charmap='A00', auto_linebreaks=True, backlight_enabled=True)

# Camera & YOLO Setup
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picam2.start()
model = YOLO('yolov8n.pt')  # or path to your trained model

# Users database
users = {
  1234567890: {'name': 'Alice', 'points': 0},
  9876543210: {'name': 'Bob', 'points': 0}
}
current_user = None

def trigger_servo():
    with servo_lock:
        lgpio.tx_servo(gpio, SERVO_PIN, 1500)  # Neutral
        time.sleep(0.5)
        lgpio.tx_servo(gpio, SERVO_PIN, 1000)  # Open
        time.sleep(0.5)
        lgpio.tx_servo(gpio, SERVO_PIN, 1500)  # Neutral
        time.sleep(0.5)
        lgpio.tx_servo(gpio, SERVO_PIN, 2000)  # Close
        time.sleep(0.5)
        lgpio.tx_servo(gpio, SERVO_PIN, 0)     # Stop

def update_lcd():
    lcd.clear()
    if current_user:
        lcd.write_string(f"{current_user['name']}\nPoints: {current_user['points']}")
    else:
        lcd.write_string("Scan your card")

def detect_rfid():
    global current_user
    while True:
        try:
            id, text = reader.read()
            if id in users:
                current_user = users[id]
                update_lcd()
            else:
                current_user = {'name': 'NewUser', 'points': 0}
                users[id] = current_user
                update_lcd()
        except Exception as e:
            print("RFID Error:", e)
        time.sleep(1)

def gen_frames():
    global detection_counter
    while True:
        frame = picam2.capture_array()
        results = model(frame)
        annotated_frame = results[0].plot()

        if any(DETECTION_TARGET in c for c in results[0].names.values()):
            detection_counter += 1
            print(f"[INFO] Detected {DETECTION_TARGET} ({detection_counter}/{DETECTION_COUNT})")
            if detection_counter >= DETECTION_COUNT:
                print("[ACTION] Triggering servo and rewarding user")
                trigger_servo()
                detection_counter = 0
                if current_user:
                    current_user['points'] += 1
                    update_lcd()

        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if _name_ == '_main_':
    update_lcd()
    threading.Thread(target=detect_rfid, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
