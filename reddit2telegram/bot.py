import logging
from typing import List
from urllib.parse import urlparse

from telegram import Update, Message, MessageEntity
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

from reddit2telegram.preview import VideoPreview, ImagePreview
from reddit2telegram.reddit import create_preview_from_reddit

log = logging.getLogger(__name__)


def create_bot(token: str) -> Updater:
    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher
    reddit_handler = MessageHandler(filters=Filters.text, callback=handle_reddit_post)
    dispatcher.add_handler(reddit_handler)

    return updater


def is_from_reddit(url: str) -> bool:
    domain = urlparse(url).netloc
    return domain in ["www.reddit.com", "redd.it"]


def handle_reddit_post(update: Update, context: CallbackContext):
    message: Message = update.effective_message

    reddit_client = context.bot_data["reddit_client"]
    urls = message.parse_entities(MessageEntity.URL).values()
    reddit_urls = filter(is_from_reddit, urls)

    for reddit_url in reddit_urls:
        preview = create_preview_from_reddit(reddit_client, reddit_url)
        log.debug(f"Sending {preview=}")

        if isinstance(preview, VideoPreview):
            context.bot.send_video(
                chat_id=message.chat_id,
                reply_to_message_id=message.message_id,
                caption=preview.title,
                video=preview.video_url,
                duration=preview.duration,
                height=preview.height,
                width=preview.width,
            )
        elif isinstance(preview, ImagePreview):
            context.bot.send_photo(
                chat_id=message.chat_id,
                reply_to_message_id=message.message_id,
                caption=preview.title,
                photo=preview.image_url,
            )
        else:
            log.warning(f"URL not supported: url={reddit_url}")
