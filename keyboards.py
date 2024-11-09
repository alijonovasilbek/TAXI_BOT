from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram import types

bot_active=True

def get_admin_buttons(message_id: int, user_chat_id: int) -> InlineKeyboardMarkup:
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
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Chatga o'tish", url=f"tg://user?id={user_chat_id}")
        ]
    ])




def get_main_control_buttons(current_flow: str,bot_active:bool) -> ReplyKeyboardMarkup:
    if current_flow == "admin":

        toggle_text = "🫅 Jo'natish Admin"
    else:
        toggle_text = "🚗 Jo'natish haydovchilarga"

    toggle_button = KeyboardButton(text=toggle_text)
    qabulqilish_all_button = KeyboardButton(text="hammasini qabulqilish")
    radqilish_all_button = KeyboardButton(text="hammasini radqilish")

    if bot_active:
        status_button = KeyboardButton(text="🛑 To'xtatish")
    else:
        status_button = KeyboardButton(text="▶️ Faollashtirish")

    return ReplyKeyboardMarkup(
        keyboard=[[toggle_button,status_button], [qabulqilish_all_button, radqilish_all_button]],
        resize_keyboard=True,
        one_time_keyboard=False
    )


def get_profile_button(user_chat_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Chatga O'tish", url=f"tg://user?id={user_chat_id}")
        ]
    ])

