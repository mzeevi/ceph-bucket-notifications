# What is Bucket Notifications
Bucket notifications provide a mechanism for sending information out of the Object Storage cluster when certain events are happening on the bucket. Currently, notifications could be sent to: HTTP, AMQP0.9.1 and Kafka endpoints.

A user can create different topics. A topic entity is defined by its name. A user can only associate its topics (via notification configuration) with buckets it owns.

In order to send notifications for events for a specific bucket, a notification entity needs to be created. A notification can be created on a subset of event types, or for all event types (default). The notification may also filter out events based on prefix/suffix and/or regular expression matching of the keys. As well as, on the metadata attributes attached to the object, or the object tags. There can be multiple notifications for any specific topic, and the same topic could be used for multiple notifications.

# How do I use it
There are a few steps to follow in order to use Bucket Notifications. All steps are client-side and are based on the S3 API.

## Step 1: Create a Topic
The topic should be provided with push endpoint parameters that would be used later when a notification is created. Upon successful request, **the response will include the topic ARN that could be later used to reference this topic in the notification request**. To update a topic, use the same command used for topic creation, with the topic name of an existing topic and different endpoint values.

Note that any notification already associated with the topic needs to be re-created for the topic update to take effect.

The following shows the parameters that can be passed to the CreateTopic request, a Python example follows:

```
POST
Action=CreateTopic
&Name=<topic-name>
&push-endpoint=<endpoint>
[&Attributes.entry.1.key=amqp-exchange&Attributes.entry.1.value=<exchange>]
[&Attributes.entry.2.key=amqp-ack-level&Attributes.entry.2.value=none|broker]
[&Attributes.entry.3.key=verify-ssl&Attributes.entry.3.value=true|false]
[&Attributes.entry.4.key=kafka-ack-level&Attributes.entry.4.value=none|broker]
[&Attributes.entry.5.key=use-ssl&Attributes.entry.5.value=true|false]
[&Attributes.entry.6.key=ca-location&Attributes.entry.6.value=<file path>]
[&Attributes.entry.7.key=OpaqueData&Attributes.entry.7.value=<opaque data>]
```
### Request parameters
- push-endpoint: URI of an endpoint to send push notification to
- OpaqueData: opaque data is set in the topic configuration and added to all notifications triggered by the ropic
- HTTP endpoint:
  - URI: `http[s]://<fqdn>[:<port]`
  - port defaults to: `80/443` for HTTP/S accordingly
  - verify-ssl: indicate whether the server certificate is validated by the client or not (“true” by default)
- AMQP0.9.1 endpoint:
  - URI: `amqp://[<user>:<password>@]<fqdn>[:<port>][/<vhost>]`
  - user/password defaults to: guest/guest
  - user/password may only be provided over HTTPS. Topic creation request will be rejected if not
  - port defaults to: `5672`
  - vhost defaults to: `“/”`
  - amqp-exchange: the exchanges must exist and be able to route messages based on topics (mandatory parameter for AMQP0.9.1)
  - amqp-ack-level: no end2end acking is required, as messages may persist in the broker before delivered into their final destination. Two ack methods exist:
    - `none`: message is considered “delivered” if sent to broker
    -  `broker`: message is considered “delivered” if acked by broker (default)
-  Kafka endpoint:
  - URI: `kafka://[<user>:<password>@]<fqdn>[:<port]`
  - if `use-ssl` is set to “true”, secure connection will be used for connecting with the broker (“false” by default)
  - if `ca-location` is provided, and secure connection is used, the specified CA will be used, instead of the default one, to authenticate the broker
  - user/password may only be provided over HTTPS. Topic creation request will be rejected if not
  - user/password may only be provided together with `use-ssl`, connection to the broker would fail if not
  - port defaults to: `9092`
  - kafka-ack-level: no end2end acking is required, as messages may persist in the broker before delivered into their final destination. Two ack methods exist:
    - `none`: message is considered “delivered” if sent to broker
    - `broker`: message is considered “delivered” if acked by broker (default)

### Request response
The response will have the following format:

```
<CreateTopicResponse xmlns="https://sns.amazonaws.com/doc/2010-03-31/">
    <CreateTopicResult>
        <TopicArn></TopicArn>
    </CreateTopicResult>
    <ResponseMetadata>
        <RequestId></RequestId>
    </ResponseMetadata>
</CreateTopicResponse>
```

The topic ARN in the response will have the following format:

```
arn:aws:sns:<zone-group>:<tenant>:<topic>
```

Note that in most cases, tenant would be empty.

### Using Boto3
#### RabbitMQ example
```
import boto3
import botocore
import urllib.parse

if __name__ == "__main__":
    ceph_endpoint = <CEPH_ENDPOINT>
    rabbitmq_endpoint = <RABBITMQ_ENDPOINT>
    access_key = <AWS_ACCESS_KEY_ID>
    secret_key = <AWS_SECRET_ACCESS_KEY>
    region = us-east-1
    topic_name = <TOPIC_NAME>
    exchange_name = <EXCHANGE_NAME>

    sns_client = boto3.client('sns',
                            endpoint_url = ceph_endpoint,
                            aws_access_key_id = access_key,
                            aws_secret_access_key = secret_key,
                            region_name = region,
                            config=botocore.client.Config(signature_version = 's3'))

    endpoint_args = 'push-endpoint=amqp://' + rabbitmq_endpoint + '&amqp-exchange=' + exchange_name + '&amqp-ack-level=broker'
    attributes = {nvp[0]: nvp[1] for nvp in urllib.parse.parse_qsl(endpoint_args, keep_blank_values=True)}

    print(sns_client.create_topic(Name=topic_name, Attributes=attributes))
```
The output of the code above is:

```
{
   "TopicArn":"arn:aws:sns:default::rabbitmq-topic-sds",
   "ResponseMetadata":{
      "RequestId":"95b7e20e-b306-4535-bc75-5162076708d6.94224.1",
      "HTTPStatusCode":200,
      "HTTPHeaders":{
         "x-amz-request-id":"tx000000000000000000001-00614d7b3e-17010-default",
         "content-type":"application/xml",
         "content-length":"296",
         "date":"Fri, 24 Sep 2021 07:16:18 GMT",
         "connection":"Keep-Alive"
      },
      "RetryAttempts":0
   }
}
```

#### Kafka example
```
import boto3
import botocore
import urllib.parse

if __name__ == "__main__":
    ceph_endpoint = <CEPH_ENDPOINT>
    kafka_endpoint = <KAFKA_ENDPOINT>
    access_key = <AWS_ACCESS_KEY_ID>
    secret_key = <AWS_SECRET_ACCESS_KEY>
    region = us-east-1
    topic_name = <TOPIC_NAME>

    sns_client = boto3.client('sns',
                            endpoint_url = ceph_endpoint,
                            aws_access_key_id = access_key,
                            aws_secret_access_key = secret_key,
                            region_name = region,
                            config=botocore.client.Config(signature_version = 's3'))

    endpoint_args = 'push-endpoint=kafka://' + kafka_endpoint + '&kafka-ack-level=broker'
    attributes = {nvp[0]: nvp[1] for nvp in urllib.parse.parse_qsl(endpoint_args, keep_blank_values=True)}

    print(attributes)

    print(sns_client.create_topic(Name=topic_name, Attributes=attributes))
```

The output of the code above is:

```
{
   "TopicArn":"arn:aws:sns:default::kafka-topic-sds",
   "ResponseMetadata":{
      "RequestId":"95b7e20e-b306-4535-bc75-5162076708d6.94224.2",
      "HTTPStatusCode":200,
      "HTTPHeaders":{
         "x-amz-request-id":"tx000000000000000000002-00614d7ca7-17010-default",
         "content-type":"application/xml",
         "content-length":"293",
         "date":"Fri, 24 Sep 2021 07:22:15 GMT",
         "connection":"Keep-Alive"
      },
      "RetryAttempts":0
   }
}
```
**Record the TopicArn, you will need it for the next step**

### Topic Configuration
The topics management API will be derived from AWS Simple Notification Service API. Note that most of the API is not applicable to Ceph, and only the following actions are implemented:

- CreateTopic
- DeleteTopic
- ListTopics

## Step 2: Create a Notification
To link a Topic with a specific bucket, a notification needs to be created:

```
PUT /<bucket name>?notification HTTP/1.1
```

### Request entities
```
<NotificationConfiguration xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
    <TopicConfiguration>
        <Id></Id>
        <Topic></Topic>
        <Event></Event>
        <Filter>
            <S3Key>
                <FilterRule>
                    <Name></Name>
                    <Value></Value>
                </FilterRule>
                 </S3Key>
             <S3Metadata>
                 <FilterRule>
                     <Name></Name>
                     <Value></Value>
                 </FilterRule>
             </S3Metadata>
             <S3Tags>
                 <FilterRule>
                     <Name></Name>
                     <Value></Value>
                 </FilterRule>
             </S3Tags>
         </Filter>
    </TopicConfiguration>
</NotificationConfiguration>
```

| Name                          | Type      | Description                                                                          | Required                                                                                                                                                                                    |
|-------------------------------|-----------|--------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ``NotificationConfiguration`` | Container | Holding list of ``TopicConfiguration`` entities                                                                                                                                                                                                                         | Yes      |
| ``TopicConfiguration``        | Container | Holding ``Id``, ``Topic`` and list of ``Event`` entities                                                                                                                                                                                                                | Yes      |
| ``Id``                        | String    | Name of the notification                                                                                                                                                                                                                                                | Yes      |
| ``Topic``                     | String    | Topic ARN. Topic must be created beforehand                                                                                                                                                                                                                             | Yes      |
| ``Event``                     | String    | List of supported events see: `S3 Notification Compatibility`_.  Multiple ``Event`` entities can be used. If omitted, all events are handled                                                                                                                            | No       |
| ``Filter``                    | Container | Holding ``S3Key``, ``S3Metadata`` and ``S3Tags`` entities                                                                                                                                                                                                               | No       |
| ``S3Key``                     | Container | Holding a list of ``FilterRule`` entities, for filtering based on object key.  At most, 3 entities may be in the list, with ``Name`` be ``prefix``, ``suffix`` or ``regex``. All filter rules in the list must match for the filter to match.                           | No       |
| ``S3Metadata``                | Container | Holding a list of ``FilterRule`` entities, for filtering based on object metadata. All filter rules in the list must match the metadata defined on the object. However, the object still match if it has other metadata entries not listed in the filter.               | No       |
| ``S3Tags``                    | Container | Holding a list of ``FilterRule`` entities, for filtering based on object tags. All filter rules in the list must match the tags defined on the object. However, the object still match it it has other tags not listed in the filter.                                   | No       |
| ``S3Key.FilterRule``          | Container | Holding ``Name`` and ``Value`` entities. ``Name`` would  be: ``prefix``, ``suffix`` or ``regex``. The ``Value`` would hold the key prefix, key suffix or a regular expression for matching the key, accordingly.                                                        | Yes      |
| ``S3Metadata.FilterRule``     | Container | Holding ``Name`` and ``Value`` entities. ``Name`` would be the name of the metadata attribute (e.g. ``x-amz-meta-xxx``). The ``Value`` would be the expected value for this attribute.                                                                                  | Yes      |
| ``S3Tags.FilterRule``         | Container | Holding ``Name`` and ``Value`` entities. ``Name`` would be the tag key, and ``Value`` would be the tag value.                                                                                                                                                           | Yes      |

### Request response

| HTTP Status | Status Code     | Description                                           |
|-------------|-----------------|-------------------------------------------------------|
| ``400``     | MalformedXML    | The XML is not well-formed                            |
| ``400``     | InvalidArgument | Missing Id; Missing/Invalid Topic ARN; Invalid Event  |
| ``404``     | NoSuchBucket    | The bucket does not exist                             |
| ``404``     | NoSuchKey       | The topic does not exist                              |

### Using Boto3
In this example we configure a notification such that every time an object is uploaded to a bucket, an event will be sent to a topic.

```
import boto3
import botocore

if __name__ == "__main__":
    ceph_endpoint = <CEPH_ENDPOINT>
    access_key = <AWS_ACCESS_KEY_ID>
    secret_key = <AWS_SECRET_ACCESS_KEY>
    region = <REGION>
    bucket_name = <BUCKET_NAME>
    
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
                'Id': 'notification-configuration',
                'TopicArn': '<USE THE ARN YOU RECEIVED FROM THE CREATE TOPIC STEP>,
                'Events': ['s3:ObjectCreated:*']
            }
        ]
    }

    s3_client.put_bucket_notification_configuration(Bucket = bucket_name,
                                                    NotificationConfiguration=bucket_notifications_configuration)

    print(s3_client.get_bucket_notification_configuration(Bucket=bucket_name))
```
## Step 3: Test
Write a simple code that uploads objects and consume the messages from the configured topic. The Object Storage cluster creates the Topic in Step 1 so there's no need to create a topic beforehand. However, in case of `RabbitMQ`, a queue and an exchange need to be created, with a routing key suitable for topic, i.e. `routing_key=#`.

This procedure does not explain how to set up `RabbitMQ`, `Kafka` or an `HTTP endpoint`, but feel free to contact us for a basic configuration.

## Event Types

| Event                                         | Supported / Not Supported |
|-----------------------------------------------|---------------------------|
| ``s3:ObjectCreated:*``                        | Supported                 | 
| ``s3:ObjectCreated:Put``                      | Supported                 |
| ``ObjectCreated:Post``                        | Supported                 |
| ``s3:ObjectCreated:Copy``                     | Supported                 |
| ``s3:ObjectCreated:CompleteMultipartUpload``  | Supported                 |
| ``s3:ObjectRemoved:*``                        | Supported                 |
| ``s3:ObjectRemoved:Delete``                   | Supported                 |
| ``s3:ObjectRemoved:DeleteMarkerCreated``      | Supported                 |
| ``s3:ObjectRestore:Post``                     | Not Supported             |
| ``s3:ObjectRestore:Complete``                 | Not Supported             |
| ``s3:ReducedRedundancyLostObject``            | Not Supported             |

## Events
The events are in JSON format (regardless of the actual endpoint), and share the same structure as the S3-compatible events pushed or pulled using the pubsub sync module.

```
{"Records":[
    {
        "eventVersion":"2.1"
        "eventSource":"aws:s3",
        "awsRegion":"",
        "eventTime":"",
        "eventName":"",
        "userIdentity":{
            "principalId":""
        },
        "requestParameters":{
            "sourceIPAddress":""
        },
        "responseElements":{
            "x-amz-request-id":"",
            "x-amz-id-2":""
        },
        "s3":{
            "s3SchemaVersion":"1.0",
            "configurationId":"",
            "bucket":{
                "name":"",
                "ownerIdentity":{
                    "principalId":""
                },
                "arn":"",
                "id:""
            },
            "object":{
                "key":"",
                "size":"",
                "eTag":"",
                "versionId":"",
                "sequencer": "",
                "metadata":[],
                "tags":[]
            }
        },
        "eventId":"",
        "opaqueData":"",
    }
]}
```

| Key                                     | Explanation                                                                                                                                       
|-----------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|
| ``awsRegion:*``                         | zonegroup                                                                                                                                         | 
| ``eventTime``                           | timestamp indicating when the event was triggered                                                                                                 |
| ``eventName``                           | see list of events above                                                                                                                          |
| ``userIdentity.principalId``            | user that triggered the change                                                                                                                    |
| ``requestParameters.sourceIPAddress``   | not supported                                                                                                                                     | 
| ``responseElements.x-amz-request-id``   | request ID of the original change                                                                                                                 |
| ``responseElements.x_amz_id_2``         | RGW on which the change was made                                                                                                                  |
| ``s3.configurationId``                  | notification ID that created the event                                                                                                            |
| ``s3.bucket.name``                      | name of the bucket                                                                                                                                |
| ``s3.bucket.ownerIdentity.principalId`` | owner of the bucket                                                                                                                               |
| ``s3.bucket.arn``                       | ARN of the bucket                                                                                                                                 |
| ``s3.bucket.id``                        | id of the bucket (an extension to the S3 notification API)                                                                                        |
| ``s3.object.key``                       | object key                                                                                                                                        |
| ``s3.object.size``                      | object size                                                                                                                                       |
| ``s3.object.eTag``                      | object etag                                                                                                                                       |
| ``s3.object.version``                   | object version in case of versioned bucket                                                                                                        |
| ``s3.object.sequencer``                 | monotonically increasing identifier of the change per object (hexadecimal format)                                                                 |
| ``s3.object.metadata``                  | any metadata set on the object sent as: x-amz-meta- (an extension to the S3 notification API)                                                     |
| ``s3.object.tags``                      | any tags set on the objcet (an extension to the S3 notification API)                                                                              |
| ``s3.eventId``                          | unique ID of the event, that could be used for acking (an extension to the S3 notification API)                                                   |
| ``s3.opaqueData``                       | opaque data is set in the topic configuration and added to all notifications triggered by the ropic (an extension to the S3 notification API)     |

### Simplified Example
The following shows the output received by a Kafka Consumer:

```
{
   "Records":[
      {
         "eventVersion":"2.2",
         "eventSource":"ceph:s3",
         "awsRegion":"",
         "eventTime":"2021-09-24T08:54:48.676394Z",
         "eventName":"s3:ObjectCreated:Put",
         "userIdentity":{
            "principalId":"test"
         },
         "requestParameters":{
            "sourceIPAddress":""
         },
         "responseElements":{
            "x-amz-request-id":"95b7e20e-b306-4535-bc75-5162076708d6.94224.14",
            "x-amz-id-2":"17010-default-default"
         },
         "s3":{
            "s3SchemaVersion":"1.0",
            "configurationId":"kafka-configuration",
            "bucket":{
               "name":"kafka-notifications-sds",
               "ownerIdentity":{
                  "principalId":"test"
               },
               "arn":"arn:aws:s3:::kafka-notifications-sds",
               "id":"kafka-notifications-sds:95b7e20e-b306-4535-bc75-5162076708d6.84129.17"
            },
            "object":{
               "key":"mock1",
               "size":24,
               "etag":"8d70234f63225bebc7b48464b5d734c1",
               "versionId":"",
               "sequencer":"59924D6162A4CE1E",
               "metadata":[
                  
               ],
               "tags":[
                  
               ]
            }
         },
         "eventId":"1632473689.516858.8d70234f63225bebc7b48464b5d734c1",
         "opaqueData":""
      }
   ]
}
```

