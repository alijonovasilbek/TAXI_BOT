from aiogram import Router, types, F, Bot
from config import *
from utils import *
from keyboards import get_admin_buttons, get_driver_buttons, get_main_control_buttons, get_profile_button
import os
from aiogram.filters import Command
from config import BOT_TOKEN
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
import time
import asyncio
from aiogram.exceptions import TelegramBadRequest
import re
from dotenv import load_dotenv

load_dotenv()


ALLOWED_GROUP_IDS = {int(os.getenv("GROUP_IDS1")), int(os.getenv("GROUP_IDS2"))}


ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

router = Router()
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

messages_file_path = "messages.txt"
message_destination = "admin"
admin_authenticated = False
message_id_tracker = {}
last_response_time = {}
RESPONSE_THRESHOLD = 5
BUFFER_TIMEOUT = 0.5
bot_active = True
is_logged_in = False

message_buffer = {}
message_timers = {}

@router.message(Command("login"))
async def login_admin(message: types.Message):
    global is_logged_in
    if message.chat.type != "private":
        await message.reply("Please use this command in a private chat with the bot.")
        return

    password_provided = message.text.split(" ", 1)[1] if len(message.text.split()) > 1 else None
    if password_provided == ADMIN_PASSWORD:
        is_logged_in = True
        await message.reply("Successfully logged in!")
        await message.answer(
            f"Messages will currently be sent to: {message_destination.capitalize()}",
            reply_markup=get_main_control_buttons(bot_active, message_destination)
        )
    else:
        await message.reply("Incorrect password. Please try again.")

@router.message(F.text == "🛑 To'xtatish")
async def stop_bot(message: types.Message):
    global bot_active
    bot_active = False
    await message.answer(
        "Bot to'xtatildi",
        reply_markup=get_main_control_buttons(message_destination, bot_active)
    )

@router.message(F.text == "▶️ Faollashtirish")
async def start_bot(message: types.Message):
    global bot_active
    bot_active = True
    await message.answer(
        "Bot aktivlashtirildi",
        reply_markup=get_main_control_buttons(message_destination, bot_active)
    )

async def admin_only(message: types.Message):
    if not is_logged_in:
        await message.reply("Buyruq mavjud emas.")
        return False
    return True

async def flush_user_buffer(user_id, username, user_chat_id):
    if not bot_active or user_id not in message_buffer:
        return

    base_message = f"👤 {username}:\n" + "\n".join(message_buffer[user_id])

    if message_destination == "admin":
        combined_message = f"{base_message}\n\n<a href='tg://user?id={user_chat_id}'>👉Mijoz profiliga o'tish👈</a>"
        timestamp = save_message_to_file(combined_message)
        sent_message = await bot.send_message(
            ADMIN_CHAT_ID,
            base_message,
            reply_markup=get_admin_buttons(timestamp, user_chat_id),
            parse_mode="HTML"
        )
        message_id_tracker[timestamp] = sent_message.message_id
    else:
        await bot.send_message(
            haydovchilarga_ONLY_GROUP_ID,
            base_message,
            reply_markup=get_driver_buttons(user_chat_id),
            parse_mode="HTML"
        )

    del message_buffer[user_id]
    if user_id in message_timers:
        del message_timers[user_id]

async def add_message_to_buffer(user_id, message_content, username, user_chat_id):
    if user_id not in message_buffer:
        message_buffer[user_id] = []

    message_buffer[user_id].append(message_content)

    if user_id in message_timers:
        message_timers[user_id].cancel()

    message_timers[user_id] = asyncio.create_task(asyncio.sleep(BUFFER_TIMEOUT))
    await message_timers[user_id]

    await flush_user_buffer(user_id, username, user_chat_id)

@router.message(F.text.contains("Jo'natish"))
async def toggle_flow(message: types.Message):
    global message_destination
    if not bot_active:
        await message.reply("Bot hozirda aktiv holarta emas Iltimos uni faollashtiring!")
        return

    message_destination = "haydovchilarga" if message_destination == "admin" else "admin"
    toggle_text = "🚗 Jo'natish: Haydovchilar guruhiga" if message_destination == "haydovchilarga" else "🫅 Jo'natish: Administratorga"
    await message.answer(toggle_text, reply_markup=get_main_control_buttons(message_destination, bot_active))


@router.message(F.text == "hammasini radqilish")
async def radqilish_all_messages(message: types.Message):
    pending_messages = get_messages_from_file(messages_file_path)
    if not pending_messages:
        await message.answer("Rad etish uchun kutilayotgan xabarlar yo‘q.")
        return

    admin_message_ids = []

    for msg in pending_messages:
        try:
            timestamp, message_content = msg.split("|", 1)
            print(f"Processing message with timestamp: {timestamp}")

            user_id = None
            if "?id=" in message_content:
                start_idx = message_content.find("?id=") + 4
                end_idx = message_content.find("'", start_idx)
                user_id = message_content[start_idx:end_idx].strip()
                message_content = message_content.split("(ID:")[0].strip()

            if not user_id:
                print(f"User ID not found in message: {msg}")
                continue

            try:
                user_id = int(user_id)
            except ValueError:
                print(f"Failed to convert user_id '{user_id}' to integer.")
                continue

            cleaned_message_content = re.sub(
                r"<a href='tg://user\?id=\d+'>👉Mijoz profiliga o'tish👈</a>",
                "",
                message_content
            ).strip()
            cleaned_message_content = re.sub(r"(💬)", r"\n\1", cleaned_message_content)



            sent_message = await bot.send_message(
                    haydovchilarga_ONLY_GROUP_ID,
                    cleaned_message_content,
                    reply_markup=get_profile_button(user_id),
                    parse_mode="HTML"
                )




            if timestamp in message_id_tracker:
                admin_message_ids.append(message_id_tracker[timestamp])

            remove_message_from_file(msg, messages_file_path)
            print(f"Message with timestamp {timestamp} removed from file.")

        except Exception as e:
            print(f"Failed to process message {msg}: {e}")

    for message_id in admin_message_ids:
        try:
            await bot.delete_message(ADMIN_CHAT_ID, message_id)
        except Exception as e:
            print(f"Failed to delete message ID {message_id} from admin chat: {e}")

    await message.answer("Barcha xabarlar rad etildi va haydovchilar guruhiga yuborildi.")

    clear_messages_file(messages_file_path)


@router.message(F.text == "hammasini qabulqilish")
async def qabulqilish_all_messages(message: types.Message):
    pending_messages = get_messages_from_file(messages_file_path)
    if not pending_messages:
        await message.answer("Rad etish uchun kutilayotgan xabarlar yo‘q.")
        return

    admin_message_ids = []

    for msg in pending_messages:
        try:
            timestamp, message_content = msg.split("|", 1)
            print(f"Processing message with timestamp: {timestamp}")

            user_id = None
            if "?id=" in message_content:
                start_idx = message_content.find("?id=") + 4
                end_idx = message_content.find("'", start_idx)
                user_id = message_content[start_idx:end_idx].strip()
                message_content = message_content.split("(ID:")[0].strip()

            if not user_id:
                print(f"User ID not found in message: {msg}")
                continue

            try:
                user_id = int(user_id)
            except ValueError:
                print(f"Failed to convert user_id '{user_id}' to integer.")
                continue

            cleaned_message_content = re.sub(
                r"<a href='tg://user\?id=\d+'>👉Mijoz profiliga o'tish👈</a>",
                "",
                message_content
            ).strip()
            cleaned_message_content = re.sub(r"(💬)", r"\n\1", cleaned_message_content)

            sent_message = await bot.send_message(
                ADMIN_CHAT_ID,
                cleaned_message_content,
                reply_markup=get_profile_button(user_id),
                parse_mode="HTML"
            )
            print(f"Message sent to drivers-only group: {cleaned_message_content}")

            if timestamp in message_id_tracker:
                admin_message_ids.append(message_id_tracker[timestamp])

            remove_message_from_file(msg, messages_file_path)
            print(f"Message with timestamp {timestamp} removed from file.")

        except Exception as e:
            print(f"Failed to process message {msg}: {e}")

    for message_id in admin_message_ids:
        try:
            await bot.delete_message(ADMIN_CHAT_ID, message_id)
        except Exception as e:
            print(f"Failed to delete message ID {message_id} from admin chat: {e}")


    await message.answer("Barcha xabarlar administratorga qabul qilindi.")

    # Clear any remaining messages in the file as a final cleanup step
    clear_messages_file(messages_file_path)







async def delete_message_after_delay(message: types.Message, delay: int):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception as e:
        print(f"Failed to delete message: {e}")




@router.message()
async def handle_message(message: types.Message):
    if not bot_active:
        return

    # Guruhdagi ruxsat etilgan xabarlarni qayta ishlash
    if message.chat.id not in ALLOWED_GROUP_IDS:
        return

    user_id = message.from_user.id
    name = f"{message.from_user.first_name or 'restricted_user'}"
    message_content = f"💬 {message.text}"

    # Xabarni keyingi qayta ishlash uchun buferga qo‘shish jarayonini tekshirish
    try:
        await add_message_to_buffer(user_id, message_content, name, user_id)
    except TelegramBadRequest as e:
        if "BUTTON_USER_PRIVACY_RESTRICTED" in str(e):
            print("Xato add_message_to_buffer qatordan chiqdi: Foydalanuvchi maxfiyligi sababli xabar guruhda qoldirildi.")
            return  # Xatolik yuz bersa, xabarni guruhda qoldirish va funksiyadan chiqish
        else:
            raise e  # Boshqa xatolar uchun ko'tarish

    # Xabarni o‘chirish va foydalanuvchiga javob yuborish jarayoni
    try:
        await message.delete()

        current_time = time.time()
        if user_id not in last_response_time or (current_time - last_response_time[user_id] > RESPONSE_THRESHOLD):
            last_response_time[user_id] = current_time
            sent_message = await message.answer(
                "Sizning zakazingiz qabul qilindi!\nLichkangizga qarang.\nВаш заказ успешно получен!\nB личке ждём вас."
            )
            # Javob xabarini keyinchalik o'chirish uchun vaqtni belgilash (ixtiyoriy)
            asyncio.create_task(delete_message_after_delay(sent_message, 15))

    except TelegramBadRequest as e:
        if "BUTTON_USER_PRIVACY_RESTRICTED" in str(e):
            print("Xato message.delete() yoki message.answer(...) qatordan chiqdi: Foydalanuvchi maxfiyligi sababli.")
            return  # Xatolik yuz bersa, funksiyadan chiqish
        else:
            raise e  # Boshqa xatolar uchun ko'tarish







@router.callback_query(F.data.startswith(("qabulqilish", "radqilish")))
async def process_callback(callback_query: types.CallbackQuery):
    if not bot_active:
        await callback_query.answer("Bot hozirda to'xtatilgan. Iltimos, uni faollashtiring.")
        return

    action, message_id = callback_query.data.split("_")
    message_content = next(
        (msg.split("|", 1)[1] for msg in get_messages_from_file() if msg.startswith(message_id)),
        None
    )

    if message_content is None:
        await callback_query.answer("Xabar topilmadi.")
        return

    user_id = None
    if "?id=" in message_content:
        start_idx = message_content.find("?id=") + 4
        end_idx = message_content.find("'", start_idx)
        user_id = message_content[start_idx:end_idx].strip()

    cleaned_message_content = re.sub(r"<a href='tg://user\?id=\d+'>👉Mijoz profiliga o'tish👈</a>", "", message_content).strip()
    cleaned_message_content = re.sub(r"(💬)", r"\n\1", cleaned_message_content)

    if action == "qabulqilish":
        if user_id:
            await bot.send_message(
                ADMIN_CHAT_ID,
                cleaned_message_content,
                reply_markup=get_profile_button(int(user_id)),
                parse_mode="HTML"
            )
        await callback_query.answer("Xabar qabul qilindi va saqlandi.")
        remove_message_from_file(message_id, messages_file_path)
        try:
            await callback_query.message.delete()
        except Exception as e:
            print(f"Failed to delete message: {e}")


    elif action == "radqilish":
        if user_id:
            await bot.send_message(
                haydovchilarga_ONLY_GROUP_ID,
                cleaned_message_content,
                reply_markup=get_profile_button(int(user_id)),
                parse_mode="HTML"
            )
        await callback_query.answer("Xabar rad etildi va haydovchilar guruhiga yuborildi.")
        remove_message_from_file(message_id, messages_file_path)

        try:
            await callback_query.message.delete()
        except Exception as e:
            print(f"Failed to delete message: {e}")

    try:
        await callback_query.message.edit_reply_markup(reply_markup=None)
    except Exception as e:
        print(f"Failed to edit reply markup for message ID {callback_query.message.message_id}: {e}")

    await callback_query.message.edit_reply_markup(
        reply_markup=get_main_control_buttons(message_destination, bot_active))
