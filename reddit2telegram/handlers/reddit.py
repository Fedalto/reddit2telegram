import logging
from io import BytesIO
from os import unlink
from tempfile import gettempdir
from typing import Union, Optional
from urllib.parse import urlparse

import praw
import sentry_sdk
from praw.reddit import Submission
from telegram import InputMediaPhoto
from youtube_dl import YoutubeDL

from reddit2telegram.preview import ImagePreview, VideoPreview, MediaGroupPreview

log = logging.getLogger(__name__)


def create_reddit_instance(
    client_id: str, client_secret: str, version: str
) -> praw.Reddit:
    user_agent = f"telegram:fedalto.reddit_preview_bot:{version} (by /u/fedalto)"

    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
    )


def is_image_post(reddit_post: Submission) -> bool:
    url: str = reddit_post.url
    return url.endswith((".jpg", ".jpeg", ".png"))


def is_video_post(reddit_post: Submission) -> bool:
    return reddit_post.secure_media and "reddit_video" in reddit_post.secure_media


def get_original(reddit_client: praw.Reddit, reddit_post: Submission) -> Submission:
    if hasattr(reddit_post, "crosspost_parent") and reddit_post.crosspost_parent:
        parent_id = reddit_post.crosspost_parent_list[0]["id"]
        return reddit_client.submission(id=parent_id)
    return reddit_post


def create_preview_from_reddit(
    reddit_client: praw.Reddit, reddit_post_url: str
) -> Optional[Union[ImagePreview, VideoPreview, MediaGroupPreview]]:
    reddit_post = reddit_client.submission(url=reddit_post_url)
    original_post = get_original(reddit_client, reddit_post)

    if is_image_post(original_post):
        return ImagePreview(title=reddit_post.title, image_url=original_post.url)

    if is_video_post(original_post):
        video_info = original_post.secure_media["reddit_video"]
        video = download_video(original_post)
        return VideoPreview(
            title=reddit_post.title,
            video=video,
            duration=video_info["duration"],
            height=video_info["height"],
            width=video_info["width"],
            supports_streaming=True,
        )

    if original_post.is_gallery:
        gallery = []
        for item in original_post.gallery_data["items"]:
            media_id = item["media_id"]
            metadata = original_post.media_metadata[media_id]
            caption = item.get("caption")
            if metadata["e"] == "Image":
                media = InputMediaPhoto(media=metadata["s"]["u"], caption=caption)
                gallery.append(media)
            else:
                # Don't know what else this can be
                sentry_sdk.capture_message(
                    f"Gallery contains media unhandled type: {metadata['e']}"
                )

        return MediaGroupPreview(
            media=gallery,
        )

    log.warning(f"Cannot handle {reddit_post_url}")
    return None


def is_from_reddit(url: str) -> bool:
    domain = urlparse(url).netloc
    return domain in ["reddit.com", "www.reddit.com", "redd.it"]


def download_video(reddit_post: Submission) -> BytesIO:
    url = reddit_post.url
    tmp_dir = gettempdir()
    filename = f"{tmp_dir}/telegram-preview-bot/reddit/{reddit_post.id}.mp4"
    ydl_opts = {
        "outtmpl": filename,
        "quiet": True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        video_bytes = BytesIO()
        with open(filename, "rb") as f:
            video_bytes.write(f.read())
        video_bytes.seek(0)
        return video_bytes
    finally:
        unlink(filename)
