import logging
from typing import List

from telegram import Update, Message, MessageEntity
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

from reddit2telegram.preview import VideoPreview, ImagePreview
from reddit2telegram.reddit import reddit_preview

log = logging.getLogger(__name__)


def create_bot(token: str) -> Updater:
    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher
    reddit_handler = MessageHandler(filters=Filters.text, callback=handle_reddit_post)
    dispatcher.add_handler(reddit_handler)

    return updater


def handle_reddit_post(update: Update, context: CallbackContext):
    message: Message = update.effective_message
    log.debug(f"Handling {message=}")

    reddit_client = context.bot_data["reddit_client"]
    reddit_urls = parse_urls(message)

    for reddit_url in reddit_urls:
        preview = reddit_preview(reddit_client, reddit_url)

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


def parse_urls(message: Message) -> List[str]:
    urls_entities: dict = message.parse_entities(MessageEntity.URL)
    return list(urls_entities.values())
