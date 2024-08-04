import json
import boto3

# Get the service resource.
dynamodb = boto3.resource('dynamodb', 'ap-south-1')
dynamodb_table = dynamodb.Table('User_Login')

def lambda_handler(event, context):
    try:
       response = dynamodb_table.get_item(
                              Key={"Mobile_Number": event["Mobile_Number"], "Login_Type": event["Login_Type"]}
                             )
       item = response['Item']
       if (event['Password'] == item["Password"]):
          loginStatus = "Success"
       else:
          loginStatus = "Failure"
    except KeyError:
        return {
              "statusCode": 200,
              "body": json.dumps({"Mobile_Number": event["Mobile_Number"], "loginStatus": "User not found"})
               }
    
    return {
    "statusCode": 200,
    "body": json.dumps({"Mobile_Number": item["Mobile_Number"], "loginStatus": loginStatus})
    }
