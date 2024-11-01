import json
import requests
from bs4 import BeautifulSoup
import difflib
import os
import boto3
import os

# Configuration
URL = 'https://vhs.frankfurt.de/de/service/termine-zum-einburgerungstest'  # The URL you want to monitor
CHECK_ELEMENT_ID = 'ffm-page-default'    # HTML element id, class, or tag to check for changes

# Function to get the webpage content
def fetch_content(url, element_id):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    element = soup.find('div', class_=element_id)  # Adjust to find by class or tag if needed
    # print(element.text.strip())
    return element.text.strip() if element else None

# Function to read file from an S3 bucket
def read_file_from_s3(bucket_name, file_key):
    """
    Reads a file from an S3 bucket and returns its content as a string.
    
    Parameters:
        bucket_name (str): The name of the S3 bucket.
        file_key (str): The key (path) of the file in the S3 bucket.
        
    Returns:
        str: The content of the file.
    """
    try:
        s3_object = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        file_content = s3_object['Body'].read().decode('utf-8')
        return file_content
    except Exception as e:
        print(f"Error reading file from S3: {e}")
        raise e  # Raise the exception to be handled by the calling function

# Function to write file to S3 Bucket
def write_file_to_s3(bucket_name, file_key, content):
    """
    Writes content to a file in an S3 bucket.
    
    Parameters:
        bucket_name (str): The name of the S3 bucket.
        file_key (str): The key (path) of the file in the S3 bucket.
        content (str): The content to write to the file.
    """
    try:
        s3_client.put_object(Bucket=bucket_name, Key=file_key, Body=content)
        print("New content written to S3.")
    except Exception as e:
        print(f"Error writing file to S3: {e}")
        raise e  # Raise the exception to be handled by the calling function


# Function to save content to file
def save_content(content, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

# Function to read content from file
def read_content(file_path):
    if not os.path.exists(file_path):
        return None
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# Function to show notification
# def show_notification(title, message):
#     notification.notify(
#         title=title,
#         message=message,
#         timeout=10
#     )

def normalize_lines(content):
    # strip
    text = [line.strip() for line in content.splitlines() if line != '']

    # remove empty line breaks
    text = [line for line in text if line != '']

    # join with single line break
    text = "\n".join(text)

    return text

# Main monitoring function
def monitor_website():
    try:
        current_content = fetch_content(URL, CHECK_ELEMENT_ID)
        
        if current_content is None:
            print("VHS Frankfurt Monitor - Error: Could not find the specified element on the page.")
            return

        # read last_content from S3 Bucket
        try:
            last_content = read_file_from_s3(bucket_name, read_key)
            last_content = normalize_lines(last_content)
            # print("File content read from S3:")
            # print(last_content)
        except Exception as e:
            try:
                current_content = normalize_lines(current_content)
                write_file_to_s3(bucket_name, write_key, current_content)
                print(f"Initial content saved for future comparison. File stored in {bucket_name}/{write_key}.")
                return
            except Exception as e:
                return {
                    'statusCode': 500,
                    'body': f"Error writing file to S3: {e}"
                }

        
        # Compare current content with the last saved content
        current_content = normalize_lines(current_content)
        if current_content != last_content:
            # Show changes if detected
            diff = difflib.unified_diff(
                last_content.splitlines(),
                current_content.splitlines(),
                lineterm='',
                fromfile='Previous',
                tofile='Current'
            )

            changes = '\n'.join(diff)

            print("VHS Frankfurt Monitor - Content change detected!")
            print(changes)
            print('----------------------------------------')
            print(f"Website URL: {URL}")

            # Update saved content
            # save_content(current_content, FILE_PATH)
        else:
            print("VHS Frankfurt Monitor - No changes detected.")
            # show_notification("VHS Frankfurt Monitor", "No changes in Website Content.")

    except Exception as e:
        print(f"An error occurred: {e}")

# Initialize S3 client
s3_client = boto3.client('s3')

# Constant value assignment
bucket_name = 'web-delta-checker-bucket'
read_key = 'last_content/last_content.txt'
write_key = 'last_content/last_content.txt'


def lambda_handler(event, context):
    # TODO implement
    monitor_website()
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
