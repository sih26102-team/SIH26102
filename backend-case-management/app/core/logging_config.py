import logging
import sys

from app.core.config import settings

def configure_logging() -> None:
    level = logging.DEBUG if settings.ENV == "development" else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.ENV == "development" else logging.WARNING
    )


logger = logging.getLogger("mplads_api")
