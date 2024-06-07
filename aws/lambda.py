import boto3
import json
import os
import logging
from urllib.parse import unquote_plus

# 로거 설정
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    glue_client = boto3.client('glue')
    
    # 이벤트 정보 로그 기록
    logger.info(f"Event: {json.dumps(event)}")
    
    # S3 버킷 이름과 파일 키 추출
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_key = event['Records'][0]['s3']['object']['key']
    
    # 파일 키 URL 디코딩
    decoded_file_key = unquote_plus(file_key)
    
    # 파일 키 로그 기록
    logger.info(f"Bucket: {bucket_name}, File key: {decoded_file_key}")
    
    s3_client = boto3.client('s3')
    
    # S3 객체 접근 권한 확인
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=decoded_file_key)
        logger.info(f"Successfully accessed S3 object: {bucket_name}/{decoded_file_key}")
    except s3_client.exceptions.NoSuchKey as e:
        logger.error(f"Error accessing S3 object: {str(e)} - NoSuchKey")
        raise
    except Exception as e:
        logger.error(f"Error accessing S3 object: {str(e)}")
        raise
    
    # Glue 작업 시작
    try:
        response = glue_client.start_job_run(
            JobName='S3toDDB',  # Glue Job 이름으로 변경
            Arguments={
                '--S3_BUCKET': bucket_name,
                '--S3_KEY': decoded_file_key
            }
        )
        logger.info(f"Started Glue job: {response}")
    except Exception as e:
        logger.error(f"Error starting Glue job: {str(e)}")
        raise
    
    result = {
        'statusCode': 200,
        'body': json.dumps('Glue job started successfully')
    }
    logger.info(f"Return Value: {result}")
    
    return result
