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


    def test_none_structured_result_falls_back_to_call_fields_not_none(self):
        # Real bug caught on a real call: structured_result key was present
        # but its value was None (extraction didn't confidently fill the
        # schema on a real completed call) -- must not silently return None.
        fake_client = MagicMock()
        fake_client.calls.create_and_wait.return_value = {
            "structured_result": None,
            "status": "completed",
            "summary": "Discussed the stuck OCR job with the customer.",
            "task_completed": True,
            "failure_code": None,
            "failure_message": None,
        }

        with patch.object(calle_client, "MOCK", False), patch.object(
            calle_client, "CALLE_API_KEY", "fake-key"
        ), patch("support_agent.calle_client.CalleClient", return_value=fake_client):
            result = calle_client.run_support_call("+15550123456", "task text")

        self.assertIsNotNone(result)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["summary"], "Discussed the stuck OCR job with the customer.")
        self.assertTrue(result["task_completed"])

    def test_calle_api_error_returns_clean_dict_not_crash(self):
        from calle.errors import CalleAPIError

        fake_client = MagicMock()
        fake_client.calls.create_and_wait.side_effect = CalleAPIError(
            code="unsupported_region_language",
            message="Calls for Guyana in English are not supported.",
            status_code=422,
            details={"region": "GY", "language": "en"},
        )

        with patch.object(calle_client, "MOCK", False), patch.object(
            calle_client, "CALLE_API_KEY", "fake-key"
        ), patch("support_agent.calle_client.CalleClient", return_value=fake_client):
            result = calle_client.run_support_call("+5926877233", "task text")

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_code"], "unsupported_region_language")
        fake_client.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
