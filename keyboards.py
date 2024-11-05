from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
# from  bot_handler import  bot_active

bot_active=True

def get_admin_buttons(message_id: int, user_chat_id: int) -> InlineKeyboardMarkup:
    # Admin buttons with approval options and chat link
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="qabul qilish", callback_data=f"qabulqilish_{message_id}"),
            InlineKeyboardButton(text="rad qilish", callback_data=f"radqilish_{message_id}")
        ],
        [
            InlineKeyboardButton(text="Chatga o'tish", url=f"tg://user?id={user_chat_id}")
        ]
    ])

def get_driver_buttons(user_chat_id: int) -> InlineKeyboardMarkup:
    # Drivers-only button with just the chat link
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Chatga o'tish", url=f"tg://user?id={user_chat_id}")
        ]
    ])

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_control_buttons(current_flow: str) -> ReplyKeyboardMarkup:
    # Set button text with appropriate emojis for the current flow
    if current_flow == "admin":

        toggle_text = "🫅 Jo'natish Admin"  # Emoji indicates sending to Admin
    else:
        toggle_text = "🚗 Jo'natish haydovchilarga"  # Emoji indicates sending to Drivers

    # Create buttons
    toggle_button = KeyboardButton(text=toggle_text)
    qabulqilish_all_button = KeyboardButton(text="hammasini qabulqilish")
    radqilish_all_button = KeyboardButton(text="hammasini radqilish")

    if bot_active:
        status_button = KeyboardButton(text="🛑 To'xtatish")  # Botni to'xtatish
    else:
        status_button = KeyboardButton(text="▶️ Faollashtirish")  # Botni faollashtirish

    # Return keyboard layout
    return ReplyKeyboardMarkup(
        keyboard=[[toggle_button,status_button], [qabulqilish_all_button, radqilish_all_button]],
        resize_keyboard=True,
        one_time_keyboard=False
    )


