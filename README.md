# Bbang : 협업을 위한 간편하고 통합된 서비스
> 음성 회의 이후 회의록 생성 기능

</br>

## 아키텍처

![aiservice](https://github.com/user-attachments/assets/4f04ce48-da1e-466b-947b-882a5d66e807)

### NCP

1. **회의 녹음본 업로드**: 회의가 끝난 후, 녹음본(MP4 파일)이 Object Storage에 업로드됩니다.
2. **STT 수행**: Cloud Function이 트리거되어 CLOVA Speech API를 호출하여 음성인식(STT)을 수행합니다. 결과는 JSON 파일로 반환됩니다.
3. **데이터 저장**: 생성된 JSON 파일은 다시 Object Storage에 저장됩니다.
4. **AWS로 데이터 이동**: 또 다른 Cloud Function이 트리거되어 JSON 파일을 AWS S3로 복사합니다. 이는 NCP에서 NoSQL DB로의 ETL 작업을 지원하지 않아 AWS로 이관하게 되었습니다.

### AWS

1. **S3에 데이터 저장**: NCP에서 전송된 JSON 파일이 S3에 저장됩니다.
2. **Lambda 함수 호출**: S3에 새 파일이 들어오면 Lambda 함수가 트리거됩니다.
3. **Glue ETL 작업**: Lambda 함수가 Glue를 호출하여 ETL 작업을 수행합니다.
4. **DynamoDB에 데이터 저장**: ETL 작업이 완료되면, 변환된 데이터는 DynamoDB에 저장됩니다.
5. **텍스트 파일 생성**: 동시에, 화자와 음성만 추출하여 텍스트 파일을 생성하고 S3에 저장합니다.
6. **Hyper CLOVA X 호출**: 또 다른 Lambda 함수가 트리거되어 Hyper CLOVA X를 호출하여 회의록을 생성합니다.
7. **완성된 회의록 저장**: 생성된 회의록은 S3에 저장됩니다.
8. **SNS 알림**: 회의록 생성이 완료되면 SNS를 통해 사용자에게 알림을 보냅니다.
