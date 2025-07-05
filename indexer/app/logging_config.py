from logging.config import dictConfig


def init_logging(log_level: str = "INFO"):
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": True,
            "formatters": {
                "default": {
                    "format": "%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                },
            },
            "root": {
                "level": "WARNING",
                "handlers": ["console"],
            },
            "loggers": {
                "indexer": {
                    "level": log_level,
                    "handlers": ["console"],
                    "propagate": False,
                },
            },
        }
    )
