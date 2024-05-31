# -*- coding: utf-8 -*-

import requests
from dotenv import load_dotenv
import os

load_dotenv()


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

        with requests.post(self._host + '/testapp/v1/chat-completions/HCX-DASH-001',
                           headers=headers, json=completion_request, stream=True) as r:
            for line in r.iter_lines():
                if line:
                    print(line.decode("utf-8"))


if __name__ == '__main__':
    completion_executor = CompletionExecutor(
        host='https://clovastudio.stream.ntruss.com',
        api_key=os.getenv('api_key'),
        api_key_primary_val = os.getenv('api_key_primary_val'),
        request_id=os.getenv('request_id')
    )

    #키워드, 회의록, 키워드 순으로
    preset_text = [{"role":"system","content":""},{"role":"user","content":"키워드:\nA: “모래의 타운 주제는 내일 점심을 무엇을 먹어야 현명한가?” B: “좋은 주제입니다.” B: “탈락, 가벼운 대한 다음 안건” B: “치킨이 좋을 것 같습니다. 점심으로 치킨은 너무 해피한 것 같습니다. 그렇습니까? 무겁습니다. 가벼운 거 없나요?” B: “먹어도 더부룩하지만 활동을 잘 할 수 있는 하지만 배는 부르는” A: “김밥이 좋을 것 같아” B: “너무 좀 더 야무진 걸로” A: “부탁드리겠습니다. 치킨 마요 덮밥” C: “싫습니다.” B: “느낌이 없습니다.” A: “회의 종료합니다.”\n\n회의록:\n\n\n참석자\n\nA\r\nB\r\nC\r\n주요 내용\r\nA는 \"모래의 타운 주제는 내일 점심을 무엇을 먹어야 현명한가?\"라고 제안했습니다.\r\nB는 이 주제를 좋아하며, \"탈락, 가벼운 대한 다음 안건\"에 대해 언급했습니다.\r\nB는 점심으로 치킨을 먹는 것이 좋을 것 같다고 제안했습니다. 그러나 치킨은 무겁다고 느껴질 수 있으므로 가벼운 대안이 필요하다고 언급했습니다.\r\nB는 먹어도 더부룩하지만 활동을 잘 할 수 있는 음식에 대해 언급했습니다.\r\nA는 김밥이 좋을 것 같다고 제안했습니다.\r\nB는 좀 더 야무진 음식을 원했습니다.\r\nA는 치킨 마요 덮밥을 요청했습니다.\r\nC는 치킨 마요 덮밥을 싫어했습니다.\r\nB는 느낌이 없다고 언급했습니다.\r\nA는 회의를 종료했습니다.\r\n결론\r\n회의에서는 내일 점심 메뉴에 대한 다양한 의견이 제시되었습니다. 치킨, 김밥, 치킨 마요 덮밥 등 다양한 음식에 대한 의견이 나왔지만, 최종 결정은 내려지지 않았습니다. 다음 회의에서 이 주제를 다시 논의할 필요가 있습니다.\n\n\n###\n\n\n키워드:\nA: “안녕하세요, 오늘의 주제는 우리 팀의 다음 프로젝트에 대한 것입니다. 아이디어가 있으신 분은 자유롭게 말씀해주세요.”\r\n\r\nB: “저는 최근에 머신러닝에 대해 많이 공부하고 있습니다. 우리 다음 프로젝트에서 머신러닝을 활용하는 것은 어떨까요?”\r\n\r\nC: “그것은 흥미로운 아이디어입니다. 하지만 우리 팀은 머신러닝에 대한 경험이 많지 않습니다. 우리가 이를 학습하고 구현하는 데 필요한 시간과 자원을 감당할 수 있을까요?”\r\n\r\nA: “C님의 말씀이 맞습니다. 우리는 머신러닝에 대한 교육을 받을 시간이 필요할 것입니다. 하지만 이는 우리 팀이 새로운 기술을 배우고 성장하는 좋은 기회가 될 수 있습니다.”\r\n\r\nB: “저도 A님의 의견에 동의합니다. 우리는 이 도전을 받아들이고 머신러닝에 대해 더 배워야 합니다.”\r\n\r\nC: “그럼, 우리는 이 주제에 대해 더 연구하고 다음 회의에서 논의하기로 합시다.”\r\n\r\nA: “좋습니다. 그럼 오늘 회의를 여기서 마치겠습니다. 감사합니다.”"}]

    request_data = {
        'messages': preset_text,
        'topP': 0.8,
        'topK': 0,
        'maxTokens': 450,
        'temperature': 0.5,
        'repeatPenalty': 2.95,
        'stopBefore': ['"###\n"', '키워드:', '회의록:'],
        'includeAiFilters': True,
        'seed': 0
    }

    print(preset_text)
    completion_executor.execute(request_data)
