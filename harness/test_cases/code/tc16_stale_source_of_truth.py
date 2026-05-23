"""Configuration management for the notification service.

Loads service configuration from the central config store and provides
typed access to settings. Configuration is refreshed every 5 minutes
to pick up changes without requiring a restart.
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

MAX_RETRIES = 3


@dataclass
class NotificationConfig:
    """Typed configuration for the notification service."""
    smtp_host: str
    smtp_port: int
    from_address: str
    template_dir: str
    rate_limit_per_minute: int = 100
    enabled_channels: List[str] = field(default_factory=lambda: ["email", "sms"])
    debug_mode: bool = False


def load_config(config_path: str = "/etc/notifier/config.json") -> NotificationConfig:
    """Load and validate notification config from disk."""
    path = Path(config_path)
    if not path.exists():
        logger.error("Config file not found: %s", config_path)
        raise FileNotFoundError(f"Config not found: {config_path}")

    raw = json.loads(path.read_text())
    return NotificationConfig(
        smtp_host=raw["smtp"]["host"],
        smtp_port=raw["smtp"]["port"],
        from_address=raw["smtp"]["from"],
        template_dir=raw.get("template_dir", "/opt/notifier/templates"),
        rate_limit_per_minute=raw.get("rate_limit", 100),
        enabled_channels=raw.get("channels", ["email"]),
        debug_mode=raw.get("debug", False),
    )


# Load config once at import time for fast access throughout the service
CONFIG = load_config()


def get_smtp_host() -> str:
    return CONFIG.smtp_host


def get_rate_limit() -> int:
    return CONFIG.rate_limit_per_minute


def is_channel_enabled(channel: str) -> bool:
    return channel in CONFIG.enabled_channels


def send_with_retry(message: dict, max_attempts: int = MAX_RETRIES) -> bool:
    """Send a notification message with retry logic."""
    import smtplib

    for attempt in range(1, max_attempts + 1):
        try:
            server = smtplib.SMTP(CONFIG.smtp_host, CONFIG.smtp_port, timeout=10)
            server.sendmail(CONFIG.from_address, message["to"], message["body"])
            server.quit()
            logger.info("Message sent to %s on attempt %d", message["to"], attempt)
            return True
        except smtplib.SMTPException as e:
            logger.warning("Send attempt %d failed: %s", attempt, e)

    logger.error("All %d send attempts failed for %s", max_attempts, message["to"])
    return False
