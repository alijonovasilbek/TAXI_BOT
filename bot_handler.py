from aiogram import Router, types, F, Bot
from config import *
from utils import *
from keyboards import get_admin_buttons,get_driver_buttons, get_main_control_buttons
import os
from aiogram.filters import Command
from config import BOT_TOKEN
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
import time
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")



router = Router()
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

# Initialize global state variables
messages_file_path = "messages.txt"
message_destination = "admin"
admin_authenticated = False
message_id_tracker = {}
last_response_time = {}
RESPONSE_THRESHOLD = 5

# Buffer for collecting messages per user
message_buffer = {}
message_timers = {}
BUFFER_TIMEOUT = 5



# Login command handler
@router.message(Command("login"))
async def login_admin(message: types.Message):
    global is_logged_in

    # Ensure the login command is only used in private chat
    if message.chat.type != "private":
        await message.reply("Iltimos, bot bilan shaxsiy suhbatda ushbu buyruqdan foydalaning.")
        return

    # Extract password from the command
    password_provided = message.text.split(" ", 1)[1] if len(message.text.split()) > 1 else None

    # Check if the password is correct
    if password_provided == ADMIN_PASSWORD:
        is_logged_in = True
        await message.reply("Kirish muvaffaqiyatli!")
        await message.answer(
            f"Hozirda xabarlar yuboriladi: {message_destination.capitalize()} ga",
            reply_markup=get_main_control_buttons(message_destination)
        )
    else:
        await message.reply("Xato parol. Iltimos, qaytadan urinib ko‘ring.")

# Function to ensure only logged-in admin can access certain commands
async def admin_only(message: types.Message):
    global is_logged_in
    if not is_logged_in:
        await message.reply("Buyruq mavjud emas.")
        return False
    return True






async def flush_user_buffer(user_id, username, user_chat_id):
    """Send buffered messages to the admin or drivers after timeout."""
    # Combine messages without the 'ID' label for simplicity
    base_message = f"👤 {username}:\n" + "\n".join(message_buffer[user_id])

    # Check the message destination and format accordingly
    if message_destination == "admin":
        # Add "Chatga o'tish" link for admin chat using HTML
        combined_message = f"{base_message}\n\n<a href='tg://user?id={user_chat_id}'>Profilga o'tish 👉</a>"
    else:
        # Use plain text for the link in drivers-only group
        combined_message = f"{base_message}\n\n<a href='tg://user?id={user_chat_id}'>Profilga o'tish 👉</a>"

    # Save the message to file with a timestamp for tracking
    timestamp = save_message_to_file(combined_message)

    # Send the combined message based on the destination
    if message_destination == "admin":
        # Send to admin chat with approval buttons and HTML formatting
        sent_message = await bot.send_message(
            ADMIN_CHAT_ID,
            combined_message,
            reply_markup=get_admin_buttons(timestamp, user_chat_id),
            parse_mode="HTML"  # Use HTML to make the link clickable
        )
        message_id_tracker[timestamp] = sent_message.message_id
    else:
        # Send to drivers-only group with plain text format
        await bot.send_message(
            haydovchilarga_ONLY_GROUP_ID,
            combined_message,
            parse_mode="HTML"  # Use HTML to make the link clickable
        )

    # Clear the user's message buffer and timer
    del message_buffer[user_id]
    del message_timers[user_id]



async def add_message_to_buffer(user_id, message_content, username, user_chat_id):
    """Add a message to the buffer for a user, setting a timer to send them as one message."""
    if user_id not in message_buffer:
        message_buffer[user_id] = []

    # Add the message to the buffer
    message_buffer[user_id].append(message_content)

    # If a timer is already running for this user, cancel it
    if user_id in message_timers:
        message_timers[user_id].cancel()

    # Start a new timer to flush the buffer after `BUFFER_TIMEOUT`
    message_timers[user_id] = asyncio.create_task(asyncio.sleep(BUFFER_TIMEOUT))
    await message_timers[user_id]

    # Once the timer expires, flush the buffer
    await flush_user_buffer(user_id, username, user_chat_id)



@router.message(F.text.contains("Jo'natish"))
async def toggle_flow(message: types.Message):
    global message_destination
    if message_destination == "admin":
        message_destination = "haydovchilarga"
        toggle_text = "🚗 Jo'natish: Haydovchilar guruhiga"
    else:
        message_destination = "admin"
        toggle_text = "🫅 Jo'natish: Administratorga"
    await message.answer(toggle_text, reply_markup=get_main_control_buttons(message_destination))



@router.message(F.text == "hammasini qabulqilish")
async def qabulqilish_all_messages(message: types.Message):
    pending_messages = get_messages_from_file(messages_file_path)
    if not pending_messages:
        await message.answer("Qabul qilish uchun kutilayotgan xabarlar yo‘q.")
        return

    for msg in pending_messages:
        timestamp, message_content = msg.split("|", 1)

        # Extract user ID if present in the format
        user_id = None
        if "(ID:" in message_content:
            start_idx = message_content.find("(ID:") + 4
            end_idx = message_content.find(")", start_idx)
            user_id = message_content[start_idx:end_idx].strip()
            message_content = message_content.split("(ID:")[0].strip()  # Exclude everything after and including "(ID:"

        # Format message content without icons at the start or end, each line with "💬"
        formatted_message_content = "\n".join(
            f"{line.strip()}" for line in message_content.split("💬") if line.strip()
        )

        # Add "Profilga o'tish" link at the end on a new line
        if user_id:
            formatted_message_content += f"\n\n<a href='tg://user?id={user_id}'>Profilga o'tish 👉</a>"

        await bot.send_message(ADMIN_CHAT_ID, formatted_message_content, parse_mode="HTML")

    # Clear messages from file after sending to admin
    clear_messages_file(messages_file_path)
    await message.answer("Barcha xabarlar administratorga qabul qilindi.")




@router.message(F.text == "hammasini radqilish")
async def radqilish_all_messages(message: types.Message):
    pending_messages = get_messages_from_file(messages_file_path)
    if not pending_messages:
        await message.answer("Rad etish uchun kutilayotgan xabarlar yo‘q.")
        return

    for msg in pending_messages:
        timestamp, message_content = msg.split("|", 1)

        # Extract user ID if present in the format
        user_id = None
        if "(ID:" in message_content:
            start_idx = message_content.find("(ID:") + 4
            end_idx = message_content.find(")", start_idx)
            user_id = message_content[start_idx:end_idx].strip()
            message_content = message_content.split("(ID:")[0].strip()  # Exclude everything after and including "(ID:"

        # Format message content without icons at the start or end, each line with "💬"
        formatted_message_content = "\n".join(
            f"{line.strip()}" for line in message_content.split("💬") if line.strip()
        )

        # Add "Profilga o'tish" link at the end on a new line
        if user_id:
            formatted_message_content += f"\n\n<a href='tg://user?id={user_id}'>Profilga o'tish 👉</a>"

        # Send to drivers-only group
        await bot.send_message(
            haydovchilarga_ONLY_GROUP_ID,
            formatted_message_content,
            parse_mode="HTML"
        )

        # Check if we have a message ID stored for this message to delete it from the admin chat
        message_id = message_id_tracker.get(timestamp)
        if message_id:
            try:
                # Attempt to delete the message from the admin chat
                await bot.delete_message(ADMIN_CHAT_ID, message_id)
            except Exception as e:
                print(f"Failed to delete message ID {message_id} from admin chat: {e}")

        # Remove each message from the file
        remove_message_from_file(msg, messages_file_path)

    # Notify the admin about the completion of the action
    await message.answer("Barcha xabarlar rad etildi va haydovchilar guruhiga yuborildi.")

    # Clear any remaining messages from the file just in case
    clear_messages_file(messages_file_path)



@router.message()
async def handle_message(message: types.Message):
    if message.chat.id == ADMIN_CHAT_ID:
        await message.reply("Bunday buyruq yo‘q")
        await  message.delete()
        return
    user_id = message.from_user.id
    username = f"@{message.from_user.username}" if message.from_user.username else "Anonymous"
    message_content = f"💬 {message.text}"

    await message.delete()

    current_time = time.time()
    if user_id not in last_response_time or (current_time - last_response_time[user_id] > RESPONSE_THRESHOLD):
        last_response_time[user_id] = current_time
        await message.answer(f"✅ {message.from_user.first_name}\nSizning so'rovingiz muvaffaqiyatli qabul qilindi!")

    await add_message_to_buffer(user_id, message_content, username, user_id)





@router.callback_query(F.data.startswith(("qabulqilish", "radqilish")))
async def process_callback(callback_query: types.CallbackQuery):
    action, message_id = callback_query.data.split("_")
    message_content = callback_query.message.text
    print(message_content)

    # Extract user ID from the original message content for creating the link
    user_id = None
    if "(ID:" in message_content:
        start_idx = message_content.find("(ID:") + 4
        end_idx = message_content.find(")", start_idx)
        user_id = message_content[start_idx:end_idx].strip()

    # Remove message from file using timestamp
    remove_message_from_file(message_id, messages_file_path)

    if action == "qabulqilish":
        await callback_query.answer("Xabar qabul qilindi va saqlandi.")
    elif action == "radqilish":
        # Append "Chatga o'tish" link if user ID was found
        if user_id :
            message_content += f"\n\n<a href=\"tg://user?id={user_id}\">Chatga o'tish</a>"

        # Send to drivers-only group
        await bot.send_message(
            haydovchilarga_ONLY_GROUP_ID,
            message_content,
            parse_mode="HTML"
        )
        await callback_query.answer("Xabar rad etildi va haydovchilar guruhiga yuborildi.")

        # Attempt to delete the message from admin chat
        try:
            await callback_query.message.delete()
        except Exception as e:
            print(f"Failed to delete message: {e}")

    # Attempt to edit the markup safely (removing the buttons)
    try:
        await callback_query.message.edit_reply_markup(reply_markup=None)
    except Exception as e:
        print(f"Failed to edit reply markup for message ID {callback_query.message.message_id}: {e}")


