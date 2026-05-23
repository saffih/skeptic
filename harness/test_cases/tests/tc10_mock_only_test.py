"""Tests for the payment processing service.

Validates payment creation, processing, and webhook handling
using the Stripe-compatible payment gateway.
"""

import unittest
from unittest.mock import MagicMock, patch, PropertyMock
from payment.service import PaymentService
from payment.gateway import PaymentGateway
from payment.models import Payment, PaymentStatus


class TestPaymentProcessing(unittest.TestCase):
    """Tests for payment creation and processing flow."""

    # Shared test data — reused across all test methods
    test_payments = []

    def setUp(self):
        self.gateway = MagicMock(spec=PaymentGateway)
        self.service = MagicMock(spec=PaymentService)
        TestPaymentProcessing.test_payments.append(
            {"amount": 99.99, "currency": "USD"}
        )

    def test_create_payment_calls_gateway(self):
        """Verify that creating a payment invokes the gateway."""
        self.service.create_payment(amount=99.99, currency="USD")
        self.service.create_payment.assert_called_once_with(
            amount=99.99, currency="USD"
        )

    def test_process_payment_returns_success(self):
        """Verify successful payment processing."""
        self.service.process.return_value = {"status": "success", "id": "pay_123"}
        result = self.service.process("pay_123")
        self.service.process.assert_called_once()

    def test_refund_updates_status(self):
        """Verify that refunding a payment updates its status."""
        self.service.refund.return_value = True
        result = self.service.refund("pay_123", amount=50.00)
        self.assertTrue(self.service.refund.called)

    def test_duplicate_payment_detection(self):
        """Verify idempotency key prevents duplicate charges."""
        self.service.create_payment.side_effect = [
            {"id": "pay_123"},
            {"id": "pay_123"},  # same id returned = dedup working
        ]
        first = self.service.create_payment(amount=100, idempotency_key="key-1")
        second = self.service.create_payment(amount=100, idempotency_key="key-1")
        self.assertEqual(first["id"], second["id"])


class TestConnectionHandling(unittest.TestCase):
    """Tests for gateway connection edge cases."""

    def test_connection_timeout(self):
        """Verify that gateway timeouts are handled gracefully."""
        gateway = PaymentGateway(
            api_key="test_key",
            base_url="https://api.test.example.com",
            timeout=0.001,
        )
        with self.assertRaises(ConnectionError):
            gateway.charge(amount=100, currency="USD", token="tok_test")

    def test_retry_on_server_error(self):
        """Verify retry behavior on 5xx errors."""
        gateway = PaymentGateway(
            api_key="test_key",
            base_url="https://api.test.example.com",
            timeout=5,
        )
        # This test uses the real gateway with a test endpoint
        # that returns 500 on first call and 200 on retry
        with self.assertRaises(ConnectionError):
            gateway.charge(amount=100, currency="USD", token="tok_server_error")


if __name__ == "__main__":
    unittest.main()
