import logging
import os

import praw
from telegram import Update, Message, MessageEntity
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

log = logging.getLogger(__name__)

reddit = praw.Reddit(
    client_id=os.getenv("reddit_client_id"),
    client_secret=os.getenv("reddit_client_secret"),
    user_agent="telegram:fedalto.reddit_preview_bot:v0.0.1 (by /u/fedalto)",
)


def handle_reddit_post(update: Update, context: CallbackContext):
    message: Message = update.effective_message
    log.debug(f"Handling {message=}")
    urls: dict = message.parse_entities(MessageEntity.URL)
    reddit_url: str = list(urls.values())[0]

    reddit_post = reddit.submission(url=reddit_url)
    log.debug(f"{reddit_post.secure_media=}")
    if "reddit_video" in reddit_post.secure_media:
        video = reddit_post.secure_media["reddit_video"]
        context.bot.send_video(
            chat_id=message.chat_id,
            reply_to_message_id=message.message_id,
            caption=reddit_post.title,
            video=video["fallback_url"],
            duration=video["duration"],
            height=video["height"],
            width=video["width"],
        )


def main():
    updater = Updater(
        token=os.getenv("telegram_token"), use_context=True,
    )
    dispatcher = updater.dispatcher
    reddit_handler = MessageHandler(filters=Filters.text, callback=handle_reddit_post)
    dispatcher.add_handler(reddit_handler)
    log.info("Starting bot")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
