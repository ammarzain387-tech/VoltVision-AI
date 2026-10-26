import cv2
import json
import time
import numpy as np
from paho.mqtt import client as mqtt_client

# --- AWS Configuration ---
# Yahan apna AWS IoT Core ka Endpoint URL paste karein
AWS_ENDPOINT = "YOUR_ENDPOINT_HERE-ats.iot.REGION.amazonaws.com" 
PORT = 8883
CLIENT_ID = "VoltVision_Edge"
TOPIC = "voltvision/alerts"

# --- Certificates Path ---
CA_CERTS = "certs/root-CA.crt"
CERTFILE = "certs/device.pem.crt"
KEYFILE = "certs/private.pem.key"

# --- MQTT Connection Setup ---
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ AWS IoT Core se successfully connect ho gaya!")
    else:
        print(f"❌ Connection fail hua, return code: {rc}")

client = mqtt_client.Client(CLIENT_ID)
client.on_connect = on_connect
client.tls_set(ca_certs=CA_CERTS, certfile=CERTFILE, keyfile=KEYFILE)
print("AWS se connect kar raha hai...")
client.connect(AWS_ENDPOINT, PORT)
client.loop_start()
time.sleep(2) # Connection establish hone ke liye thoda wait

# --- OpenCV Computer Vision Setup ---
cap = cv2.VideoCapture(0) # 0 ka matlab laptop ka apna camera hai
last_alert_time = 0

print("VoltVision AI camera open kar raha hai. Band karne ke liye 'q' dabayein.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Camera nahi chal raha.")
        break

    # Image processing: Spark/Aag ko color se detect karna (HSV color space)
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

    # --- AWS par Alert Bhejna ---
    current_time = time.time()
    # 5 seconds ka gap takay baar baar same message na jaye
    if spark_detected and (current_time - last_alert_time > 5):
        alert_payload = {"alert": "WARNING: Electrical Spark Detected!", "timestamp": int(current_time)}
        client.publish(TOPIC, json.dumps(alert_payload))
        print(f"🚨 AWS par alert bhej diya: {alert_payload}")
        last_alert_time = current_time

    # Keyboard par 'q' dabane se loop break ho jayega
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
client.loop_stop()