import re
import threading
import time
import requests
import logging
import json
from kafka import KafkaProducer

logger = logging.getLogger(__name__)


class KafkaProducerWrapper:
    def __init__(self, connection_args, topic, kafka_cls=KafkaProducer):
        self.topic = topic
        connection_args['value_serializer'] = \
            lambda v: json.dumps(v).encode('utf-8')
        self.producer = kafka_cls(**connection_args)

    def send(self, message):
        logger.info('put to queue: %s' % message)
        self.producer.send(self.topic, message)
        self.producer.flush()


def check_body(body, regex):
    """match string with regex"""
    if body and regex:
        return bool(re.match(regex, str(body)))
    else:
        return False


def check(url, body_check_re=r'', timeout=10.0, producer=None):
    """check url with timeout and body regex check"""
    timestamp = time.time()
    code = 0
    body = None
    response_time = timeout

    try:
        response = requests.get(
            url,
            timeout=timeout,
            allow_redirects=False,
            headers={
                'UserAgent': 'Aiven health checker/0.1'
            }
        )
    except requests.Timeout:
        code = 499  # client closed request
    except requests.RequestException:
        pass
    else:
        code = response.status_code
        response_time = response.elapsed.total_seconds()
        body = response.content

    body_check_valid = check_body(body, body_check_re)

    message = {
        'timestamp': timestamp,
        'code': code,
        'body_check_valid': body_check_valid,
        'time': response_time,
        'url': url,
    }
    if producer:
        producer.send(message)
    return message


def check_loop(
        url, period=5, timeout=10, body_check_re='',
        producer=None, oneshot=False):
    """inf loop for url checks
    """
    while True:
        worker = threading.Thread(target=check, kwargs={
            'url': url,
            'timeout': timeout,
            'body_check_re': body_check_re,
            'producer': producer,
        })
        logger.info('check url=%s' % url)
        worker.start()
        time.sleep(period)
        if oneshot:
            return


def regex_arg(regex):
    """custom regex type from https://stackoverflow.com/a/37472037"""
    try:
        re.compile(regex)
    except re.error:
        raise ValueError
    return regex
