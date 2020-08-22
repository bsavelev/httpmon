from copy import deepcopy
import threading
import json
import logging
from datetime import datetime
import time
import uuid
from psycopg2 import pool as pgpool
import psycopg2
from kafka import KafkaConsumer

logger = logging.getLogger(__name__)


class KafkaConsumerWrapper:
    def __init__(self, connection_args, topic):
        self.topic = topic
        consumer_args = {
            'auto_offset_reset': "earliest",
            'group_id': 'httpmon',
            'client_id': uuid.uuid4(),
            'value_deserializer': lambda v: json.loads(v.decode('utf-8')),
        }
        connection_args.update(consumer_args)
        self.consumer = KafkaConsumer(**connection_args)
        self.consumer.subscribe([self.topic])

    def messages(self):
        raw_msgs = self.consumer.poll(timeout_ms=1000)
        for tp, msgs in raw_msgs.items():
            for msg in msgs:
                logger.info('got msg: %s' % str(msg))
                yield msg.value
        self.consumer.commit()


class PGExporter:
    def __init__(self, connection_args, pool_size=10):
        self.pool = pgpool.ThreadedConnectionPool(1, pool_size, connection_args)

    @staticmethod
    def worker(pool, sql, params):
        conn = None
        while not conn:
            try:
                conn = pool.getconn()
            except pgpool.PoolError:
                logger.warning("No free connection in pool")
                time.sleep(1)

        with conn.cursor() as curs:
            try:
                curs.execute(sql, params)
                conn.commit()
                logger.info("Put to DB: %s" % params)
            except psycopg2.Error as e:
                logger.error(e)
        pool.putconn(conn)

    def submit(self, message):
        sql = """INSERT INTO checks
        (url, timestamp, code, body_check_valid, time)
        VALUES
        (%(url)s, %(timestamp_dt)s, %(code)s, %(body_check_valid)s, %(time)s)
        """
        message = deepcopy(message)
        message['timestamp_dt'] = datetime.fromtimestamp(message['timestamp'])
        thread = threading.Thread(
            target=self.worker, args=(self.pool, sql, message))
        thread.start()


def consumer_loop(consumer, exporter):
    while True:
        for message in consumer.messages():
            exporter.submit(message)
