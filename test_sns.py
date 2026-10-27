import boto3

# Your AWS SNS Topic ARN
TOPIC_ARN = "arn:aws:sns:ap-southeast-2:522688056640:VoltVision-Spark-Alerts"

# AWS SNS Client Setup
sns_client = boto3.client(
    'sns',
    region_name='ap-southeast-2',                   # Matched with ARN region
    aws_access_key_id='AKIAXTMVCZVAE33ZIR43',        # Paste your Access Key here
    aws_secret_access_key='lbmV4ByMuK3a0ImtMAmHPg4FdN2NkUm99sfWVCZW'     # Paste your Secret Key here
)

def send_test_alert():
    try:
        response = sns_client.publish(
            TopicArn=TOPIC_ARN,
            Message="⚠️ VOLTVISION AI ALERT: Electrical Spark Hazard Detected at Zone 1!",
            Subject="⚡ VoltVision Emergency Alert"
        )
        print("✅ Alert Sent Successfully! Message ID:", response['MessageId'])
    except Exception as e:
        print("❌ Failed to send alert:", e)

if __name__ == "__main__":
    send_test_alert()