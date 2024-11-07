import boto3

sns_client = boto3.client('sns')


def publish_sns_message(message, subject):
    response = sns_client.publish(
        TopicArn='arn:aws:sns:eu-central-1:796973490501:web-checker-notification',
        Message=message,
        Subject=subject,
        MessageStructure='string'
    )

    print("SNS Message published.")
