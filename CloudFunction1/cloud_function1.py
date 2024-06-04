import boto3
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

service_name = 's3'
endpoint_url = 'https://kr.object.ncloudstorage.com'
region_name = 'kr-standard'
access_key = os.getenv('access_key')
secret_key = os.getenv('secret_key')

class ClovaSpeechClient:
    # Clova Speech invoke URL
    invoke_url = os.getenv('invoke_url')
    # Clova Speech secret key
    secret = os.getenv('secret')

    def req_url(self, url, completion, callback=None, userdata=None, forbiddens=None, boostings=None, wordAlignment=True, fullText=True, diarization=None, sed=None):
        request_body = {
            'url': url,
            'language': 'ko-KR',
            'completion': completion,
            'callback': callback,
            'userdata': userdata,
            'wordAlignment': wordAlignment,
            'fullText': fullText,
            'forbiddens': forbiddens,
            'boostings': boostings,
            'diarization': diarization,
            'sed': sed,
        }
        headers = {
            'Accept': 'application/json;UTF-8',
            'Content-Type': 'application/json;UTF-8',
            'X-CLOVASPEECH-API-KEY': self.secret
        }
        return requests.post(headers=headers,
                             url=self.invoke_url + '/recognizer/url',
                             data=json.dumps(request_body).encode('UTF-8'))

    def req_object_storage(self, data_key, completion, callback=None, userdata=None, forbiddens=None, boostings=None,
                           wordAlignment=True, fullText=True, diarization=None, sed=None):
        request_body = {
            'dataKey': data_key,
            'language': 'ko-KR',
            'completion': completion,
            'callback': callback,
            'userdata': userdata,
            'wordAlignment': wordAlignment,
            'fullText': fullText,
            'forbiddens': forbiddens,
            'boostings': boostings,
            'diarization': diarization,
            'sed': sed,
        }
        headers = {
            'Accept': 'application/json;UTF-8',
            'Content-Type': 'application/json;UTF-8',
            'X-CLOVASPEECH-API-KEY': self.secret
        }
        return requests.post(headers=headers,
                             url=self.invoke_url + '/recognizer/object-storage',
                             data=json.dumps(request_body).encode('UTF-8'))

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


    """
    지정된 object storage의 모든 객체 중 가장 최근에 추가된 객체 반환
    
    """
    s3 = boto3.client(service_name, endpoint_url=endpoint_url, aws_access_key_id=access_key,
                      aws_secret_access_key=secret_key)

    bucket_name = 'semicolon-recording-voice'
    max_keys = 300

    #list_bucket_contents(s3, bucket_name, max_keys)

    latest_object = get_latest_object(s3, bucket_name, max_keys)
    print('Latest object: Name=%s, Size=%d, Owner=%s' % \
          (latest_object.get('Key'), latest_object.get('Size'), latest_object.get('Owner').get('ID')))
    

    """
    clova speech api 호출    
    """
    #res = ClovaSpeechClient().req_url(url='https://kr.object.ncloudstorage.com/semicolon-recording-voice/test1.m4a', completion='sync')
    res = ClovaSpeechClient().req_object_storage(data_key=latest_object.get('Key'), completion='sync')
    print(res.text)