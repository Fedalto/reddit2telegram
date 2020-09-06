import unittest

from telegram import Bot, Message

from reddit2telegram.bot import parse_urls


class ParseRedditURL(unittest.TestCase):
    def test_link_only(self):
        message_data = {
            "message_id": 32,
            "date": 1599243544,
            "chat": {
                "id": 41390186,
                "type": "private",
                "username": "fedalto",
                "first_name": "Leonardo",
                "last_name": "Fedalto",
            },
            "text": "https://www.reddit.com/r/nextfuckinglevel/comments/i99a63/3d_printed_spiderman_homecoming_mask/",
            "entities": [{"type": "url", "offset": 0, "length": 95}],
            "caption_entities": [],
            "photo": [],
            "new_chat_members": [],
            "new_chat_photo": [],
            "delete_chat_photo": False,
            "group_chat_created": False,
            "supergroup_chat_created": False,
            "channel_chat_created": False,
            "from": {
                "id": 41390186,
                "first_name": "Leonardo",
                "is_bot": False,
                "last_name": "Fedalto",
                "username": "fedalto",
                "language_code": "en",
            },
        }
        bot = Bot(token="1234:test")
        message = Message.de_json(message_data, bot)
        urls = parse_urls(message)

        self.assertIn(
            "https://www.reddit.com/r/nextfuckinglevel/comments/i99a63/3d_printed_spiderman_homecoming_mask/",
            urls,
        )


if __name__ == "__main__":
    unittest.main()
