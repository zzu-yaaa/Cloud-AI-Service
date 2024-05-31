import boto3
from dotenv import load_dotenv
import os

load_dotenv()

service_name = 's3'
endpoint_url = 'https://kr.object.ncloudstorage.com'
region_name = 'kr-standard'
access_key = os.getenv('access_key')
secret_key = os.getenv('secret_key')

def list_bucket_contents(s3, bucket_name, max_keys):
    response = s3.list_objects(Bucket=bucket_name, MaxKeys=max_keys)

    print('list all in the bucket')

    while True:
        print('IsTruncated=%r' % response.get('IsTruncated'))
        print('Marker=%s' % response.get('Marker'))
        print('NextMarker=%s' % response.get('NextMarker'))

        print('Object List')
        for content in response.get('Contents'):
            print(' Name=%s, Size=%d, Owner=%s' % \
                  (content.get('Key'), content.get('Size'), content.get('Owner').get('ID')))

        if response.get('IsTruncated'):
            response = s3.list_objects(Bucket=bucket_name, MaxKeys=max_keys,
                                       Marker=response.get('NextMarker'))
        else:
            break

def get_latest_object(s3, bucket_name, max_keys):
    response = s3.list_objects(Bucket=bucket_name, MaxKeys=max_keys)

    latest_object = None
    latest_time = None

    while True:
        for content in response.get('Contents'):
            if latest_time is None or content.get('LastModified') > latest_time:
                latest_time = content.get('LastModified')
                latest_object = content

        if response.get('IsTruncated'):
            response = s3.list_objects(Bucket=bucket_name, MaxKeys=max_keys,
                                       Marker=response.get('NextMarker'))
        else:
            break

    return latest_object

def set_bucket_acl(s3, bucket_name):
    """
    Set the ACL of the specified bucket to 'public-read'.

    :param s3: Boto3 S3 client
    :param bucket_name: Name of the S3 bucket
    """
    s3.put_bucket_acl(Bucket=bucket_name, ACL='public-read')
    response = s3.get_bucket_acl(Bucket=bucket_name)
    print(f"Bucket ACL for {bucket_name}: {response}")

def set_object_acl(s3, bucket_name, object_name, owner_id, target_id):
    """
    Set the ACL of the specified object.

    :param s3: Boto3 S3 client
    :param bucket_name: Name of the S3 bucket
    :param object_name: Name of the S3 object
    :param owner_id: Canonical ID of the object owner
    :param target_id: Canonical ID of the user to be granted read access
    """
    s3.put_object_acl(
        Bucket=bucket_name,
        Key=object_name,
        AccessControlPolicy={
            'Grants': [
                {
                    'Grantee': {
                        'ID': owner_id,
                        'Type': 'CanonicalUser'
                    },
                    'Permission': 'FULL_CONTROL'
                },
                {
                    'Grantee': {
                        'ID': target_id,
                        'Type': 'CanonicalUser'
                    },
                    'Permission': 'READ'
                }
            ],
            'Owner': {
                'ID': owner_id
            }
        }
    )
    response = s3.get_object_acl(Bucket=bucket_name, Key=object_name)
    print(f"Object ACL for {object_name} in {bucket_name}: {response}")

def set_object_acl_public(s3, bucket_name, object_name):
    """
    Set the ACL of the specified object to 'public-read'.

    :param s3: Boto3 S3 client
    :param bucket_name: Name of the S3 bucket
    :param object_name: Name of the S3 object
    """
    s3.put_object_acl(Bucket=bucket_name, Key=object_name, ACL='public-read')
    response = s3.get_object_acl(Bucket=bucket_name, Key=object_name)
    print(f"Object ACL for {object_name} in {bucket_name}: {response}")

if __name__ == "__main__":
    s3 = boto3.client(service_name, endpoint_url=endpoint_url, aws_access_key_id=access_key,
                      aws_secret_access_key=secret_key)

    source_bucket_name = 'semicolon-recording-voice'
    max_keys = 300

    list_bucket_contents(s3, source_bucket_name, max_keys)

    latest_object = get_latest_object(s3, source_bucket_name, max_keys)
    print('Latest object: Name=%s, Size=%d, Owner=%s' % \
          (latest_object.get('Key'), latest_object.get('Size'), latest_object.get('Owner').get('ID')))
    
    target_bucket_name = 'semicolon-recording-text'
    object_name = 'stt_test1.json'
    owner_id = 'test-owner-id'
    target_id = 'test-user-id'
    
    # 버킷 ACL 설정
    #set_bucket_acl(s3, target_bucket_name)

    # 객체 ACL 설정
    set_object_acl_public(s3, target_bucket_name, object_name)
