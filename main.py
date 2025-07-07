#!/usr/bin/env python3
"""
Telegram User Bot - Message Monitor
Monitors all chats using Pyrogram and sends message info via Aiogram bot.
"""

import asyncio
import logging
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message as PyrogramMessage
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message as AiogramMessage
from config import (
    API_ID, API_HASH, USER_SESSION,
    BOT_TOKEN,
    TARGET_USERS, EXCLUDED_CHATS,
    MIN_MESSAGE_LENGTH, INCLUDE_MEDIA,
    INCLUDE_PRIVATE_CHATS, INCLUDE_GROUPS, INCLUDE_CHANNELS,
    LOG_LEVEL
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Pyrogram user bot
user_bot = Client(
    name=USER_SESSION,
    api_id=API_ID,
    api_hash=API_HASH
)

# Initialize Aiogram bot and dispatcher
aiogram_bot = Bot(token=BOT_TOKEN)

# Global variable to store aiogram bot instance for access in pyrogram handlers
bot_instance = None

async def format_message_info(message: PyrogramMessage) -> str:
    """Format message information for reporting."""
    info_parts = []
    
    # Basic message info
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    info_parts.append(f"🕒 *Time:* {timestamp}")
    
    # Chat information
    chat = message.chat
    if chat:
        chat_type = chat.type.value if chat.type else "unknown"
        chat_title = chat.title or chat.first_name or "Unknown"
        chat_username = f"@{chat.username}" if chat.username else "No username"
        
        # Escape markdown characters
        chat_title = chat_title.replace('*', '\\*').replace('_', '\\_').replace('`', '\\`')
        
        info_parts.append(f"💬 *Chat:* {chat_title}")
        info_parts.append(f"🏷️ *Type:* {chat_type.title()}")
        info_parts.append(f"🔗 *Username:* {chat_username}")
        info_parts.append(f"🆔 *Chat ID:* `{chat.id}`")
    
    # Sender information
    sender = message.from_user
    if sender:
        sender_name = f"{sender.first_name or ''} {sender.last_name or ''}".strip()
        sender_username = f"@{sender.username}" if sender.username else "No username"
        
        # Escape markdown characters
        sender_name = sender_name.replace('*', '\\*').replace('_', '\\_').replace('`', '\\`')
        
        info_parts.append(f"👤 *Sender:* {sender_name}")
        info_parts.append(f"🔗 *Sender Username:* {sender_username}")
        info_parts.append(f"🆔 *Sender ID:* `{sender.id}`")
    
    # Message content
    if message.text:
        text_preview = message.text[:200] + "..." if len(message.text) > 200 else message.text
        # Escape markdown characters in text
        text_preview = text_preview.replace('*', '\\*').replace('_', '\\_').replace('`', '\\`')
        info_parts.append(f"📝 *Text:* {text_preview}")
    
    # Media information
    if message.media:
        media_type = str(message.media).split('.')[-1] if message.media else "unknown"
        info_parts.append(f"📎 *Media:* {media_type.upper()}")
        
        if message.caption:
            caption_preview = message.caption[:100] + "..." if len(message.caption) > 100 else message.caption
            # Escape markdown characters in caption
            caption_preview = caption_preview.replace('*', '\\*').replace('_', '\\_').replace('`', '\\`')
            info_parts.append(f"📄 *Caption:* {caption_preview}")
    
    # Additional info
    if message.reply_to_message:
        info_parts.append("↩️ *Reply:* This is a reply to another message")
    
    if message.forward_from or message.forward_from_chat:
        info_parts.append("🔄 *Forwarded:* This is a forwarded message")
    
    info_parts.append(f"🔗 *Message ID:* `{message.id}`")
    
    return "\n".join(info_parts)

def should_process_message(message: PyrogramMessage) -> bool:
    """Determine if a message should be processed based on filters."""
    
    # Skip if no chat
    if not message.chat:
        return False
    
    # Skip excluded chats
    if message.chat.id in EXCLUDED_CHATS:
        return False
    
    # Check chat type filters
    if message.chat.type:
        chat_type = message.chat.type.value
        if chat_type == "private" and not INCLUDE_PRIVATE_CHATS:
            return False
        elif chat_type in ["group", "supergroup"] and not INCLUDE_GROUPS:
            return False
        elif chat_type == "channel" and not INCLUDE_CHANNELS:
            return False
    
    # Check message length
    if message.text and len(message.text) < MIN_MESSAGE_LENGTH:
        return False
    
    # Check media inclusion
    if message.media and not INCLUDE_MEDIA:
        return False
    
    return True

@user_bot.on_message(filters.all)
async def handle_message(client: Client, message: PyrogramMessage):
    print(message)
    """Handle incoming messages from all chats."""
    try:
        # Skip if message doesn't meet criteria
        if not should_process_message(message):
            return
        
        # Skip messages from self
        if message.from_user and message.from_user.is_self:
            return
        
        logger.info(f"Processing message from chat: {message.chat.id}")
        
        # Format message information
        message_info = await format_message_info(message)
        
        # Send to target users via aiogram bot
        for user_id in TARGET_USERS:
            try:
                await aiogram_bot.send_message(
                    chat_id=user_id,
                    text=f"📨 *New Message Detected*\n\n{message_info}",
                    parse_mode="MarkdownV2"
                )
                logger.info(f"Message info sent to user: {user_id}")
            except Exception as e:
                logger.error(f"Failed to send message to user {user_id}: {e}")
    
    except Exception as e:
        logger.error(f"Error handling message: {e}")

async def main():
    """Main function to run both bots."""
    logger.info("Starting Telegram Message Monitor...")
    
    # Validate configuration
    if not API_ID or not API_HASH:
        logger.error("API_ID and API_HASH must be configured!")
        return
    
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN must be configured!")
        return
    
    if not TARGET_USERS:
        logger.warning("No target users configured! Please add user IDs to TARGET_USERS in config.py")
    
    user_bot.run()
 
if __name__ == "__main__":
    asyncio.run(main()) 