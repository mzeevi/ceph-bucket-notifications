import boto3
import botocore
import constants

if __name__ == "__main__":
    ceph_endpoint = constants.CEPH_ENDPOINT
    access_key = constants.AWS_ACCESS_KEY_ID
    secret_key = constants.AWS_SECRET_ACCESS_KEY
    region = constants.REGION
    bucket_name = constants.BUCKET_NAME

    s3_client = boto3.client('s3',
                            endpoint_url = ceph_endpoint,
                            aws_access_key_id = access_key,
                            aws_secret_access_key = secret_key,
                            region_name = region,
                            config = botocore.client.Config(signature_version='s3'))

    # upload_files
    object_path = './mock_file.txt'
    object_name = 'mock1'
    # create the S3 bucket
    s3_client.create_bucket(Bucket = bucket_name)
    s3_client.upload_file(object_path, bucket_name, object_name)

    print("uploaded")
