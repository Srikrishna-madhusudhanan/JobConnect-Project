import json
import boto3
import random
import logging

# Get the service resource.
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('User_Login')

logger = logging.getLogger()
logger.setLevel("INFO")

client = boto3.client('ses', region_name='ap-south-1')

def lambda_handler(event, context):
    
    AccessCode =""
    
    if event["Action"] == "SendAccessCode": 
            try:
                    response = table.get_item(
                        Key={
                            "Mobile_Number": event["Mobile_Number"],
                            "Login_Type": event["Login_Type"]
                        }
                    )
            except ClientError as err:
                    AccessCode = str(random.randrange(123456, 987654))
            else:
                    item = response['Item']
                    try:
                        if len(item["AccessCode"]) > 3: 
                               AccessCode = item["AccessCode"]
                    except Exception:
                        AccessCode = str(random.randrange(123456, 987654))
            if len(AccessCode) < 3:
                AccessCode = str(random.randrange(123456, 987654))
            table.update_item(
                    Key={
                            "Mobile_Number": event["Mobile_Number"],
                            "Login_Type": event["Login_Type"]
                    },
                    UpdateExpression='SET AccessCode = :val1',
                    ExpressionAttributeValues={
                        ':val1': AccessCode
                    }
                )
            response = client.send_email(
                            Destination={
                                'ToAddresses': [event["RecipientEmailAddress"]]
                            },
                            Message={
                                'Body': {
                                    'Text': {
                                        'Charset': 'UTF-8',
                                        'Data': 'Access Code: ' + AccessCode,
                                    }
                                },
                                'Subject': {
                                    'Charset': 'UTF-8',
                                    'Data': 'Access Code for JobConnect verification',
                                },
                            },
                            Source="JobConnects@protonmail.com"
                            )
            return {
                'statusCode': 200,
                'body': json.dumps("Email Sent Successfully. MessageId is: " + response['MessageId'])
            }
    elif event["Action"] == "VerifyEmail": 
            try:
                    response = table.get_item(
                        Key={
                            "Mobile_Number": event["Mobile_Number"],
                            "Login_Type": event["Login_Type"]
                        }
                    )
            except ClientError as err:
                    raise
            else:
                    item = response['Item']
                    try:
                        if item["AccessCode"] == event["AccessCode"]:
                                table.update_item(
                                                Key={
                                                        "Mobile_Number": event["Mobile_Number"],
                                                        "Login_Type": event["Login_Type"]
                                                },
                                                UpdateExpression='SET EmailStatus = :val1',
                                                ExpressionAttributeValues={
                                                    ':val1': "Verified"
                                                }
                                            )
                                return {
                                      "statusCode": 200,
                                      "body": json.dumps({"Email": event["RecipientEmailAddress"], "Email_Status": "Email Verified"})
                                       }
                        else:
                                return {
                                      "statusCode": 202,
                                      "body": json.dumps({"Email": event["RecipientEmailAddress"], "Email_Status": "Email is not yet verified"})
                                       }
                    except Exception as e:
                           Logger.info(e)

        