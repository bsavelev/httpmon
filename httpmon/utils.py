from collections import namedtuple

KafkaArgs = namedtuple(
    'KafkaArgs',
    [
        'kafka_server',
        'kafka_ca',
        'kafka_cert',
        'kafka_key',
    ])


def prepare_kafka_connection_args(args):
    kafka_ssl = {}
    for kafka_arg in ['kafka_ca', 'kafka_cert', 'kafka_key']:
        kafka_ssl[kafka_arg] = getattr(args, kafka_arg)

    kafka_connection_args = {
        'bootstrap_servers': args.kafka_server,
    }
    if all(kafka_ssl.values()):
        kafka_connection_args_ssl = {
            'security_protocol': 'SSL',
            'ssl_cafile': kafka_ssl['kafka_ca'],
            'ssl_certfile': kafka_ssl['kafka_cert'],
            'ssl_keyfile': kafka_ssl['kafka_key'],
        }
        kafka_connection_args.update(kafka_connection_args_ssl)
    return kafka_connection_args
