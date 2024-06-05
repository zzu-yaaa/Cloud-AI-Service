import boto3
import requests
from dotenv import load_dotenv
import os
from botocore.exceptions import NoCredentialsError


load_dotenv()

service_name = 's3'
endpoint_url = 'https://kr.object.ncloudstorage.com'
region_name = 'kr-standard'
access_key = os.getenv('access_key')
secret_key = os.getenv('secret_key')

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

    source_bucket_name = 'semicolon-recording-text'
    max_keys = 300

    latest_object = get_latest_object(s3, source_bucket_name, max_keys)
    print('Latest object: Name=%s, Size=%d, Owner=%s' % \
          (latest_object.get('Key'), latest_object.get('Size'), latest_object.get('Owner').get('ID')))
    
    set_object_acl_public(s3, source_bucket_name, latest_object.get('Key'))

    try:
        # 네이버 클라우드에서 파일 스트리밍으로 다운로드
        naver_url = f"{endpoint_url}/{source_bucket_name}/{latest_object.get('Key')}"
        response = requests.get(naver_url, stream=True, headers={
            'Authorization': access_key,
            'x-amz-date': "20160825T183244Z",
            'Host': "kr.object.ncloudstorage.com"
        })

        if response.status_code == 200:
            # 아마존 S3에 파일 업로드
            #aws_s3.upload_fileobj(response.raw, aws_bucket_name, aws_object_key)
            print("true")
            print(response.content)
            #print(f'Successfully transferred {naver_object_key} from Naver Cloud to {aws_object_key} in AWS S3.')
        else:
            print(f'Failed to download object from Naver Cloud. Status code: {response.status_code}')
    except NoCredentialsError:
        print('Credentials not available')

    
