import logging
from typing import Optional

import sentry_sdk
from telegram import Update, Message, MessageEntity
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, Dispatcher

from reddit2telegram.handlers.reddit import create_preview_from_reddit, is_from_reddit

log = logging.getLogger(__name__)


def create_bot(token: str) -> Updater:
    updater = Updater(token=token)
    dispatcher: Dispatcher = updater.dispatcher

    dispatcher.add_handler(
        MessageHandler(filters=Filters.entity(MessageEntity.URL), callback=url_handler)
    )
    dispatcher.add_error_handler(error_handler)

    return updater


def error_handler(update: Optional[Update], context: CallbackContext):
    if update:
        log.exception(
            f"Error handling update = {update.to_dict()}", exc_info=context.error
        )

        with sentry_sdk.push_scope() as sentry_scope:
            sentry_scope.set_level("error")
            sentry_scope.set_user({"id": update.effective_chat.id})
            sentry_scope.set_context("update", update.to_dict())
            sentry_sdk.capture_exception(context.error)
    else:
        log.exception("Error", exc_info=context.error)

        with sentry_sdk.push_scope() as sentry_scope:
            sentry_scope.set_level("error")
            sentry_sdk.capture_exception(context.error)


def url_handler(update: Update, context: CallbackContext):
    message: Message = update.effective_message

    urls = message.parse_entities([MessageEntity.URL]).values()

    for url in urls:
        if is_from_reddit(url):
            reddit_client = context.bot_data["reddit_client"]

            preview = create_preview_from_reddit(reddit_client, url)
            if preview:
                send_preview(preview, message, context)
            else:
                log.warning(f"URL not supported: {url=}")


def send_preview(preview, message: Message, context: CallbackContext):
    log.debug(f"Sending {preview=}")
    preview.send(message, context)
