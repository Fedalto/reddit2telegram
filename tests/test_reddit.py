import unittest
from unittest.mock import patch

from reddit2telegram.config import settings
from reddit2telegram.preview import ImagePreview, VideoPreview
from reddit2telegram.handlers.reddit import (
    create_reddit_instance,
    create_preview_from_reddit,
)


class RedditTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.reddit_client = create_reddit_instance(
            settings.reddit_client_id,
            settings.reddit_client_secret,
            str(settings.version),
        )
        patch("reddit2telegram.handlers.reddit.download_video").start()

    def test_image(self):
        url = "https://www.reddit.com/r/funny/comments/d2bwot/printers/"
        preview = create_preview_from_reddit(self.reddit_client, url)

        self.assertIsInstance(preview, ImagePreview)
        self.assertEqual(preview.title, "Printers")
        self.assertEqual("https://i.redd.it/jlx9wokn7tl31.jpg", preview.image_url)

    def test_gif(self):
        url = "https://www.reddit.com/r/nextfuckinglevel/comments/i99a63/3d_printed_spiderman_homecoming_mask"
        preview = create_preview_from_reddit(self.reddit_client, url)

        self.assertIsInstance(preview, VideoPreview)
        self.assertEqual(preview.title, "3D Printed Spiderman Homecoming Mask")

    def test_crosspost(self):
        url = "https://www.reddit.com/r/oddlysatisfying/comments/inarcs/this_handmade_tortilla_press/"
        preview = create_preview_from_reddit(self.reddit_client, url)

        self.assertIsInstance(preview, VideoPreview)
        self.assertEqual(preview.title, "This handmade tortilla press")


if __name__ == "__main__":
    unittest.main()
