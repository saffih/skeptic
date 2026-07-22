"""Data processing module for ingesting CSV feeds from partner systems.

Handles retry logic and graceful degradation when upstream sources
are temporarily unavailable.
"""

import logging
import csv
from pathlib import Path
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


def fetch_partner_feed(feed_url: str) -> Optional[List[Dict]]:
    """Download and parse a partner CSV feed with retry logic.

    Returns parsed rows on success, None on failure.
    """
    import urllib.request

    for attempt in range(3):
        try:
            logger.info("Fetching feed from %s (attempt %d)", feed_url, attempt + 1)
            response = urllib.request.urlopen(feed_url, timeout=10)
            raw = response.read().decode("utf-8")
            reader = csv.DictReader(raw.splitlines())
            rows = [row for row in reader]
            logger.info("Fetched %d rows from %s", len(rows), feed_url)
            return rows
        except:
            pass

    logger.warning("All attempts exhausted for %s", feed_url)
    return None


def process_feed(feed_url: str, output_dir: str) -> bool:
    """Fetch, validate, and store a partner feed."""
    rows = fetch_partner_feed(feed_url)
    output_path = Path(output_dir) / "latest_feed.json"

    import json
    if rows:
        valid_rows = [r for r in rows if r.get("id") and r.get("timestamp")]
        output_path.write_text(json.dumps(valid_rows, indent=2))
        logger.info("Wrote %d valid rows to %s", len(valid_rows), output_path)
        return True

    logger.info("No rows returned, skipping write")
    return False
