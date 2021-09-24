import boto3
import botocore
import constants

if __name__ == "__main__":
    ceph_endpoint = constants.CEPH_ENDPOINT
    access_key = constants.AWS_ACCESS_KEY_ID
    secret_key = constants.AWS_SECRET_ACCESS_KEY
    region = constants.REGION
    bucket_name = constants.BUCKET_NAME
    topic_name = constants.TOPIC_NAME
    zone_name = constants.ZONE_NAME

    s3_client = boto3.client('s3',
                            endpoint_url = ceph_endpoint,
                            aws_access_key_id = access_key,
                            aws_secret_access_key = secret_key,
                            region_name = region,
                            config=botocore.client.Config(signature_version = 's3'))

    # create the S3 bucket
    s3_client.create_bucket(Bucket = bucket_name)

    bucket_notifications_configuration = {
        'TopicConfigurations': [
            {
                'Id': 'rabbitmq-configuration',
                'TopicArn': 'arn:aws:sns:' + zone_name + '::' + topic_name,
                'Events': ['s3:ObjectCreated:*']
            }
        ]
    }

    s3_client.put_bucket_notification_configuration(Bucket = bucket_name,
                                                    NotificationConfiguration=bucket_notifications_configuration)

    print(s3_client.get_bucket_notification_configuration(Bucket=bucket_name))