#!/bin/bash


./make_lambda.sh

aws lambda update-function-code --function-name QueueInConsumer --zip-file fileb://worker.zip
