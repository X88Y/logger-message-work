import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram API credentials for user bot
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
USER_SESSION = os.getenv("USER_SESSION", "user_bot")

# Telegram Bot API credentials
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Target users who will receive message info (list of user IDs)
TARGET_USERS = [
    # Add target user IDs here, example:
    # 123456789,
    # 987654321,
    7517848621
]

# Chat filters (optional)
EXCLUDED_CHATS = [
    # Add chat IDs to exclude from monitoring, example:
    # -1001234567890,
]

# Message content filters
MIN_MESSAGE_LENGTH = 1  # Minimum message length to process
INCLUDE_MEDIA = True    # Whether to include media messages
INCLUDE_PRIVATE_CHATS = True  # Whether to monitor private chats
INCLUDE_GROUPS = True   # Whether to monitor groups
INCLUDE_CHANNELS = True # Whether to monitor channels

# Logging
LOG_LEVEL = "INFO" 