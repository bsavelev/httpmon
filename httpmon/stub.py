from collections import defaultdict


class KafkaProducerStub:
    def __init__(self, *args, **kwargs):
        self.messages = defaultdict(list)

    def send(self, topic, message):
        self.messages[topic].append(message)

    def flush(self):
        pass
