import logging
from typing import Union

import praw
from praw.reddit import Submission

from reddit2telegram.preview import ImagePreview, VideoPreview

log = logging.getLogger(__name__)


def create_reddit_instance(
    client_id: str, client_secret: str, version: str
) -> praw.Reddit:
    user_agent = f"telegram:fedalto.reddit_preview_bot:{version} (by /u/fedalto)"

    return praw.Reddit(
        client_id=client_id, client_secret=client_secret, user_agent=user_agent,
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
) -> Union[ImagePreview, VideoPreview]:
    reddit_post = reddit_client.submission(url=reddit_post_url)
    original_post = get_original(reddit_client, reddit_post)

    if is_image_post(original_post):
        return ImagePreview(title=reddit_post.title, image_url=original_post.url)

    if is_video_post(original_post):
        video = original_post.secure_media["reddit_video"]
        return VideoPreview(
            title=reddit_post.title,
            video_url=video["fallback_url"],
            duration=video["duration"],
            height=video["height"],
            width=video["width"],
        )
