# -*- coding: utf-8 -*-

import base64
import json
import http.client

from dotenv import load_dotenv
import os

load_dotenv()


class CompletionExecutor:
    def __init__(self, host, api_key, api_key_primary_val, request_id):
        self._host = host
        self._api_key = api_key
        self._api_key_primary_val = api_key_primary_val
        self._request_id = request_id

    def _send_request(self, completion_request):
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'X-NCP-CLOVASTUDIO-API-KEY': self._api_key,
            'X-NCP-APIGW-API-KEY': self._api_key_primary_val,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': self._request_id
        }

        conn = http.client.HTTPSConnection(self._host)
        conn.request('POST', '/testapp/v1/api-tools/summarization/v2/9211466a82fa438090053eaafc4cb1b6', json.dumps(completion_request), headers)
        response = conn.getresponse()
        result = json.loads(response.read().decode(encoding='utf-8'))
        conn.close()
        return result

    def execute(self, completion_request):
        res = self._send_request(completion_request)
        if res['status']['code'] == '20000':
            return res['result']['text']
        else:
            return 'Error'

    def read_text_from_file(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()


if __name__ == '__main__':
    completion_executor = CompletionExecutor(
        host='clovastudio.apigw.ntruss.com',
        api_key=os.getenv('api_key'),
        api_key_primary_val = os.getenv('api_key_primary_val'),
        request_id=os.getenv('request_id')
    )

    # file_path = '/home/zzu/2024/kea/AI-Service/stt_test1.json'  # Replace this with the path to your file
    # text_content = read_text_from_file(file_path)

    request_data = json.loads("""{
  "texts" : ["A: “모래의 타운 주제는 내일 점심을 무엇을 먹어야 현명한가?” B: “좋은 주제입니다.” B: “탈락, 가벼운 대한 다음 안건” B: “치킨이 좋을 것 같습니다. 점심으로 치킨은 너무 해피한 것 같습니다. 그렇습니까? 무겁습니다. 가벼운 거 없나요?” B: “먹어도 더부룩하지만 활동을 잘 할 수 있는 하지만 배는 부르는” A: “김밥이 좋을 것 같아” B: “너무 좀 더 야무진 걸로” A: “부탁드리겠습니다. 치킨 마요 덮밥” C: “싫습니다.” B: “느낌이 없습니다.” A: “회의 종료합니다.”"],
  "segMinSize" : 300,
  "includeAiFilters" : true,
  "autoSentenceSplitter" : true,
  "segCount" : -1,
  "segMaxSize" : 1000
}""", strict=False)

    response_text = completion_executor.execute(request_data)
    print(request_data)
    print(response_text)
