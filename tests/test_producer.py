import unittest
from httpmon.producer import (
    check, check_body, check_loop, KafkaProducerWrapper
)
from httpmon.stub import KafkaProducerStub


class CheckBodyTestCase(unittest.TestCase):
    def test_empty_body(self):
        self.assertFalse(check_body('', '.*'))

    def test_empty_regex(self):
        self.assertFalse(check_body('test', ''))

    def test_match(self):
        self.assertTrue(check_body('<html>ffff', '.*<html.*>'))

    def test_not_match(self):
        self.assertFalse(check_body('<html>ffff', 'nonexists'))


class CheckURLTestCase(unittest.TestCase):
    def test_200(self):
        r = check('https://www.google.com')
        self.assertEqual(r['code'], 200)

    def test_301(self):
        """test not follow redirects"""
        r = check('https://google.com')
        self.assertEqual(r['code'], 301)

    def test_nonexists_domain(self):
        r = check('https://google1111.com')
        self.assertEqual(r['code'], 0)

    def test_request_timeout(self):
        r = check(
            'http://slowwly.robertomurray.co.uk'
            '/delay/2000/url/https://www.google.com',
            timeout=1)
        self.assertEqual(r['code'], 499)
        self.assertEqual(r['time'], 1)

    def test_200_body_check(self):
        r = check('https://www.google.com', body_check_re='.*Google.*')
        self.assertTrue(r['body_check_valid'])

    def test_with_producer(self):
        topic = 'unittest'
        producer = KafkaProducerWrapper({}, topic=topic, kafka_cls=KafkaProducerStub)
        r = check('https://www.google.com', producer=producer)
        self.assertEqual(r['code'], 200)
        self.assertEqual(len(producer.producer.messages[topic]), 1)
        self.assertEqual(producer.producer.messages[topic][0]['code'], 200)


class CheckLoopTestCase(unittest.TestCase):
    def test_loop(self):
        topic = 'unittest'
        producer = KafkaProducerWrapper({}, topic=topic, kafka_cls=KafkaProducerStub)
        check_loop(
            'https://www.google.com',
            producer=producer, period=1, oneshot=True)
        self.assertEqual(len(producer.producer.messages[topic]), 1)
        self.assertEqual(producer.producer.messages[topic][0]['code'], 200)
