import re

import time

def is_valid_phone_number(phone_number):
    return re.match(r'^\+?\d{9,15}$', phone_number) is not None


def clear_messages_file(file_path="messages.txt"):
    with open(file_path, "w", encoding="utf-8") as file:
        file.write("")




def save_message_to_file(message, file_path="messages.txt"):
    timestamp = str(int(time.time() * 1000))
    message_with_id = f"{timestamp}|{message.replace('\n', ' ').strip()}"
    with open(file_path, "a", encoding="utf-8") as file:
        file.write(message_with_id + "\n")
    return timestamp



def get_messages_from_file(file_path="messages.txt"):
    with open(file_path, "r", encoding="utf-8") as file:
        return [msg.strip() for msg in file.readlines()]


def remove_message_from_file(timestamp: str, file_path: str = "messages.txt"):
    # Read all messages from the file
    messages = get_messages_from_file(file_path)

    # Locate the message that starts with the specified timestamp
    matched_message = next((msg for msg in messages if msg.startswith(timestamp)), None)

    if matched_message:
        messages.remove(matched_message)
        print(f"Removed message: {matched_message}")

        # Write remaining messages back to the file
        with open(file_path, "w", encoding="utf-8") as file:
            for msg in messages:
                file.write(msg + "\n")
    else:
        print(f"Message with timestamp {timestamp} not found in file.")
