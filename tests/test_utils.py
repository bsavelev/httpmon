import unittest
from httpmon.utils import prepare_kafka_connection_args, KafkaArgs


class TestPrepareKafka(unittest.TestCase):

    def test_no_ssl(self):
        args = KafkaArgs(
            kafka_server='server',
            kafka_ca=None,
            kafka_cert=None,
            kafka_key=None,
        )
        r = prepare_kafka_connection_args(args)
        self.assertDictEqual(r, {'bootstrap_servers': 'server'})

    def test_part_ssl(self):
        args = KafkaArgs(
            kafka_server='server',
            kafka_ca=__file__,
            kafka_cert=None,
            kafka_key=None,
        )
        r = prepare_kafka_connection_args(args)
        self.assertDictEqual(r, {'bootstrap_servers': 'server'})

    def test_ssl(self):
        args = KafkaArgs(
            kafka_server='server',
            kafka_ca='path',
            kafka_cert='path',
            kafka_key='path',
        )
        r = prepare_kafka_connection_args(args)
        expected = {
            'security_protocol': 'SSL',
            'ssl_cafile': 'path',
            'ssl_certfile': 'path',
            'ssl_keyfile': 'path',
            'bootstrap_servers': 'server'
        }
        self.assertDictEqual(r, expected)
