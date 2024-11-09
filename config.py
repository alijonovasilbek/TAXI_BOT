from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID'))
haydovchilarga_ONLY_GROUP_ID = -1002456657753
DATABASE_PATH = os.getenv("DATABASE_PATH", "telegram_bot.db")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

GROUP_IDS1 = int(os.getenv('GROUP_IDS1'))
GROUP_IDS2 = int(os.getenv('GROUP_IDS2'))

GROUP_IDS = [GROUP_IDS1, GROUP_IDS2]
