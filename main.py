import cv2
import numpy as np
import time
import boto3

# =====================================================================
# AWS SNS CONFIGURATION (MUST BE OUTSIDE / ABOVE THE LOOP)
# =====================================================================
TOPIC_ARN = "arn:aws:sns:ap-southeast-2:522688056640:VoltVision-Spark-Alerts"
AWS_REGION = "ap-southeast-2"

# Replace with your actual AWS Keys
AWS_ACCESS_KEY_ID = "YOUR_AWS_ACCESS_KEY"
AWS_SECRET_ACCESS_KEY = "YOUR_AWS_SECRET_ACCESS_KEY"

# Initialize AWS SNS Client
sns_client = boto3.client(
    'sns',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

last_sns_alert_time = 0
SNS_COOLDOWN = 15  # Seconds delay between alerts

# =====================================================================
# OPENCV CAMERA SETUP & LOOP
# =====================================================================
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Error: Could not open webcam.")
    exit()

print("🚀 VoltVision AI System Running...")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # HSV Color range for bright sparks
    lower_bound = np.array([0, 0, 250])
    upper_bound = np.array([180, 80, 255])

    # Create mask and apply blur to reduce noise
    mask = cv2.inRange(hsv, lower_bound, upper_bound)
    mask = cv2.GaussianBlur(mask, (5, 5), 0)

    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    spark_detected = False

    for contour in contours:
        # Area threshold to filter out tiny room lights
        if cv2.contourArea(contour) > 1000:
            spark_detected = True
            x, y, w, h = cv2.boundingRect(contour)

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(
                frame,
                "SPARK HAZARD DETECTED",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 255),
                2
            )

    # Send AWS SNS Email Alert
    if spark_detected:
        current_time = time.time()
        if current_time - last_sns_alert_time > SNS_COOLDOWN:
            try:
                response = sns_client.publish(
                    TopicArn=TOPIC_ARN,
                    Message="🚨 CRITICAL HAZARD ALERT: Electrical Spark Detected by VoltVision AI!",
                    Subject="⚡ VoltVision Emergency Hazard Alert"
                )
                print("📧 Email alert sent via AWS SNS! ID:", response['MessageId'])
                last_sns_alert_time = current_time
            except Exception as e:
                print("❌ Failed to send SNS alert:", e)

    # Windows display
    cv2.imshow("VoltVision AI - Hazard Monitor", frame)
    cv2.imshow("Detection Mask (Debug)", mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()