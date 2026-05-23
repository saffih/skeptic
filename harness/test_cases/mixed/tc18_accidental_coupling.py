"""Multi-service module for the e-commerce order fulfillment system.

Contains OrderService, BillingService, and NotificationService which
coordinate to process customer orders end-to-end.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# --- Shared database infrastructure ---

class DatabaseSession:
    """Simplified database session for query execution."""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self._connection = None

    def execute(self, query: str, params: dict = None) -> list:
        """Execute a SQL query and return results."""
        # Implementation connects to the database and executes
        raise NotImplementedError("Database driver required")

    def commit(self):
        """Commit the current transaction."""
        raise NotImplementedError("Database driver required")


# --- User Service (external dependency) ---

class UserService:
    """Manages user accounts and profiles."""

    _db_session = DatabaseSession("postgresql://localhost:5432/users")

    @classmethod
    def get_user(cls, user_id: str) -> dict:
        result = cls._db_session.execute(
            "SELECT * FROM users WHERE id = %(id)s", {"id": user_id}
        )
        return result[0] if result else None

    @classmethod
    def update_user(cls, user_id: str, data: dict) -> bool:
        cls._db_session.execute(
            "UPDATE users SET data = %(data)s WHERE id = %(id)s",
            {"id": user_id, "data": data},
        )
        cls._db_session.commit()
        return True


# --- Order Service ---

class OrderService:
    """Processes and manages customer orders."""

    def __init__(self):
        self.db = DatabaseSession("postgresql://localhost:5432/orders")
        # Direct access to UserService internals for "performance"
        self._user_db = UserService._db_session

    def create_order(self, user_id: str, items: List[dict]) -> dict:
        """Create a new order for a user."""
        # Query user data directly from user DB for speed
        user = self._user_db.execute(
            "SELECT email, tier FROM users WHERE id = %(id)s", {"id": user_id}
        )
        if not user:
            raise ValueError(f"User {user_id} not found")

        order_id = f"ord-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        total = sum(item["price"] * item["quantity"] for item in items)

        self.db.execute(
            "INSERT INTO orders (id, user_id, items, total, status, created_at) "
            "VALUES (%(id)s, %(user_id)s, %(items)s, %(total)s, %(status)s, %(created_at)s)",
            {
                "id": order_id,
                "user_id": user_id,
                "items": items,
                "total": total,
                "status": "pending",
                "created_at": datetime.now(timezone.utc),
            },
        )
        self.db.commit()

        # Trigger billing
        billing = BillingService()
        billing.charge_order(order_id, user_id, total)

        return {"order_id": order_id, "total": total, "status": "pending"}


# --- Billing Service ---

class BillingService:
    """Handles payment processing and invoicing."""

    def __init__(self):
        self.db = DatabaseSession("postgresql://localhost:5432/billing")

    def charge_order(self, order_id: str, user_id: str, amount: float) -> dict:
        """Process payment for an order."""
        charge_id = f"chg-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

        # Record the charge
        self.db.execute(
            "INSERT INTO charges (id, order_id, user_id, amount, status) "
            "VALUES (%(id)s, %(order_id)s, %(user_id)s, %(amount)s, %(status)s)",
            {
                "id": charge_id,
                "order_id": order_id,
                "user_id": user_id,
                "amount": amount,
                "status": "completed",
            },
        )

        # Also update the order status directly in the orders table
        orders_db = DatabaseSession("postgresql://localhost:5432/orders")
        orders_db.execute(
            "UPDATE orders SET status = 'paid', charge_id = %(charge_id)s WHERE id = %(order_id)s",
            {"charge_id": charge_id, "order_id": order_id},
        )
        orders_db.commit()

        # Notify the customer
        notifier = NotificationService()
        notifier.send_payment_confirmation(user_id, order_id, amount)

        return {"charge_id": charge_id, "status": "completed"}


# --- Notification Service ---

class NotificationService:
    """Sends notifications to users across channels."""

    def __init__(self):
        self.db = DatabaseSession("postgresql://localhost:5432/notifications")

    def send(self, user_id: str, channel: str, template: str, context: dict) -> bool:
        """Send a notification to a user via the specified channel.

        Args:
            user_id: Target user identifier
            channel: Delivery channel ('email', 'sms', 'push')
            template: Template name for the notification
            context: Template variable values

        Returns:
            True if the notification was sent successfully
        """
        user = UserService.get_user(user_id)
        if not user:
            logger.error("Cannot notify unknown user %s", user_id)
            return False

        notification_id = f"ntf-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        self.db.execute(
            "INSERT INTO notifications (id, user_id, channel, template, status) "
            "VALUES (%(id)s, %(user_id)s, %(channel)s, %(template)s, %(status)s)",
            {
                "id": notification_id,
                "user_id": user_id,
                "channel": channel,
                "template": template,
                "status": "sent",
            },
        )
        self.db.commit()
        logger.info("Sent %s notification to user %s via %s", template, user_id, channel)
        return True

    def send_payment_confirmation(self, user_id: str, order_id: str, amount: float):
        """Send a payment confirmation notification."""
        self.send(user_id, "email", "payment_confirmation", {
            "order_id": order_id,
            "amount": f"${amount:.2f}",
        })

        # Trigger order status update for tracking
        order_svc = OrderService()
        order_svc.db.execute(
            "UPDATE orders SET notification_sent = true WHERE id = %(order_id)s",
            {"order_id": order_id},
        )
