from logging.config import dictConfig

LOG_CONFIG = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "%(asctime)s %(levelname)s:%(name)s:%(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "default"}},
    "root": {"level": "INFO", "handlers": ["console"]},
    "loggers": {
        "reddit2telegram": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": False,
        }
    },
}


def configure_logging():
    dictConfig(LOG_CONFIG)
