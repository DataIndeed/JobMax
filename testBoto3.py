import boto3
s3_resource = boto3.resource('s3')
s3_client = boto3.client('s3')
s3_client.upload_file(Filename="wordcloudl.jpg", Bucket="jobmaxresults", Key="testboto3up")