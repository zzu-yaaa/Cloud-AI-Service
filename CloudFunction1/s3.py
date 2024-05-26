import boto3

service_name = 's3'
endpoint_url = 'https://kr.object.ncloudstorage.com'
region_name = 'kr-standard'
access_key = ''
secret_key = ''

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

if __name__ == "__main__":
    s3 = boto3.client(service_name, endpoint_url=endpoint_url, aws_access_key_id=access_key,
                      aws_secret_access_key=secret_key)

    bucket_name = 'semicolon-recording-voice'
    max_keys = 300

    list_bucket_contents(s3, bucket_name, max_keys)

    latest_object = get_latest_object(s3, bucket_name, max_keys)
    print('Latest object: Name=%s, Size=%d, Owner=%s' % \
          (latest_object.get('Key'), latest_object.get('Size'), latest_object.get('Owner').get('ID')))
