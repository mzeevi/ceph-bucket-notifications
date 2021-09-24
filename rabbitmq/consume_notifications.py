import pika
import constants

if __name__ == "__main__":
    rabbitmq_endpoint = constants.RABBITMQ_ENDPOINT.split(':')[0]
    topic_name = constants.TOPIC_NAME
    exchange_name = constants.EXCHANGE_NAME
    exchange_type = constants.EXCHANGE_TYPE

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitmq_endpoint))
    channel = connection.channel()

    channel.exchange_declare(exchange=exchange_name, exchange_type=exchange_type)

    result = channel.queue_declare('', durable=True, exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key='#')

    def callback(ch, method, properties, body):
        print(" [x] Received %r" % body.decode())
        ch.basic_ack(delivery_tag=method.delivery_tag)

    print(' [*] Waiting for objects. To exit press CTRL+C')
    channel.basic_consume(queue=queue_name, on_message_callback=callback)
    channel.start_consuming()