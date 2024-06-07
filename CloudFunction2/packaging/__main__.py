import boto3
import requests
import json
from botocore.exceptions import NoCredentialsError

service_name = 's3'
endpoint_url = 'https://kr.object.ncloudstorage.com'
region_name = 'kr-standard'
naver_access_key = '네이버 액세스키'
naver_secret_key = '네이버 시크릿키'

aws_access_key = 'aws 액세스키'
aws_secret_key = 'aws 시크릿키'

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
    return f"Object ACL for {object_name} in {bucket_name}: {response}"

def main(args):
    naver_s3 = boto3.client(service_name, endpoint_url=endpoint_url, aws_access_key_id=naver_access_key,
                      aws_secret_access_key=naver_secret_key)
    
    aws_s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)

    source_bucket_name = 'semicolon-recording-text'
    max_keys = 300
    target_bucket_name = 'semicolon-stt-result'

    latest_object = get_latest_object(naver_s3, source_bucket_name, max_keys)
    latest_object_info = 'Latest object: Name=%s, Size=%d, Owner=%s' % \
                         (latest_object.get('Key'), latest_object.get('Size'), latest_object.get('Owner').get('ID'))
    
    acl_response = set_object_acl_public(naver_s3, source_bucket_name, latest_object.get('Key'))

    try:
        # 네이버 클라우드에서 파일 스트리밍으로 다운로드
        naver_url = f"{endpoint_url}/{source_bucket_name}/{latest_object.get('Key')}"
        response = requests.get(naver_url, stream=True, headers={
            'Authorization': naver_access_key,
            'x-amz-date': "20160825T183244Z",
            'Host': "kr.object.ncloudstorage.com"
        })

        if response.status_code == 200:
            # 아마존 S3에 파일 업로드
            aws_s3.upload_fileobj(response.raw, target_bucket_name, latest_object.get('Key'))
            return {
                "done": True,
                "latest_object_info": latest_object_info,
                "acl_response": acl_response,
                "message": "File successfully transferred",
            }
        else:
            return {
                "done": False,
                "error_message": f'Failed to download object from Naver Cloud. Status code: {response.status_code}'
            }
    except NoCredentialsError:
        return {"done": False, "error_message": 'Credentials not available'}

# 실제 패키징 파일에는 메인 함수 호출 x, 함수 테스트용
if __name__ == '__main__':
    args = {}
    main(args)
