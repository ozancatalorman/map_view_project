import os
import ast
import sys
import boto3



def get_monday_api_key():
    # If platform is linux then running remotely so use AWS Secrets Manager
    if sys.platform == 'linux':
        session = boto3.session.Session()
        client_params = {'service_name': 'secretsmanager', 'region_name': 'us-east-2'}
        client = session.client(**client_params)
        response = client.get_secret_value(SecretId='prod/monday/api-key')
        response_dict = ast.literal_eval(response['SecretString'])
        monday_api_key = response_dict['monday-api-key']

    # Otherwise, running locally so use keyring for credentials
    else:
        monday_api_key = os.getenv('MONDAY_API_KEY')

    # Return key
    return monday_api_key