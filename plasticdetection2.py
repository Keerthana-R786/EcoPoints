import time
import threading
import cv2
import lgpio
import smbus2
from flask import Flask, render_template, Response
from picamera2 import Picamera2
from ultralytics import YOLO
import SimpleMFRC522
import numpy as np
from PIL import Image
import io

# Initialize Flask
app = Flask(_name_)

# Initialize camera
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'RGB888', "size": (640, 480)}))
picam2.start()

# Load YOLOv8 model
model = YOLO("yolov8n.pt")  # Replace with your trained model path if custom

# Initialize RFID and LCD
reader = SimpleMFRC522.SimpleMFRC522()
bus = smbus2.SMBus(1)
lcd_addr = 0x27

# Initialize Servo
servo_pin = 17
chip = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(chip, servo_pin)

def set_servo(angle):
    pulse = int((angle * 2000 / 180) + 500)
    lgpio.tx_pwm(chip, servo_pin, 50, pulse)
    time.sleep(0.5)
    lgpio.tx_pwm(chip, servo_pin, 0, 0)

# LCD Functions
def lcd_init():
    cmds = [0x33, 0x32, 0x06, 0x0C, 0x28, 0x01]
    for cmd in cmds:
        lcd_byte(cmd, 0)
        time.sleep(0.05)

def lcd_byte(bits, mode):
    bits_high = mode | (bits & 0xF0) | 0x08
    bits_low = mode | ((bits << 4) & 0xF0) | 0x08
    bus.write_byte(lcd_addr, bits_high)
    time.sleep(0.0005)
    bus.write_byte(lcd_addr, bits_high | 0x04)
    time.sleep(0.0005)
    bus.write_byte(lcd_addr, bits_high & ~0x04)
    time.sleep(0.0005)
    bus.write_byte(lcd_addr, bits_low)
    time.sleep(0.0005)
    bus.write_byte(lcd_addr, bits_low | 0x04)
    time.sleep(0.0005)
    bus.write_byte(lcd_addr, bits_low & ~0x04)
    time.sleep(0.0005)

def lcd_string(message, line):
    message = message.ljust(16, " ")
    lcd_byte(line, 0)
    for char in message:
        lcd_byte(ord(char), 1)

# Detection & Control Variables
bottle_detected_count = 0
user_id = None
user_name = ""
max_count = 5

# Thread-safe lock
lock = threading.Lock()

def detect_and_control():
    global bottle_detected_count, user_id, user_name

    while True:
        frame = picam2.capture_array()
        results = model.predict(source=frame, conf=0.5, classes=[39], verbose=False)  # Class 39 = bottle

        if results and results[0].boxes:
            with lock:
                bottle_detected_count += 1
            print(f"Bottle detected ({bottle_detected_count}/{max_count})")

            if bottle_detected_count >= max_count:
                print("Activating servo...")
                set_servo(90)
                time.sleep(1)
                set_servo(0)

                # Reward user
                lcd_string(f"User: {user_name}", 0x80)
                lcd_string("Reward +1 Point", 0xC0)

                time.sleep(3)
                bottle_detected_count = 0

        time.sleep(0.2)

def video_stream():
    while True:
        frame = picam2.capture_array()
        with lock:
            annotated = frame.copy()
        _, buffer = cv2.imencode('.jpg', annotated)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def rfid_thread():
    global user_id, user_name
    while True:
        try:
            id, text = reader.read()
            user_id = id
            user_name = text.strip()
            print(f"User detected: {user_name} (ID: {user_id})")
            lcd_string(f"Hello {user_name}", 0x80)
            lcd_string("Welcome!", 0xC0)
            time.sleep(3)
        except Exception as e:
            print("RFID error:", e)
        time.sleep(1)

if _name_ == '_main_':
    lcd_init()
    threading.Thread(target=rfid_thread, daemon=True).start()
    threading.Thread(target=detect_and_control, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
