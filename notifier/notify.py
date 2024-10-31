import time
from plyer import notification

def show_persistent_notification(title, message):
    notification_sent = False
    
    while not notification_sent:
        # Show the notification
        notification.notify(
            title=title,
            message=message,
            app_name="My App",
            timeout=10  # Timeout in seconds
        )
        
        # Wait before showing it again (for example, every 30 seconds)
        time.sleep(10)

        # Condition to stop the notification loop (for example, user input)
        user_input = input("Type 'dismiss' to stop notifications: ")
        if user_input.lower() == 'dismiss':
            notification_sent = True

# Run the persistent notification
# show_persistent_notification()
