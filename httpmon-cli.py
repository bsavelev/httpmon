import logging
import argparse

from httpmon.producer import regex_arg, check_loop, KafkaProducerWrapper
from httpmon.consumer import KafkaConsumerWrapper, consumer_loop, PGExporter
from httpmon.utils import prepare_kafka_connection_args

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description='HTTP checker with Apache Kafka processing')
    parser.add_argument(
        '--kafka-server', type=str,
        required=True, help='Kafka server [host:port]')
    parser.add_argument(
        '--kafka-topic', type=str,
        required=True, help='Kafka topic')
    parser.add_argument(
        '--kafka-ca', type=argparse.FileType('r'),
        help='Kafka SSL CA path')
    parser.add_argument(
        '--kafka-cert', type=argparse.FileType('r'),
        help='Kafka SSL certificate path')
    parser.add_argument(
        '--kafka-key', type=argparse.FileType('r'),
        help='Kafka SSL key path')
    parser.add_argument(
        "-v", "--verbosity", action="count",
        help="increase output verbosity", default=0)
    subparser = parser.add_subparsers(help='sub-command help', dest='command')
    parser_producer = subparser.add_parser(
        'producer', help='Perform HTTP check')
    parser_consumer = subparser.add_parser(
        'consumer', help='Consume message and store in SQL')
    parser_consumer.add_argument(
        '-u', '--uri', type=str,
        required=True, help='PostgreSQL connection uri')
    parser_producer.add_argument(
        '-u', '--url', type=str, required=True, help='URL to check')
    parser_producer.add_argument(
        '-t', '--timeout', type=float, default=10.0, help='Check timeout')
    parser_producer.add_argument(
        '-p', '--period', type=float, default=5.0, help='Check period')
    parser_producer.add_argument(
        '-b', '--body', type=regex_arg, help='Regex for body check')
    parser_producer.add_argument(
        '-o', '--oneshot',
        action='store_true', default=False, help='Run check once')
    args = parser.parse_args()

    level = logging.INFO
    if args.verbosity > 0:
        level = logging.DEBUG

    logging.basicConfig(
        format='%(asctime)s [%(levelname)s] '
               '[%(module)s:%(funcName)s:%(lineno)s] %(message)s',
        level=level
    )

    kafka_connection_args = prepare_kafka_connection_args(args)

    if args.command == 'producer':
        url = args.url
        timeout = args.timeout
        body_check_re = args.body
        period = args.period
        oneshot = args.oneshot

        logger.info(
            'run with: url=%s; period=%f; timeout=%f; body_check_re=%s' % (
                url, period, timeout, body_check_re
            ))

        check_loop(
            url, period, timeout, body_check_re,
            KafkaProducerWrapper(kafka_connection_args, args.kafka_topic),
            oneshot=oneshot,
        )
    elif args.command == 'consumer':
        consumer_loop(
            KafkaConsumerWrapper(kafka_connection_args, args.kafka_topic),
            PGExporter(args.uri)
        )


if __name__ == '__main__':
    main()
