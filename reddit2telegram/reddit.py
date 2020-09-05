import logging

import praw

log = logging.getLogger(__name__)


def create_reddit_instance(
    client_id: str, client_secret: str, version: str
) -> praw.Reddit:
    user_agent = f"telegram:fedalto.reddit_preview_bot:{version} (by /u/fedalto)"

    return praw.Reddit(
        client_id=client_id, client_secret=client_secret, user_agent=user_agent,
    )


def reddit_preview(reddit_client: praw.Reddit, reddit_post_url: str) -> dict:
    reddit_post = reddit_client.submission(url=reddit_post_url)
    log.debug(f"{reddit_post.secure_media=}")
    if "reddit_video" in reddit_post.secure_media:
        video = reddit_post.secure_media["reddit_video"]
        preview = dict(
            caption=reddit_post.title,
            video=video["fallback_url"],
            duration=video["duration"],
            height=video["height"],
            width=video["width"],
        )
        return preview
