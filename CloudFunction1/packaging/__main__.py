import boto3
import requests
import json

service_name = "s3"
endpoint_url = "https://kr.object.ncloudstorage.com"
region_name = 'kr-standard'
access_key = "액세스키"
secret_key = "시크릿키"

class ClovaSpeechClient:
    # Clova Speech invoke URL
    invoke_url = "링크"
    # Clova Speech secret key
    secret = "시크릿"

    def req_object_storage(self, data_key, completion, callback, resultToObs, userdata=None, forbiddens=None, boostings=None,
                           wordAlignment=True, fullText=True, diarization=None, sed=None):
        request_body = {
            'dataKey': data_key,
            'language': 'ko-KR',
            'completion': completion,
            'callback': callback,
            'userdata': userdata,
            'wordAlignment': wordAlignment,
            'fullText': fullText,
            'resultToObs' : resultToObs,
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


def main(args):
    try:
        s3 = boto3.client(service_name,
                          endpoint_url=endpoint_url,
                          aws_access_key_id=access_key,
                          aws_secret_access_key=secret_key)

        bucket_name = 'semicolon-recording-voice'
        max_keys = 300

        latest_object = get_latest_object(s3, bucket_name, max_keys)
        if not latest_object:
            return {"done": False, "error_message": "No objects found in the bucket"}

        object_info = {
            'Name': latest_object.get('Key'),
            'Size': latest_object.get('Size'),
            'Owner': latest_object.get('Owner').get('ID')
        }

        res = ClovaSpeechClient().req_object_storage(data_key=latest_object.get('Key'), completion='async',
                                                     callback='https://kr.object.ncloudstorage.com/semicolon-recording-text', resultToObs=True)
        
        return {
            "done": True,
            "latest_object_info": object_info,
            "clova_response": res.text
        }

    except Exception as e:
        return {"done": False, "error_message": str(e)}

#실제 패키징 파일에는 메인 함수 호출 x, 함수 테스트용
# if __name__ == '__main__':
#     args = {}
#     main(args)