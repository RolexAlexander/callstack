"""Zero-cost verification of the CALL-E integration, mocking the SDK
client entirely so this can run for free, repeatedly, before spending any
real call credits.
"""

import unittest
from unittest.mock import MagicMock, patch

from support_agent import calle_client


class TestRunSupportCall(unittest.TestCase):
    def test_mock_mode_returns_labeled_placeholder(self):
        with patch.object(calle_client, "MOCK", True):
            result = calle_client.run_support_call("+15550123456", "call and help")
        self.assertTrue(result["mock"])
        self.assertIn("MOCK MODE", result["summary"])

    def test_missing_key_falls_back_to_mock(self):
        with patch.object(calle_client, "MOCK", False), patch.object(calle_client, "CALLE_API_KEY", ""):
            result = calle_client.run_support_call("+15550123456", "call and help")
        self.assertTrue(result.get("mock"))

    def test_real_call_uses_correct_sdk_shape(self):
        fake_client = MagicMock()
        fake_client.calls.create_and_wait.return_value = {
            "structured_result": {
                "issue_resolved": True,
                "customer_sentiment": "satisfied",
                "summary": "Walked customer through the 300KB upload threshold.",
                "follow_up_needed": "",
            }
        }

        with patch.object(calle_client, "MOCK", False), patch.object(
            calle_client, "CALLE_API_KEY", "fake-key"
        ), patch("support_agent.calle_client.CalleClient", return_value=fake_client) as mock_cls:
            result = calle_client.run_support_call("+15550123456", "explain the upload issue")

        mock_cls.assert_called_once_with(api_key="fake-key")
        _, kwargs = fake_client.calls.create_and_wait.call_args
        self.assertEqual(kwargs["task"], "explain the upload issue")
        self.assertEqual(kwargs["recipient"], {"phones": ["+15550123456"]})
        self.assertEqual(kwargs["result_schema"], calle_client.RESULT_SCHEMA)
        fake_client.close.assert_called_once()
        self.assertTrue(result["issue_resolved"])


if __name__ == "__main__":
    unittest.main()
