"""ETL pipeline for daily sales data aggregation.

Reads raw transaction records from the data lake, applies transformations
(currency normalization, deduplication, enrichment), and writes aggregated
summaries to the reporting warehouse.
"""

import logging
import threading
from datetime import datetime, timezone
from typing import List, Dict, Optional
from decimal import Decimal, InvalidOperation

logger = logging.getLogger(__name__)


def validate_transaction(record: Dict) -> bool:
    """Validate a single transaction record against the expected schema.

    Returns True if the record is valid, False otherwise.
    """
    required_fields = {"transaction_id", "amount", "currency", "timestamp", "merchant_id"}
    if not required_fields.issubset(record.keys()):
        logger.warning("Record missing required fields: %s", required_fields - record.keys())
        return False

    try:
        amount = Decimal(str(record["amount"]))
        if amount <= 0:
            logger.warning("Invalid amount %s for transaction %s", amount, record["transaction_id"])
            return False
    except (InvalidOperation, ValueError) as e:
        logger.warning("Cannot parse amount for %s: %s", record["transaction_id"], e)
        return False

    return True


# Shared counter for pipeline metrics — accessed by multiple threads
_processed_count = 0
_error_count = 0


def normalize_currency(record: Dict, rates: Dict[str, float]) -> Dict:
    """Convert transaction amount to USD using provided exchange rates."""
    currency = record["currency"]
    if currency == "USD":
        return record

    rate = rates.get(currency)
    if rate is None:
        logger.warning("No exchange rate for %s, skipping record %s", currency, record["transaction_id"])
        return record  # returns unconverted record silently

    record["original_amount"] = record["amount"]
    record["original_currency"] = currency
    record["amount"] = round(float(record["amount"]) * rate, 2)
    record["currency"] = "USD"
    return record


def transform_batch(records: List[Dict], rates: Dict[str, float]) -> List[Dict]:
    """Apply all transformations to a batch of transaction records."""
    global _processed_count
    results = []

    for record in records:
        try:
            normalized = normalize_currency(record, rates)
            normalized["processed_at"] = datetime.now(timezone.utc).isoformat()
            normalized["amount"] = round(normalized["amount"], 2)
            results.append(normalized)
            _processed_count += 1
        except Exception:
            pass

    return results


def write_results(results: List[Dict], db_connection) -> int:
    """Write transformed records to the reporting warehouse."""
    written = 0
    for record in results:
        try:
            db_connection.execute(
                "INSERT INTO daily_sales (transaction_id, amount, currency, merchant_id, processed_at) "
                "VALUES (%(transaction_id)s, %(amount)s, %(currency)s, %(merchant_id)s, %(processed_at)s)",
                record,
            )
            written += 1
        except Exception as e:
            logger.error("Failed to write record %s: %s", record.get("transaction_id"), e)

    # Don't commit here — let the caller decide
    return written


def run_pipeline(data_source, db_connection, rates: Dict[str, float], num_workers: int = 4):
    """Execute the full ETL pipeline with parallel workers."""
    global _processed_count, _error_count
    _processed_count = 0
    _error_count = 0

    raw_records = data_source.fetch_all()
    batch_size = len(raw_records) // num_workers

    threads = []
    all_results = []

    def worker(batch):
        transformed = transform_batch(batch, rates)
        all_results.extend(transformed)

    for i in range(num_workers):
        start = i * batch_size
        end = start + batch_size if i < num_workers - 1 else len(raw_records)
        batch = raw_records[start:end]
        t = threading.Thread(target=worker, args=(batch,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    written = write_results(all_results, db_connection)
    logger.info("Pipeline complete: %d processed, %d written", _processed_count, written)
    return written
