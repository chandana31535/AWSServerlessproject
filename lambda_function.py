import boto3
from botocore.exceptions import ClientError

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')

def lambda_handler(event, context):
    # Retrieve the bucket and key from the event
    bucket = "skill10awsrekog"
    key = event['key']
    
     # Check if the object exists in the bucket
    try:
        s3.head_object(Bucket=bucket, Key=key)
    except ClientError as e:
        if e.response['Error']['Code'] == "404":
            # Object doesn't exist, return an error
            return {
                'statusCode': 404,
                'body': 'The specified image does not exist in the bucket.'
            }
        else:
            # An error occurred, return an error
            return {
                'statusCode': 500,
                'body': 'An error occurred: ' + e.response['Error']['Message']
            }
    
    # Download the image from S3
    response = s3.get_object(Bucket=bucket, Key=key)
    image_bytes = response['Body'].read()
    
    # Store the image in the S3 bucket
    new_key = 'analyzed/' + key  # Key for the analyzed image
    s3.put_object(Bucket=bucket, Key=new_key, Body=image_bytes)
    
    # Use Rekognition to analyze the image
    response = rekognition.detect_labels(
        Image={
            'Bytes': image_bytes
        },
        MaxLabels=10,
        MinConfidence=90
    )
    
    # Return the detected labels as a response
    labels = []
    for label in response['Labels']:
        labels.append({
            'name': label['Name'],
            'confidence': label['Confidence']
        })
    return labels
        
   
