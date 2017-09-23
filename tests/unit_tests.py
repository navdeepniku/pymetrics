import unittest
from server import client_export_db, read_server_config, client_alerts
import datetime


class ValidateServerConfig(unittest.TestCase):
    # validate xml file read
    def test_read_server_config(self):
        self.assertNotEqual(len(read_server_config()), 0)


class ValidateDb(unittest.TestCase):
    # validate db connectivity and schema
    def test_client_export_db(self):
        metrics = {'timestamp': datetime.datetime(2017, 9, 18, 23, 36, 37, 608587),
                   'data': {'mem_percent': 80.3, 'cpu_percent': 17.3}}
        if len(read_server_config()) != 0:
            client = read_server_config()[0]
            self.assertEqual(client_export_db(client, metrics), 0)


class ValidateSMTP(unittest.TestCase):
    # validate SMTP connection
    def test_client_alerts(self):
        metrics = {'timestamp': datetime.datetime(2017, 9, 18, 23, 36, 37, 608587),
                   'data': {'mem_percent': 80.3, 'cpu_percent': 17.3}}
        if len(read_server_config()) != 0:
            client = read_server_config()[0]
            self.assertEqual(client_alerts(client, metrics), 0)


if __name__ == '__main__':
    unittest.main()
