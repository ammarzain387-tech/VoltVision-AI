import cv2
import json
import time
import numpy as np
from paho.mqtt import client as mqtt_client

# --- AWS Configuration (Dummy Mode) ---
AWS_ENDPOINT = "dummy-endpoint-ats.iot.ap-southeast-2.amazonaws.com"
PORT = 8883
CLIENT_ID = "VoltVision_Edge"
TOPIC = "voltvision/alerts"

# --- OpenCV Computer Vision Setup ---
cap = cv2.VideoCapture(0) # 0 = Laptop Camera
last_alert_time = 0

print("VoltVision AI camera open kar raha hai. Band karne ke liye 'q' dabayein.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Camera nahi chal raha.")
        break

    # Image processing: Spark/Aag ko color se detect karna (HSV)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Bright orange/yellow (Sparks) ke liye color range
    lower_spark = np.array([15, 150, 200]) 
    upper_spark = np.array([35, 255, 255])
    
    mask = cv2.inRange(hsv, lower_spark, upper_spark)
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    spark_detected = False
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 500: # Agar spark ka size bada hai to alert trigger karein
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
            cv2.putText(frame, "HAZARD: SPARK DETECTED!", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            spark_detected = True

    cv2.imshow("VoltVision AI - Edge Monitor", frame)

    # --- Local Alert Print (No AWS) ---
    current_time = time.time()
    if spark_detected and (current_time - last_alert_time > 3):
        print(f"🚨 [LOCAL ALERT] WARNING: Electrical Spark Detected! (Simulating AWS sending...)")
        last_alert_time = current_time

    # Keyboard par 'q' dabane se loop break ho jayega
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()