import logging

from src.infrastructure.config import Config

logger = logging.getLogger(__name__)


def init_sentry(config: Config) -> None:
    if config.sentry is None:
        return

    import sentry_sdk  # noqa: PLC0415

    try:
        sentry_sdk.init(
            dsn=config.sentry.dsn,
            environment=config.sentry.environment,
            traces_sample_rate=config.sentry.traces_sample_rate,
            profiles_sample_rate=config.sentry.profiles_sample_rate,
        )
        logger.info("Sentry initialized for environment: %s", config.sentry.environment)
    except Exception:
        logger.warning(
            "Failed to initialize Sentry; continuing without it", exc_info=True
        )
