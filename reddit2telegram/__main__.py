import logging

import sentry_sdk
from telegram.error import NetworkError

from reddit2telegram.bot import create_bot
from reddit2telegram.config import settings
from reddit2telegram.handlers.reddit import create_reddit_instance
from reddit2telegram.log import configure_logging

logger = logging.getLogger("reddit2telegram")


def filter_errors(event, hint):
    err = hint["originalException"]
    if err and isinstance(err, NetworkError):
        logger.warning(f"Network error. exc={err}")
        return None
    return event


def configure_sentry():
    sentry_sdk.init(
        traces_sample_rate=1.0,
        release=str(settings.version),
        before_send=filter_errors,
    )


def main():
    configure_sentry()
    configure_logging()

    bot = create_bot(settings.telegram_token)

    reddit_client = create_reddit_instance(
        settings.reddit_client_id, settings.reddit_client_secret, str(settings.version)
    )
    bot.dispatcher.bot_data["reddit_client"] = reddit_client

    logger.info(f"Starting bot {bot.bot.name}")
    bot.start_polling()
    bot.idle()


main()
