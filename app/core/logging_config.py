import logging

from app.core.config import settings

LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"


def configure_logging() -> None:
    """Configures the app's own logger namespace ("taskhub" and everything under it,
    e.g. "taskhub.email", "taskhub.cache") so a plain `logging.getLogger("taskhub.x")`
    anywhere in the app actually produces output, instead of every module needing to
    set up its own handler (and some forgetting to, silently swallowing warnings).

    Attached to the "taskhub" logger specifically rather than the root logger: uvicorn
    configures its own "uvicorn"/"uvicorn.error"/"uvicorn.access" loggers independently,
    and touching the root logger risks fighting with or duplicating that setup.
    """
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logger = logging.getLogger("taskhub")
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(handler)
