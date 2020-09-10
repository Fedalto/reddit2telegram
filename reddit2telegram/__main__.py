import logging
from logging.config import dictConfig

from reddit2telegram.bot import create_bot
from reddit2telegram.config import settings
from reddit2telegram.log import LOG_CONFIG
from reddit2telegram.reddit import create_reddit_instance

log = logging.getLogger("reddit2telegram")
dictConfig(LOG_CONFIG)

bot = create_bot(settings.telegram_token)

reddit_client = create_reddit_instance(
    settings.reddit_client_id, settings.reddit_client_secret, settings.version
)
bot.dispatcher.bot_data["reddit_client"] = reddit_client

log.info(f"Starting bot {bot.bot.name}")
bot.start_polling()
bot.idle()
