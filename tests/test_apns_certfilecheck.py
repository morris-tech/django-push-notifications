import json
import mock
import os
from django.test import TestCase
from push_notifications.models import APNSDevice

from django.conf import settings

from push_notifications.apns import *


class APNSCertfileTestCase(TestCase):
    def test_apns_send_message_good_certfile(self):
        path = os.path.join(os.path.dirname(__file__), "test_data", "good_revoked.pem")
        settings.PUSH_NOTIFICATIONS_SETTINGS["APNS_CERTIFICATE"] = path
        device = APNSDevice.objects.create(
            registration_id="1212121212121212121212121212121212121212121212121212121212121212",
        )
        with mock.patch("ssl.wrap_socket") as ws:
            with mock.patch("socket.socket") as socket:
                socket.return_value = 123
                device.send_message("Hello world")
                ws.assert_called_once_with(123, ca_certs=None, certfile=path, ssl_version=3)

    def test_apns_send_message_raises_no_privatekey(self):
        path = os.path.join(os.path.dirname(__file__), "test_data", "without_private.pem")
        settings.PUSH_NOTIFICATIONS_SETTINGS["APNS_CERTIFICATE"] = path
        device = APNSDevice.objects.create(
            registration_id="1212121212121212121212121212121212121212121212121212121212121212",
        )
        with self.assertRaises(ImproperlyConfigured) as ic:
            device.send_message("Hello world")
        self.assertTrue(bool(ic.exception.args))
        self.assertEqual(ic.exception.args[0],
                         "The APNS certificate file at '%s' is unusable: The certificate doesn't contain a private key" % path)

    def test_apns_send_message_raises_passwd(self):
        path = os.path.join(os.path.dirname(__file__), "test_data", "good_with_passwd.pem")
        settings.PUSH_NOTIFICATIONS_SETTINGS["APNS_CERTIFICATE"] = path
        device = APNSDevice.objects.create(
            registration_id="1212121212121212121212121212121212121212121212121212121212121212",
        )
        with self.assertRaises(ImproperlyConfigured) as ic:
            device.send_message("Hello world")
        self.assertTrue(bool(ic.exception.args))
        self.assertEqual(ic.exception.args[0],
                         "The APNS certificate file at '%s' is unusable: The certificate private key should not be encrypted" % path)
