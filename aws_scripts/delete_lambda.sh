#!/bin/bash


ACCOUNT_ID=`aws sts get-caller-identity --output text --query 'Account'`
REGION=`aws configure get region`


# Lambda
MAPPING_UUID=`aws lambda list-event-source-mappings --output text --query "EventSourceMappings[?EventSourceArn=='arn:aws:sqs:$REGION:$ACCOUNT_ID:queue-in' && FunctionArn=='arn:aws:lambda:$REGION:$ACCOUNT_ID:function:QueueInConsumer'].UUID"`
echo $MAPPING_UUID
aws lambda delete-event-source-mapping --uuid $MAPPING_UUID

aws lambda delete-function --function-name QueueInConsumer

aws iam detach-role-policy --role-name lambda-worker-role \
                           --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess

aws iam detach-role-policy --role-name lambda-worker-role \
                           --policy-arn arn:aws:iam::aws:policy/AWSLambdaBasicExecutionRole

aws iam detach-role-policy --role-name lambda-worker-role \
                           --policy-arn arn:aws:iam::aws:policy/AmazonSQSFullAccess

aws iam delete-role --role-name lambda-worker-role
