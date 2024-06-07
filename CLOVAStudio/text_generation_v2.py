# -*- coding: utf-8 -*-

import requests
import json

class CompletionExecutor:
    def __init__(self, host, api_key, api_key_primary_val, request_id):
        self._host = host
        self._api_key = api_key
        self._api_key_primary_val = api_key_primary_val
        self._request_id = request_id

    def execute(self, completion_request):
        headers = {
            'X-NCP-CLOVASTUDIO-API-KEY': self._api_key,
            'X-NCP-APIGW-API-KEY': self._api_key_primary_val,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': self._request_id,
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'text/event-stream'
        }

        complete_message = ""
        is_signal_event_received = False

        with requests.post(self._host + '/testapp/v1/chat-completions/HCX-DASH-001',
                           headers=headers, json=completion_request, stream=True) as r:
            for line in r.iter_lines():
                if line:
                    line_decoded = line.decode("utf-8")
                    if line_decoded.startswith("data:"):
                        data_json = line_decoded[5:].strip()  # 'data:' 이후의 문자열을 가져옴
                        data = json.loads(data_json)  # JSON 문자열을 파싱
                        message = data.get("message", {})
                        if message.get("role") == "assistant":
                            complete_message += message.get("content", "")
                    elif line_decoded.startswith("event:result"):
                        is_signal_event_received = True
                        break  # 'event:result' 이벤트를 만나면 루프를 종료하고 결과를 반환

        if is_signal_event_received:
            print(complete_message)  # 완전한 메시지 출력
            with open("result.txt", "w", encoding="utf-8") as file:
                file.write(complete_message)  # 결과를 텍스트 파일로 저장

def read_local_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

if __name__ == '__main__':
    # 로컬 텍스트 파일 경로 설정
    local_file_path = '/home/zzu/2024/kea/AI-Service/CLOVAStudio/test_script.txt'

    # 텍스트 파일에서 내용 읽기
    file_content = read_local_text_file(local_file_path)

    completion_executor = CompletionExecutor(
        host='https://clovastudio.stream.ntruss.com',
        api_key='NTA0MjU2MWZlZTcxNDJiY9ZEfO75vfZxynekgN7roWNRAMsquTx0rs56sChcM2xd',
        api_key_primary_val='EEU8W1DSp2WG9xluqwmcf6vGHtgJ1z1LfLc2dZ0C',
        request_id='062aeba7-3ff8-41a4-8693-0e5d1d6c45de'
    )

    fixed_content = (
        "키워드:\r\n"
        "A: “모래의 타운 주제는 내일 점심을 무엇을 먹어야 현명한가?” "
        "B: “좋은 주제입니다.” "
        "B: “탈락, 가벼운 대한 다음 안건” "
        "B: “치킨이 좋을 것 같습니다. 점심으로 치킨은 너무 해피한 것 같습니다. "
        "그렇습니까? 무겁습니다. 가벼운 거 없나요?” "
        "B: “먹어도 더부룩하지만 활동을 잘 할 수 있는 하지만 배는 부르는” "
        "A: “김밥이 좋을 것 같아” "
        "B: “너무 좀 더 야무진 걸로” "
        "A: “부탁드리겠습니다. 치킨 마요 덮밥” "
        "C: “싫습니다.” "
        "B: “느낌이 없습니다.” "
        "A: “회의 종료합니다.”\r\n\r\n"
        "회의록:\r\n\r\n"
        "참석자\r\n"
        "A, B, C\r\n"
        "주요 내용\r\n"
        "A가 \"모래의 타운 주제는 내일 점심을 무엇을 먹어야 현명한가?\"라고 제안함.\r\n"
        "B는 이 주제를 좋아하나 치킨이 너무 무겁다고 언급하며, 가벼운 대안을 찾으려 함.\r\n"
        "A는 김밥을 제안했으나, B는 좀 더 야무진 음식을 원함.\r\n"
        "A는 치킨 마요 덮밥을 제안했으나, C는 이를 싫어함.\r\n"
        "B는 느낌이 없다고 언급함.\r\n"
        "A는 회의를 종료함.\r\n"
        "결론\r\n"
        "내일 점심 메뉴에 대해 다양한 의견이 제시되었으나, 최종 결정에는 이르지 못했습니다. "
        "치킨, 김밥, 치킨 마요 덮밥 등 다양한 제안이 나왔으나 만족스러운 결론을 도출하지 못했으며, "
        "다음 회의에서 추가 논의가 필요합니다.\r\n\r\n\r\n"
        "###\r\n\r\n"
        "키워드:\r\n"
    )

    combined_content = fixed_content + file_content

    preset_text = [
        {"role": "system", "content": ""},
        {"role": "user", "content": combined_content}
    ]

    request_data = {
        'messages': preset_text,
        'topP': 0.8,
        'topK': 0,
        'maxTokens': 500,
        'temperature': 0.3,
        'repeatPenalty': 3.0,
        'stopBefore': [],
        'includeAiFilters': True,
        'seed': 0
    }

    completion_executor.execute(request_data)
