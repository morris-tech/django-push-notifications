import xml.etree.ElementTree as ET

from django.test import TestCase

from push_notifications.wns import dict_to_xml_schema, wns_send_bulk_message, wns_send_message
try:
	from mock import patch
except ImportError:
	from unittest.mock import patch


class WNSSendMessageTestCase(TestCase):
	def setUp(self):
		pass

	@patch('push_notifications.wns._wns_prepare_toast', **{
		'return_value': 'this is expected'
	})
	@patch('push_notifications.wns._wns_send')
	def test_send_message_calls_wns_send_with_toast_if_string_is_passed_to_message(self, mock_method, _):
		wns_send_message(uri='one', message='test message')
		mock_method.assert_called_with(uri='one', data='this is expected', wns_type='wns/toast',
										package_id=None, secret_key=None)

	@patch('push_notifications.wns.dict_to_xml_schema', **{
		'return_value': ET.Element('toast')
	})
	@patch('push_notifications.wns._wns_send')
	def test_send_message_calls_wns_send_with_xml_if_xml_data_is_passed(self, mock_method, _):
		wns_send_message(uri='one', xml_data={'key': 'value'})
		mock_method.assert_called_with(uri='one', data=b'<toast />', wns_type='wns/toast',
										package_id=None, secret_key=None)

	@patch('push_notifications.wns._wns_send')
	def test_send_message_calls_wns_send_with_xml_if_xml_data_is_passed(self, mock_method):
		wns_send_message(uri='one', raw_data='expected data')
		mock_method.assert_called_with(uri='one', data='expected data', wns_type='wns/raw',
										package_id=None, secret_key=None)

	def test_send_message_raises_TypeError_if_one_of_the_data_params_arent_filled(self):
		with self.assertRaises(TypeError):
			wns_send_message(uri='one')


class WNSSendBulkMessageTestCase(TestCase):
	def setUp(self):
		pass

	@patch('push_notifications.wns.wns_send_message')
	def test_send_bulk_message_doesnt_call_send_message_with_empty_list(self, mock_method):
		wns_send_bulk_message(uri_list=[], message='test message')
		mock_method.assert_not_called()

	@patch('push_notifications.wns.wns_send_message')
	def test_send_bulk_message_calls_send_message(self, mock_method):
		wns_send_bulk_message(uri_list=['one', ], message='test message')
		mock_method.assert_called_with(message='test message', raw_data=None, uri='one', xml_data=None,
										package_id=None, secret_key=None)


class WNSDictToXmlSchemaTestCase(TestCase):
	def setUp(self):
		pass

	def test_create_simple_xml_from_dict(self):
		xml_data = {
			"toast": {
				"attrs": {
					"key": "value"
				},
				"children": {
					"visual": {
						"children": {
							"binding": {
								"attrs": {
									"template": "ToastText01"
								},
								"children": {
									"text": {
										"attrs": {
											"id": "1"
										},
										"children": "toast notification"
									}
								}
							}
						}
					}
				}
			}
		}
		# Converting xml to str via tostring is inconsistent, so we have to check each element.
		xml_tree = dict_to_xml_schema(xml_data)
		self.assertEqual(xml_tree.tag, 'toast')
		self.assertEqual(xml_tree.attrib, {'key': 'value'})
		visual = xml_tree.getchildren()[0]
		self.assertEqual(visual.tag, 'visual')
		binding = visual.getchildren()[0]
		self.assertEqual(binding.tag, 'binding')
		self.assertEqual(binding.attrib, {"template": "ToastText01"})
		text = binding.getchildren()[0]
		self.assertEqual(text.tag, 'text')
		self.assertEqual(text.attrib, {'id': '1'})
		self.assertEqual(text.text, 'toast notification')

	def test_create_multi_sub_element_xml_from_dict(self):
		xml_data = {
			"toast": {
				"attrs": {
					"key": "value"
				},
				"children": {
					"visual": {
						"children": {
							"binding": {
								"attrs": {
									"template": "ToastText02"
								},
								"children": {
									"text": [
										{
											"attrs": {
												"id": "1"
											},
											"children": "first text"
										},
										{
											"attrs": {
												"id": "2"
											},
											"children": "second text"
										}
									]
								}
							}
						}
					}
				}
			}
		}
		# Converting xml to str via tostring is inconsistent, so we have to check each element.
		xml_tree = dict_to_xml_schema(xml_data)
		self.assertEqual(xml_tree.tag, 'toast')
		self.assertEqual(xml_tree.attrib, {'key': 'value'})
		visual = xml_tree.getchildren()[0]
		self.assertEqual(visual.tag, 'visual')
		binding = visual.getchildren()[0]
		self.assertEqual(binding.tag, 'binding')
		self.assertEqual(binding.attrib, {"template": "ToastText02"})
		children = binding.getchildren()
		self.assertEqual(len(children), 2)

	def test_create_two_multi_sub_element_xml_from_dict(self):
		xml_data = {
			"toast": {
				"attrs": {
					"key": "value"
				},
				"children": {
					"visual": {
						"children": {
							"binding": {
								"attrs": {
									"template": "ToastText02"
								},
								"children": {
									"text": [
										{
											"attrs": {
												"id": "1"
											},
											"children": "first text"
										},
										{
											"attrs": {
												"id": "2"
											},
											"children": "second text"
										}
									],
									"image": [
										{
											"attrs": {
												"src": "src1"
											},
										},
										{
											"attrs": {
												"src": "src2"
											},
										}
									]
								}
							}
						}
					}
				}
			}
		}
		# Converting xml to str via tostring is inconsistent, so we have to check each element.
		xml_tree = dict_to_xml_schema(xml_data)
		self.assertEqual(xml_tree.tag, 'toast')
		self.assertEqual(xml_tree.attrib, {'key': 'value'})
		visual = xml_tree.getchildren()[0]
		self.assertEqual(visual.tag, 'visual')
		binding = visual.getchildren()[0]
		self.assertEqual(binding.tag, 'binding')
		self.assertEqual(binding.attrib, {"template": "ToastText02"})
		children = binding.getchildren()
		self.assertEqual(len(children), 4)
