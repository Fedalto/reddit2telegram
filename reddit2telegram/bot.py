import logging

import sentry_sdk
from telegram import Update, Message, MessageEntity
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, Dispatcher

from reddit2telegram.preview import VideoPreview, ImagePreview
from reddit2telegram.handlers.reddit import create_preview_from_reddit, is_from_reddit

log = logging.getLogger(__name__)


def create_bot(token: str) -> Updater:
    updater = Updater(token=token, use_context=True)
    dispatcher: Dispatcher = updater.dispatcher
    dispatcher.add_handler(
        MessageHandler(filters=Filters.entity(MessageEntity.URL), callback=url_handler)
    )
    dispatcher.add_error_handler(error_handler)

    return updater


def error_handler(update: Update, context: CallbackContext):
    with sentry_sdk.push_scope() as sentry_scope:
        sentry_scope.set_user({"id": update.effective_chat.id})
        sentry_scope.set_level("error")
        sentry_scope.set_context("update", update.to_dict())
        sentry_sdk.capture_exception(context.error)


def url_handler(update: Update, context: CallbackContext):
    message: Message = update.effective_message

    urls = message.parse_entities(MessageEntity.URL).values()

    for url in urls:
        if is_from_reddit(url):
            reddit_client = context.bot_data["reddit_client"]
            preview = create_preview_from_reddit(reddit_client, url)
            if not preview:
                log.warning(f"URL not supported: url={url}")
                continue

            send_preview(preview, message, context)


def send_preview(preview, message: Message, context: CallbackContext):
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
