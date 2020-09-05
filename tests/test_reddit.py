import unittest

from reddit2telegram.config import settings
from reddit2telegram.reddit import create_reddit_instance, reddit_preview


class RedditTestCase(unittest.TestCase):
    def test_gif(self):
        reddit_client = create_reddit_instance(
            settings.reddit_client_id,
            settings.reddit_client_secret,
            settings.version,
        )
        url = "https://www.reddit.com/r/nextfuckinglevel/comments/i99a63/3d_printed_spiderman_homecoming_mask"
        preview = reddit_preview(reddit_client, url)

        self.assertEqual(
            preview["caption"],
            "3D Printed Spiderman Homecoming Mask",
        )
        self.assertIn("https://v.redd.it/gtg6x2gzdug51/DASH_480.mp4", preview["video"])


if __name__ == '__main__':
    unittest.main()
