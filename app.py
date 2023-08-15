import os
import boto3
import pandas as pd
from flask import Flask, render_template
from sqlalchemy import create_engine
from dotenv import load_dotenv
import logging

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

def get_cloudwatch_client():
    region = 'us-west-1'  # Replace with your desired AWS region
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    
    return boto3.client(
        'cloudwatch',
        region_name=region,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )

def fetch_metric_data(cloudwatch, namespace, metric_name, dimensions, start_time, end_time):
    try:
        response = cloudwatch.get_metric_data(
            MetricDataQueries=[
                {
                    'Id': 'm1',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': namespace,
                            'MetricName': metric_name,
                            'Dimensions': dimensions,
                        },
                        'Period': 3600,
                        'Stat': 'Average',
                    },
                    'ReturnData': True,
                },
            ],
            StartTime=start_time,
            EndTime=end_time,
        )
        return response['MetricDataResults'][0]['Values']
    except Exception as e:
        logging.error(f"Error fetching metric {metric_name}: {e}")
        return []

def store_data_in_postgres(df, table_name):
    try:
        db_url = os.getenv('DB_URL')
        engine = create_engine(db_url)

        chunk_size = 1000  # Adjust the chunk size as needed
        for start in range(0, len(df), chunk_size):
            chunk = df.iloc[start:start + chunk_size]
            chunk.to_sql(table_name, engine, if_exists='append', index=False)
            
        logging.info(f"Data stored in PostgreSQL table: {table_name}")
    except Exception as e:
        logging.error(f"Error storing data in PostgreSQL: {e}")

@app.route('/')
def index():
    cloudwatch = get_cloudwatch_client()

    s3_bucket_name = os.getenv('S3_BUCKET_NAME')
    rds_instance_id = os.getenv('RDS_INSTANCE_ID')
    ec2_instance_id = os.getenv('EC2_INSTANCE_ID')

    # Fetch and process S3 metrics
    s3_metrics_to_monitor = ['BucketSizeBytes', 'NumberOfObjects', 'BytesUploaded', 'BytesDownloaded', 'TotalRequestCount', '4xxErrorRate', '5xxErrorRate']
    s3_data = {}
    for metric_name in s3_metrics_to_monitor:
        s3_data[metric_name] = fetch_metric_data(cloudwatch, 'AWS/S3', metric_name, [{'Name': 'BucketName', 'Value': s3_bucket_name}, {'Name': 'StorageType', 'Value': 'AllStorageTypes'}], '2023-07-01T00:00:00Z', '2023-07-25T00:00:00Z')
    df_s3 = pd.DataFrame(s3_data)
    store_data_in_postgres(df_s3, 's3_metrics')

    # Fetch and process RDS metrics
    rds_metrics_to_monitor = ['CPUUtilization', 'DatabaseConnections', 'FreeableMemory', 'VolumeBytesUsed']
    rds_data = {}
    for metric_name in rds_metrics_to_monitor:
        rds_data[metric_name] = fetch_metric_data(cloudwatch, 'AWS/RDS', metric_name, [{'Name': 'DBInstanceIdentifier', 'Value': rds_instance_id}], '2023-07-01T00:00:00Z', '2023-07-25T00:00:00Z')
    df_rds = pd.DataFrame(rds_data)
    store_data_in_postgres(df_rds, 'rds_metrics')

    # Fetch and process EC2 metrics
    ec2_metrics_to_monitor = [
        {'name': 'CPUUtilization', 'namespace': 'AWS/EC2'},
        {'name': 'MemoryUtilization', 'namespace': 'System/Linux', 'dimensions': [{'Name': 'InstanceId', 'Value': ec2_instance_id}]},
        {'name': 'NetworkIn', 'namespace': 'AWS/EC2', 'dimensions': [{'Name': 'InstanceId', 'Value': ec2_instance_id}]},
        {'name': 'NetworkOut', 'namespace': 'AWS/EC2', 'dimensions': [{'Name': 'InstanceId', 'Value': ec2_instance_id}]},
        {'name': 'DiskSpaceUtilization', 'namespace': 'System/Linux', 'dimensions': [{'Name': 'InstanceId', 'Value': ec2_instance_id}]}
    ]
    ec2_metric_data = {}
    for metric_info in ec2_metrics_to_monitor:
        metric_name = metric_info['name']
        namespace = metric_info['namespace']
        dimensions = metric_info.get('dimensions', [])
        data = fetch_metric_data(cloudwatch, namespace, metric_name, dimensions, '2023-07-01T00:00:00Z', '2023-07-25T00:00:00Z')
        ec2_metric_data[metric_name] = data
    df_ec2 = pd.DataFrame(ec2_metric_data)
    store_data_in_postgres(df_ec2, 'ec2_metrics')

    return render_template('dashboard.html', df_s3=df_s3, df_rds=df_rds, df_ec2=df_ec2)

if __name__ == '__main__':
    app.run(debug=True)
