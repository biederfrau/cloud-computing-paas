#!/bin/bash


ACCOUNT_ID=`aws sts get-caller-identity --output text --query 'Account'`
REGION=`aws configure get region`


# Lambda
MAPPING_UUID=`aws lambda list-event-source-mappings --output text --query "EventSourceMappings[?EventSourceArn=='arn:aws:sqs:$REGION:$ACCOUNT_ID:queue-in' && FunctionArn=='arn:aws:lambda:$REGION:$ACCOUNT_ID:function:QueueInConsumer'].UUID"`
aws lambda delete-event-source-mapping --uuid $MAPPING_UUID

aws lambda delete-function --function-name QueueInConsumer


# Queues
aws sqs delete-queue --queue-url https://queue.amazonaws.com/$ACCOUNT_ID/queue-master
aws sqs delete-queue --queue-url https://queue.amazonaws.com/$ACCOUNT_ID/queue-out
aws sqs delete-queue --queue-url https://queue.amazonaws.com/$ACCOUNT_ID/queue-in


# Roles
aws iam detach-role-policy --role-name lambda-worker-role \
                           --policy-arn arn:aws:iam::$ACCOUNT_ID:policy/service-role/AWSLambdaBasicExecutionRole-40c6177f-37ee-4319-8d26-f59e614ea503

aws iam detach-role-policy --role-name lambda-worker-role \
                           --policy-arn arn:aws:iam::aws:policy/AmazonSQSFullAccess

aws iam delete-role --role-name lambda-worker-role


