import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import col, explode, first, concat_ws
import boto3

# 인수 읽기
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'S3_BUCKET', 'S3_KEY'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# S3에서 데이터 읽기
s3_path = f"s3://{args['S3_BUCKET']}/{args['S3_KEY']}"
datasource0 = glueContext.create_dynamic_frame.from_options(
    connection_type="s3",
    connection_options={"paths": [s3_path]},
    format="json"
)

# 필요한 정보 추출
extracted_data = datasource0.select_fields(['segments', 'token'])

# DynamicFrame을 DataFrame으로 변환
df = extracted_data.toDF()

# 토큰명을 파일 이름으로 사용하기 위해 토큰명을 추출
token_value = df.select(first('token')).collect()[0][0]

# segment 배열을 개별 레코드로 분리하고 필요한 정보 추출
exploded_df = df.withColumn("segment", explode("segments")).select(
    col('token').alias('meeting_id'),
    col('segment.start').cast("string").alias('time'),
    col('segment.textEdited').alias('content'),
    col('segment.speaker.name').alias('name')
)

# DataFrame을 다시 DynamicFrame으로 변환하여 DynamoDB에 저장
extracted_segments = DynamicFrame.fromDF(exploded_df, glueContext, "extracted_segments")

glueContext.write_dynamic_frame.from_options(
    frame=extracted_segments,
    connection_type="dynamodb",
    connection_options={"dynamodb.output.tableName": "semicolon-voice-log"},
    transformation_ctx="datasink4"
)

# 필요한 형식으로 문자열 결합
text_df = exploded_df.withColumn("line", concat_ws(" : ", col("name"), col("content"))).select("line")

# 모든 행을 하나의 텍스트 파일로 저장
lines = text_df.select("line").rdd.map(lambda row: row.line).collect()
output_text = "\n".join(lines)
text_output_path = f"s3://meeton-meeting-log/{token_value}.txt"

# S3에 텍스트 파일로 저장
s3_client = boto3.client('s3')
s3_client.put_object(Bucket="meeton-meeting-log", Key=f"{token_value}.txt", Body=output_text)

job.commit()
