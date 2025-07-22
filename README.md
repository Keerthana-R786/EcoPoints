# ♻️ EcoPoints - Smart Plastic Bottle Recycling System

An AI-powered plastic bottle disposal system using **Raspberry Pi**, **YOLOv8**, **RFID**, **LCD**, and **Servo Motor** that rewards users with eco-points for responsible recycling.

---

## 🧠 Problem Statement

Many people lack the motivation to recycle plastic bottles due to the absence of rewards or awareness. Improper disposal and mixing with general waste reduce recycling efficiency. Manual collection is slow, inconsistent, and labor-intensive.

---

## 🎯 Objective

To **encourage responsible recycling** by rewarding users (especially students) for depositing verified plastic bottles. The system builds awareness through an interactive and rewarding experience while promoting environmental cleanliness.

---

## 🚀 How It Works

1. LCD displays: `WELCOME` → `SCAN THE ID`
2. User scans RFID card.
3. LCD displays: `INSERT THE BOTTLE`
4. Servo motor opens the bottle slot.
5. Camera captures the inserted item and uses **YOLOv8** for object detection.
6. If detected as **plastic bottle**:
   - LCD shows: `VERIFIED`
   - 10 points are awarded and stored.
7. If not:
   - LCD shows: `NOT PLASTIC BOTTLE`

---

## ⚙️ Hardware Components

| Component             | Function                                   |
|----------------------|--------------------------------------------|
| **Raspberry Pi 4**    | Main processing unit                       |
| **PiCamera Module**   | Captures and analyzes the bottle image     |
| **RC522 RFID Module** | Scans user ID for authentication           |
| **RFID Tags**         | Unique student/user ID cards               |
| **I2C 16x2 LCD**      | Displays status and messages               |
| **Servo Motor**       | Opens/closes the bin slot                  |
| **Breadboard & Wires**| Circuit assembly                           |
| **Bottle Bin**        | Holds collected plastic bottles            |

---

## 🧰 Software & Libraries Used

- Python 3.x
- [YOLOv8](https://github.com/ultralytics/ultralytics) (Ultralytics)
- Flask (for live video stream)
- OpenCV (`cv2`)
- `picamera2`
- `lgpio` (servo & GPIO control)
- `SimpleMFRC522` (RFID reading)
- `smbus2`, `RPLCD` (for LCD control)
- NumPy, Pillow

---


---

## 🔌 Hardware Setup

- Connect **RFID** to Raspberry Pi SPI pins (MISO, MOSI, SCK, RST)
- Connect **Servo motor** to GPIO17 (pin 11)
- Connect **LCD (I2C)** to SDA/SCL pins
- Attach **PiCamera** to CSI interface
- Enable I2C and SPI using:

```bash
sudo raspi-config
# Enable: I2C, SPI, Camera
```

## 💻 Software Installation

Run the following commands to install required packages:

```bash
# Update system packages
sudo apt update && sudo apt upgrade

# Install required Linux packages
```

## 📥 Download YOLOv8 Model

Download the YOLOv8 nano model using the following command:

```bash
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
```

## ▶️ How to Run

Start the system by running the following command:

```bash
python3 main.py
```

## 🔄 LCD Message Flow

| Step               | LCD Message         |
|--------------------|---------------------|
| Startup            | WELCOME             |
| RFID Prompt        | SCAN THE ID         |
| After RFID Scan    | INSERT THE BOTTLE   |
| Verified Bottle    | VERIFIED            |
| Invalid Item       | NOT PLASTIC BOTTLE  |


## 📈 Reward System

- Each plastic bottle inserted after verification = **+10 EcoPoints**
- Points are **stored per user in memory**
- Can be extended to a **database** (e.g., SQLite or Firebase)
- Enables **user ranking** and **reward-based systems**

---

## 💡 Future Enhancements

- Persist user data using **SQLite** or **Firebase**
- Add **mobile/web dashboard** to track eco-points
- Add **buzzer or LED feedback** for interaction
- Use **face recognition** for user identification
- Add **QR code scanning** as an alternative to RFID

---

## ⚠️ Known Challenges

- YOLO detection may vary based on **lighting** or **angle**
- **Limited processing power** on Raspberry Pi
- Possible **missed RFID scans**
- Servo may **wear out** with frequent use
- Requires regular **cleaning and calibration**
- Risk of misuse: users may insert **non-plastic items**

---

## 📜 License

This project is licensed under the **MIT License**.  
See the [LICENSE](./LICENSE) file for details.

---

## 👨‍💻 Team Members

- **Jaffiswetha J** – ECE, 2nd Year  
- **Keerthana R** – IT, 2nd Year  
- **Rishivathen C** – ACT, 3rd Year

## 📣 Acknowledgment

Special thanks to our **institution** and **faculty mentors** for supporting this project and guiding us throughout the development process.

