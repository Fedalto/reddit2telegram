import logging

from reddit2telegram.bot import create_bot
from reddit2telegram.config import settings
from reddit2telegram.reddit import create_reddit_instance

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

bot = create_bot(settings.telegram_token)

reddit_client = create_reddit_instance(settings.reddit_client_id, settings.reddit_client_secret, settings.version)
bot.dispatcher.bot_data["reddit_client"] = reddit_client

log.info("Starting bot")
bot.start_polling()
bot.idle()
