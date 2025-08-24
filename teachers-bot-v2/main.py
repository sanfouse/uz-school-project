import asyncio
import logging
import sys
from contextlib import asynccontextmanager

from loguru import logger

from core.bot import dp, bot, setup_bot, shutdown_bot
from core.config import settings
from services.notification_handler import notification_handler

# Import handlers to register them
import handlers.main_menu
import handlers.registration
import handlers.lessons
import handlers.finance
import handlers.profile


def register_handlers():
    """Register all handlers with the dispatcher"""
    dp.include_router(handlers.main_menu.router)
    dp.include_router(handlers.registration.router)
    dp.include_router(handlers.lessons.router)
    dp.include_router(handlers.finance.router)
    dp.include_router(handlers.profile.router)


async def setup_logging():
    """Setup logging configuration"""
    logger.remove()  # Remove default handler
    
    # Add console logging
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    # Add file logging for production
    if not settings.DEBUG:
        logger.add(
            "logs/bot.log",
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="1 day",
            retention="30 days"
        )


async def main():
    """Main application entry point"""
    try:
        # Setup logging
        await setup_logging()
        logger.info("Starting Teachers Bot v2.0")
        
        # Register handlers
        register_handlers()
        logger.info("Handlers registered")
        
        # Setup bot
        await setup_bot()
        
        # Start notification handler in background
        notification_task = asyncio.create_task(notification_handler.start_listening())
        logger.info("Notification handler started")
        
        # Start bot polling
        logger.info("Starting bot polling...")
        polling_task = asyncio.create_task(dp.start_polling(bot, skip_updates=True))
        
        try:
            await polling_task
        except (KeyboardInterrupt, asyncio.CancelledError):
            logger.info("Bot stopped by user")
        finally:
            # Cancel tasks
            polling_task.cancel()
            notification_task.cancel()
            
            # Wait for tasks to complete
            await asyncio.gather(polling_task, notification_task, return_exceptions=True)
            
            # Stop notification handler
            await notification_handler.stop_listening()
            logger.info("Notification handler stopped")
        
    except Exception as e:
        logger.error(f"Critical error: {e}")
        sys.exit(1)
    finally:
        # Cleanup
        await shutdown_bot()
        logger.info("Bot shutdown completed")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
    except Exception as e:
        print(f"Application crashed: {e}")
        sys.exit(1)