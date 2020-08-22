import os
import tempfile
import shutil
import time
import unittest
from httpmon.producer import check, KafkaProducerWrapper
from httpmon.consumer import PGExporter, KafkaConsumerWrapper
from httpmon.utils import prepare_kafka_connection_args, KafkaArgs


class IntegrationTestCase(unittest.TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        for name in ['KAFKA_CRT', 'KAFKA_KEY', 'KAFKA_CA']:
            with open(os.path.join(self.tempdir, name), 'w') as fp:
                fp.write(os.environ.get(name, ''))

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    @property
    def _kafka_connection(self):
        args = KafkaArgs(
            kafka_server=os.environ.get('KAFKA_SERVER'),
            kafka_ca=os.path.join(self.tempdir, 'KAFKA_CA'),
            kafka_cert=os.path.join(self.tempdir, 'KAFKA_CRT'),
            kafka_key=os.path.join(self.tempdir, 'KAFKA_KEY'),
        )
        if os.environ.get('KAFKA_NO_SSL'):
            # localhost testing purpose
            args = KafkaArgs(
                kafka_server=os.environ.get('KAFKA_SERVER'),
                kafka_ca=None,
                kafka_cert=None,
                kafka_key=None,
            )

        return prepare_kafka_connection_args(args)

    def test_run(self):
        """
        Make one check, push to kafka, read from kafka, put to DB
        """
        consumer = KafkaConsumerWrapper(self._kafka_connection, 'unittest')
        exporter = PGExporter(os.environ.get('PG_URI'))
        producer = KafkaProducerWrapper(self._kafka_connection, 'unittest')
        need_message = True
        while need_message:
            # parallel testing create many consumers
            # produce until got one message
            check('https://www.google.com', producer=producer)
            time.sleep(1)
            for message in consumer.messages():
                exporter.submit(message)
                need_message = False
