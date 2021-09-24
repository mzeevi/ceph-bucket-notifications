import kafka
import json
import constants

if __name__ == "__main__":
    topic_name = constants.TOPIC_NAME
    bootstrap_server = constants.KAFKA_ENDPOINT

    consumer = kafka.KafkaConsumer(topic_name,
                             bootstrap_servers=bootstrap_server,
                             auto_offset_reset='earliest',
                             enable_auto_commit=True,
                             value_deserializer=lambda x: json.loads(x.decode('utf-8')))

    for message in consumer:
        print("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                             message.offset, message.key,
                                             message.value))