import requests
from bs4 import BeautifulSoup
import difflib
import os
from plyer import notification
from notifier import notify
import os

# Configuration
URL = 'https://vhs.frankfurt.de/de/service/termine-zum-einburgerungstest'  # The URL you want to monitor
CHECK_ELEMENT_ID = 'ffm-page-default'    # HTML element id, class, or tag to check for changes

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = r'last_content\last_content.txt'    # File to store the last content state

# Function to get the webpage content
def fetch_content(url, element_id):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    element = soup.find('div', class_=element_id)  # Adjust to find by class or tag if needed
    # print(element.text.strip())
    return element.text.strip() if element else None

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
def show_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        timeout=10
    )

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
        current_content = normalize_lines(current_content)
        if current_content is None:
            print("VHS Frankfurt Monitor - Error: Could not find the specified element on the page.")
            notify.show_persistent_notification(
                title="VHS Frankfurt Monitor",
                message="Error: Could not find the specified element on the page."
            )
            return

        last_content = read_content(os.path.join(ROOT_PATH, FILE_PATH))
        last_content = normalize_lines(last_content)


        if last_content is None:
            # First time setup: Save content and exit
            save_content(current_content, os.path.join(ROOT_PATH, FILE_PATH))
            print("Initial content saved for future comparison.")
            return

        # Compare current content with the last saved content
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

            # Send a persistent notification
            notify.show_persistent_notification(
                title="VHS Frankfurt Monitor",
                message="Integrationstest web page has changed! Register now!"
            )

            # Update saved content
            # save_content(current_content, FILE_PATH)
        else:
            print("VHS Frankfurt Monitor - No changes detected.")
            show_notification("VHS Frankfurt Monitor", "No changes in Website Content.")

    except Exception as e:
        print(f"An error occurred: {e}")
        notify.show_persistent_notification(
                title="VHS Frankfurt Monitor",
                message=f"An error occurred: {e}"
            )
        

# Run the monitor function
if __name__ == "__main__":
    monitor_website()