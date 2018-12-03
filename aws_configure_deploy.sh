#!/bin/bash

ACCOUNT_ID=`aws sts get-caller-identity --output text --query 'Account'`
REGION=`aws configure get region`


# Roles
aws iam create-role --role-name lambda-worker-role \
                    --assume-role-policy-document file://lambdaAssumeRolePolicyDocument.json

aws iam attach-role-policy --role-name lambda-worker-role \
                           --policy-arn arn:aws:iam::$ACCOUNT_ID:policy/service-role/AWSLambdaBasicExecutionRole-40c6177f-37ee-4319-8d26-f59e614ea503

aws iam attach-role-policy --role-name lambda-worker-role \
                           --policy-arn arn:aws:iam::aws:policy/AmazonSQSFullAccess


# Queues
aws sqs create-queue --queue-name queue-in
aws sqs create-queue --queue-name queue-out
aws sqs create-queue --queue-name queue-master


# Lambda
./aws_make_lambda.sh

aws lambda create-function --function-name QueueInConsumer \
                           --runtime python3.7 \
                           --handler lambda_worker.consume_queue_in \
                           --zip-file fileb://worker.zip \
                           --role arn:aws:iam::$ACCOUNT_ID:role/lambda-worker-role \
                           --timeout 30

aws lambda create-event-source-mapping --function-name QueueInConsumer \
                                       --event-source-arn arn:aws:sqs:$REGION:$ACCOUNT_ID:queue-in \
                                       --batch-size 10
