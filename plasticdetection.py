from flask import Flask, Response, render_template_string
import cv2
import time
import threading
import lgpio
from ultralytics import YOLO

# Initialize Flask app
app = Flask(name)

# Initialize camera
camera = cv2.VideoCapture(0)
model = YOLO("yolov8n.pt")  # Use your custom model if needed

# Servo setup
h = lgpio.gpiochip_open(0)
servo_pin = 18

# Detection logic
detection_count = 0
detection_threshold = 5
servo_triggered = False

# HTML Template
HTML_TEMPLATE = """
<html>
<head><title>Live Stream</title></head>
<body>
<h2>YOLOv8 Bottle Detection</h2>
<img src="{{ url_for('video_feed') }}">
</body>
</html>
"""
def move_servo():
    print("Claiming GPIO and moving servo...")
    lgpio.gpio_claim_output(h, servo_pin, 0)  # <-- Claim pin first

    # Move to center
    print("Center (7.5%)")
    lgpio.tx_pwm(h, servo_pin, 50, 7.5)
    time.sleep(1)

    # Move to left
    print("Left (5%)")
    lgpio.tx_pwm(h, servo_pin, 50, 5.0)
    time.sleep(1)

    # Move to right
    print("Right (10%)")
    lgpio.tx_pwm(h, servo_pin, 50, 10.0)
    time.sleep(1)

    # Stop PWM
    print("Stopping PWM")
    lgpio.tx_pwm(h, servo_pin, 0, 0)



def generate_frames():
    global detection_count, servo_triggered
    while True:
        success, frame = camera.read()
        if not success:
            break

        # Run YOLO detection
        results = model(frame, verbose=False)
        annotated_frame = results[0].plot()

        # Check for 'bottle' in detections
        labels = results[0].names
        bottle_found = any(labels[int(cls)] == 'bottle' for cls in results[0].boxes.cls)

        if bottle_found and not servo_triggered:
            move_servo()
            servo_triggered = True
        elif not bottle_found:
            servo_triggered = False  # reset if object is gone


        _, buffer = cv2.imencode('.jpg', annotated_frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

try:
    if name == 'main':
        app.run(host='0.0.0.0', port=5000)
finally:
    # Cleanup
    camera.release()
    lgpio.tx_pwm(h, servo_pin, 0, 0)
    lgpio.gpiochip_close(h)