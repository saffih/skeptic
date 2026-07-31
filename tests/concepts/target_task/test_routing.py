import unittest
from unittest.mock import patch

from concepts.target_task.host_adapter import ProviderCapabilities, TargetTaskHostAdapter
from concepts.target_task.routing import RoutingError, resolve_lead_route, resolve_route


PROFILE = {"provider": "generic-recorded-host", "model_class": "small", "effort": "low", "timeout_seconds": 30, "budget": 0}


class UnavailableAdapter(TargetTaskHostAdapter):
    provider_id = "unavailable"
    LEAD_ROLE = "lead"
    MODEL_ALIASES = {"small": "small-model"}
    LAUNCH_MODE = "external"

    def discover_capabilities(self):
        return ProviderCapabilities(self.provider_id, False, ("worker",), False, "none")

    def provider_role(self, canonical_role):
        return canonical_role

    def validate_provider_evidence(self, raw):
        raise AssertionError("not used")


class RoutingTests(unittest.TestCase):
    def test_generic_route_resolves(self):
        route = resolve_route("worker", PROFILE)
        self.assertEqual(route.status, "RESOLVED")
        self.assertEqual(route.resolved_model, "recorded-small")

    def test_explicit_unavailable_provider_fails_closed(self):
        profile = {**PROFILE, "provider": "unavailable"}
        with patch("concepts.target_task.routing.ADAPTER_TYPES", {"unavailable": UnavailableAdapter}):
            with self.assertRaises(RoutingError):
                resolve_route("worker", profile)

    def test_unavailable_lead_route_requires_relaunch(self):
        profile = {**PROFILE, "provider": "unavailable"}
        with patch("concepts.target_task.routing.ADAPTER_TYPES", {"unavailable": UnavailableAdapter}):
            route = resolve_lead_route(profile)
        self.assertEqual(route.status, "RELAUNCH_REQUIRED")
        self.assertIsNotNone(route.blocker)

    def test_current_provider_must_be_explicit(self):
        with self.assertRaises(RoutingError):
            resolve_route("worker", {**PROFILE, "provider": "current"})


if __name__ == "__main__":
    unittest.main()
