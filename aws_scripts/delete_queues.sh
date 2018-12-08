#!/bin/bash


ACCOUNT_ID=`aws sts get-caller-identity --output text --query 'Account'`

aws sqs delete-queue --queue-url https://queue.amazonaws.com/$ACCOUNT_ID/queue-master
aws sqs delete-queue --queue-url https://queue.amazonaws.com/$ACCOUNT_ID/queue-in
