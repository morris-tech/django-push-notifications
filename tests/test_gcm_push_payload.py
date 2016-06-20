import mock
import json
from django.test import TestCase
from push_notifications.gcm import gcm_send_message, gcm_send_bulk_message
from tests.mock_responses import GCM_PLAIN_RESPONSE, GCM_JSON_RESPONSE


class GCMPushPayloadTest(TestCase):
	def test_push_payload(self):
		with mock.patch("push_notifications.gcm._gcm_send", return_value=GCM_PLAIN_RESPONSE) as p:
			gcm_send_message("abc", {"message": "Hello world"})
			p.assert_called_once_with(
				b"data.message=Hello+world&registration_id=abc",
				"application/x-www-form-urlencoded;charset=UTF-8",  key=None)

	def test_push_payload_params(self):
		with mock.patch("push_notifications.gcm._gcm_send", return_value=GCM_PLAIN_RESPONSE) as p:
			gcm_send_message("abc", {"message": "Hello world"}, delay_while_idle=True, time_to_live=3600)
			p.assert_called_once_with(
				b"data.message=Hello+world&delay_while_idle=1&registration_id=abc&time_to_live=3600",
				"application/x-www-form-urlencoded;charset=UTF-8",  key=None)

	def test_bulk_push_payload(self):
		with mock.patch("push_notifications.gcm._gcm_send", return_value=GCM_JSON_RESPONSE) as p:
			gcm_send_bulk_message(["abc", "123"], {"message": "Hello world"})
			p.assert_called_once_with(
				b'{"data":{"message":"Hello world"},"registration_ids":["abc","123"]}',
				"application/json",  key=None)
