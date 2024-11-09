import re
import time
import os

BASE_DIR = '/home/tuya/Taxi_Bot/'

def is_valid_phone_number(phone_number):
    return re.match(r'^\+?\d{9,15}$', phone_number) is not None


def clear_messages_file(file_path="messages.txt"):
    file_path = os.path.join(BASE_DIR, file_path)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write("")


def save_message_to_file(message, file_path="messages.txt"):
    file_path = os.path.join(BASE_DIR, file_path)
    timestamp = str(int(time.time() * 1000))
    message_with_id = f"{timestamp}|{message.replace(chr(10), ' ').strip()}"
    with open(file_path, "a", encoding="utf-8") as file:
        file.write(message_with_id + "\n")
    return timestamp


def get_messages_from_file(file_path="messages.txt"):
    file_path = os.path.join(BASE_DIR, file_path)
    with open(file_path, "r", encoding="utf-8") as file:
        return [msg.strip() for msg in file.readlines()]


def remove_message_from_file(timestamp: str, file_path: str = "messages.txt"):
    file_path = os.path.join(BASE_DIR, file_path)
    messages = get_messages_from_file(file_path)

    matched_message = next((msg for msg in messages if msg.startswith(timestamp)), None)

    if matched_message:
        messages.remove(matched_message)
        with open(file_path, "w", encoding="utf-8") as file:
            for msg in messages:
                file.write(msg + "\n")
    else:
        print(f"Message with timestamp {timestamp} not found in file.")

