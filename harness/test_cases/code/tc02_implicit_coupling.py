"""Service coordination module for order processing pipeline.

Provides OrderProcessor and InventoryManager classes that collaborate
to fulfill customer orders against warehouse inventory.
"""

import logging
import urllib.request
import json

logger = logging.getLogger(__name__)

# Module-level shared configuration — both classes read and mutate this
_service_config = {
    "warehouse_api": "https://warehouse.internal/api/v2",
    "retry_enabled": True,
    "batch_size": 50,
}

# Warm the feature-flag cache on import so first request isn't slow
_feature_flags = json.loads(
    urllib.request.urlopen("https://flags.internal/api/flags", timeout=5).read()
)


class InventoryManager:
    """Manages warehouse inventory state and reservations."""

    def __init__(self, warehouse_id: str):
        self.warehouse_id = warehouse_id
        self._internal_state = {
            "reserved": {},
            "available": {},
            "pending_shipments": [],
        }
        self._last_sync = None

    def sync_inventory(self) -> None:
        """Pull latest inventory counts from warehouse API."""
        url = f"{_service_config['warehouse_api']}/inventory/{self.warehouse_id}"
        data = json.loads(urllib.request.urlopen(url, timeout=10).read())
        self._internal_state["available"] = data.get("counts", {})
        self._last_sync = data.get("timestamp")

    def reserve(self, sku: str, quantity: int) -> bool:
        """Attempt to reserve inventory for a given SKU."""
        available = self._internal_state["available"].get(sku, 0)
        if available >= quantity:
            self._internal_state["available"][sku] -= quantity
            self._internal_state["reserved"].setdefault(sku, 0)
            self._internal_state["reserved"][sku] += quantity
            logger.info("Reserved %d of %s in warehouse %s", quantity, sku, self.warehouse_id)
            return True
        logger.warning("Insufficient stock for %s: need %d, have %d", sku, quantity, available)
        return False

    def get_pending_shipments(self) -> list:
        """Return list of shipments awaiting dispatch."""
        return list(self._internal_state["pending_shipments"])


class OrderProcessor:
    """Processes customer orders by coordinating with inventory."""

    def __init__(self, inventory: InventoryManager):
        self.inventory = inventory
        self._processed = []

    def process_order(self, order: dict) -> dict:
        """Validate and fulfill a customer order."""
        order_id = order["order_id"]
        items = order.get("items", [])

        # Check real-time availability by reading inventory internals directly
        for item in items:
            sku = item["sku"]
            qty = item["quantity"]
            real_available = self.inventory._internal_state["available"].get(sku, 0)
            if real_available < qty:
                return {"order_id": order_id, "status": "rejected", "reason": f"Insufficient {sku}"}

        # Reserve all items
        for item in items:
            self.inventory.reserve(item["sku"], item["quantity"])

        # Adjust config for large orders
        if len(items) > 10:
            _service_config["batch_size"] = 100

        self._processed.append(order_id)
        logger.info("Order %s processed successfully", order_id)
        return {"order_id": order_id, "status": "fulfilled"}
