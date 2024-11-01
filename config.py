from dotenv import load_dotenv
import os

load_dotenv()  

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv('ADMIN_CHAT_ID'))
haydovchilarga_ONLY_GROUP_ID = int(os.getenv('haydovchilarga_ONLY_GROUP_ID'))
# USERS_AND_haydovchilarga_GROUP_ID = int(os.getenv('USERS_AND_haydovchilarga_GROUP_ID'))
DATABASE_PATH = os.getenv("DATABASE_PATH", "telegram_bot.db")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# # Parse the group IDs from a string into a list of integers
# GROUP_IDS = [int(id.strip()) for id in os.getenv("GROUP_IDS", "").strip("[]").split(",") if id.strip()]

GROUP_IDS1 = int(os.getenv('GROUP_IDS1'))
GROUP_IDS2 = int(os.getenv('GROUP_IDS2'))

GROUP_IDS = [GROUP_IDS1, GROUP_IDS2]