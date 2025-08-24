from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis
from loguru import logger

from core.config import settings


# Initialize Redis
redis = Redis.from_url(settings.redis_url, decode_responses=True)

# Initialize Bot
bot = Bot(
    token=settings.TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

# Initialize Storage
storage = RedisStorage(redis)

# Initialize Dispatcher
dp = Dispatcher(storage=storage)


async def setup_bot():
    """Setup bot configuration"""
    try:
        # Delete webhook to use long polling
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Bot setup completed - using long polling")
        
        # Get bot info
        bot_info = await bot.get_me()
        logger.info(f"Bot started: @{bot_info.username}")
        
    except Exception as e:
        logger.error(f"Failed to setup bot: {e}")
        raise


async def shutdown_bot():
    """Cleanup bot resources"""
    try:
        await bot.session.close()
        await redis.close()
        logger.info("Bot shutdown completed")
    except Exception as e:
        logger.error(f"Error during bot shutdown: {e}")