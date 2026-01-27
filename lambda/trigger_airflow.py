import boto3
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # 1. Parse S3 Event (Note: Format varies if coming from EventBridge vs S3 Direct)
    try:
        s3_record = event['Records'][0]['s3']
        bucket_name = s3_record['bucket']['name']
        file_key = s3_record['object']['key']
    except KeyError:
        # Fallback for EventBridge format
        bucket_name = event['detail']['bucket']['name']
        file_key = event['detail']['object']['key']

    logger.info(f"File {file_key} detected in {bucket_name}")

    # 2. Authenticate with MWAA (Managed Airflow)
    mwaa_env_name = 'Your-MWAA-Environment-Name'
    client = boto3.client('mwaa')
    
    # Create a CLI token to talk to Airflow
    token = client.create_cli_token(Name=mwaa_env_name)
    
    # 3. Trigger the DAG via REST API (Experimental endpoint for dags trigger)
    import http.client
    import base64

    url = f"{token['WebServerHostname']}"
    # Constructing the CLI command to trigger
    # command: dags trigger <dag_id> --conf '{"key": "val"}'
    conf_json = json.dumps({"bucket": bucket_name, "key": file_key})
    mwaa_command = f"dags trigger tax_doc_ingestion_dag --conf '{conf_json}'"
    
    # Making the actual request
    conn = http.client.HTTPSConnection(url)
    headers = {
        'Authorization': f"Bearer {token['CliToken']}",
        'Content-Type': 'text/plain'
    }
    conn.request("POST", "/aws_mwaa/cli", mwaa_command, headers)
    res = conn.getresponse()
    
    return {
        'statusCode': 200,
        'body': json.dumps(f"Triggered Airflow for {file_key}")
    }