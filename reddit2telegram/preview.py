import logging
from dataclasses import dataclass
from io import BytesIO
from typing import Optional

import requests
from telegram import Message
from telegram.error import TelegramError
from telegram.ext import CallbackContext

log = logging.getLogger(__name__)


@dataclass
class ImagePreview:
    title: str
    image_url: str

    def send(self, message: Message, context: CallbackContext):
        send_by_url_max_size = 5 * 1024 ** 2  # 5Mb
        send_by_file_max_size = 10 * 1024 ** 2  # 10Mb

        media_size = get_preview_size(self.image_url)

        if media_size < send_by_url_max_size:
            photo = self.image_url
        elif media_size < send_by_file_max_size:
            photo = download_file(self.image_url)
        else:
            log.info(
                f"Can't send preview because it exceeds Telegram size limit. {media_size=}, {self=}"
            )
            return

        try:
            context.bot.send_photo(
                chat_id=message.chat_id,
                reply_to_message_id=message.message_id,
                caption=self.title,
                photo=photo,
            )
        except TelegramError as e:
            log.error(f"Error sending photo error={e}. preview={self}, {media_size=}")
            raise


@dataclass
class VideoPreview:
    title: str
    video_url: str
    duration: Optional[int] = None
    height: Optional[int] = None
    width: Optional[int] = None

    def send(self, message: Message, context: CallbackContext):
        send_by_url_max_size = 20 * 1024 ** 2  # 20Mb
        send_by_file_max_size = 50 * 1024 ** 2  # 50Mb

        media_size = get_preview_size(self.video_url)

        if media_size < send_by_url_max_size:
            video = self.video_url

        elif media_size < send_by_file_max_size:
            video = download_file(self.video_url)
        else:
            log.info(
                f"Can't send preview because it exceeds Telegram size limit. {media_size=}, {self=}"
            )
            return

        try:
            context.bot.send_video(
                chat_id=message.chat_id,
                reply_to_message_id=message.message_id,
                caption=self.title,
                video=video,
                duration=self.duration,
                height=self.height,
                width=self.width,
            )
        except TelegramError as e:
            log.error(f"Error sending video error={e}. preview={self}, {media_size=}")
            raise


def get_preview_size(url: str) -> int:
    head_response = requests.head(url)
    if content_length := head_response.headers.get("Content-Length"):
        return int(content_length)
    return 0


def download_file(url: str) -> BytesIO:
    response = requests.get(url)
    return BytesIO(response.content)
