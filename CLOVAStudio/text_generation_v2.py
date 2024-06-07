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

if __name__ == '__main__':
    completion_executor = CompletionExecutor(
        host='https://clovastudio.stream.ntruss.com',
        api_key='NTA0MjU2MWZlZTcxNDJiY9ZEfO75vfZxynekgN7roWNRAMsquTx0rs56sChcM2xd',
        api_key_primary_val='EEU8W1DSp2WG9xluqwmcf6vGHtgJ1z1LfLc2dZ0C',
        request_id='062aeba7-3ff8-41a4-8693-0e5d1d6c45de'
    )

    preset_text = [{"role":"system","content":""},{"role":"user","content":"키워드:\r\nA: “모래의 타운 주제는 내일 점심을 무엇을 먹어야 현명한가?” B: “좋은 주제입니다.” B: “탈락, 가벼운 대한 다음 안건” B: “치킨이 좋을 것 같습니다. 점심으로 치킨은 너무 해피한 것 같습니다. 그렇습니까? 무겁습니다. 가벼운 거 없나요?” B: “먹어도 더부룩하지만 활동을 잘 할 수 있는 하지만 배는 부르는” A: “김밥이 좋을 것 같아” B: “너무 좀 더 야무진 걸로” A: “부탁드리겠습니다. 치킨 마요 덮밥” C: “싫습니다.” B: “느낌이 없습니다.” A: “회의 종료합니다.”\r\n\r\n회의록:\r\n\r\n참석자\r\nA, B, C\r\n주요 내용\r\nA가 \"모래의 타운 주제는 내일 점심을 무엇을 먹어야 현명한가?\"라고 제안함.\r\nB는 이 주제를 좋아하나 치킨이 너무 무겁다고 언급하며, 가벼운 대안을 찾으려 함.\r\nA는 김밥을 제안했으나, B는 좀 더 야무진 음식을 원함.\r\nA는 치킨 마요 덮밥을 제안했으나, C는 이를 싫어함.\r\nB는 느낌이 없다고 언급함.\r\nA는 회의를 종료함.\r\n결론\r\n내일 점심 메뉴에 대해 다양한 의견이 제시되었으나, 최종 결정에는 이르지 못했습니다. 치킨, 김밥, 치킨 마요 덮밥 등 다양한 제안이 나왔으나 만족스러운 결론을 도출하지 못했으며, 다음 회의에서 추가 논의가 필요합니다.\r\n\r\n\r\n###\r\n\r\n키워드:\r\nA : 제가 경험했던 것들 아니면 생각했던 것들도 좀 많이 공유를 할 수 있는 시간이 되면 여러분들한테도 조금 도움이 되지 않을까 꼭 여러분들이 연구를 하는 게 아니더라도\r\nA : 여러분들이 회사에 현업에 가더라도 연구하는 관점에서 생각하는 것들은 현업에 가서도 특히나 중요하거든요.\r\nA : 여러분들이 그냥 회사에서 기계처럼 일할 게 아니잖아요. 회사에서 생각하면서 주도하고\r\nA : 상사로부터 인정받으려면은 결국 시키는 것만 기계적으로 해가지고는 한계가 있거든요. 그럼 결국에는 회사 가서도 내가 인정받으려면 약간의 연구자의 마인드가 있어야 돼요.\r\nA : 그래서 그런 관점에서 저도 회사에서 삼성에서 제가 3년 동안 일도 해봤고 그리고 지금은 이제 연구를 메인으로 하지만\r\nA : 연구와 현업 간의 조화 그리고 두 개의 차이점 차이점과 또 공통점들도 제가 다 경험을 했거든요.\r\nA : 그러니까 현업에서 일하는 거와 연구와 다른 점도 확실히 있어요. 다른 점도 있는데 근데 또\r\nA : 공유하는 가치도 또 동시에 있기 때문에 여러분들이 제가 중간중간에 연구와 관련된\r\nA : 이야기들 하면은 여러분 나름대로 소화를 해서 여러분들 각자에 맞게 적용을 해보는 것도 좋을 것 같습니다.\r\nA : 그래서 오늘 첫 시간이니까 신라 것으만 하고 그냥 간단히 마칠게요. 그래서 우리 다음 수업부터 이제 본격적으로 진행하도록 하겠습니다. 질문 있을\r\nA : 따로 없으면 끝나고 개인적으로 해도 되고 수업 여기까지 하겠습니다."}]

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
