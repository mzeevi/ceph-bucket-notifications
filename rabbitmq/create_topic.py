import boto3
import botocore
import urllib.parse
import constants

if __name__ == "__main__":
    ceph_endpoint = constants.CEPH_ENDPOINT
    rabbitmq_endpoint = constants.RABBITMQ_ENDPOINT
    access_key = constants.AWS_ACCESS_KEY_ID
    secret_key = constants.AWS_SECRET_ACCESS_KEY
    region = constants.REGION
    topic_name = constants.TOPIC_NAME
    exchange_name = constants.EXCHANGE_NAME

    sns_client = boto3.client('sns',
                            endpoint_url = ceph_endpoint,
                            aws_access_key_id = access_key,
                            aws_secret_access_key = secret_key,
                            region_name = region,
                            config=botocore.client.Config(signature_version = 's3'))

    endpoint_args = 'push-endpoint=amqp://' + rabbitmq_endpoint + '&amqp-exchange=' + exchange_name + '&amqp-ack-level=broker'
    attributes = {nvp[0]: nvp[1] for nvp in urllib.parse.parse_qsl(endpoint_args, keep_blank_values=True)}

    print(attributes)

    print(sns_client.create_topic(Name=topic_name, Attributes=attributes))