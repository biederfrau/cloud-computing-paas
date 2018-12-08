#!/bin/bash


aws dynamodb create-table --table-name visited_urls \
        --attribute-definitions AttributeName=url,AttributeType=S \
        --key-schema AttributeName=url,KeyType=HASH \
        --provisioned-throughput ReadCapacityUnits=25,WriteCapacityUnits=25

aws dynamodb create-table --table-name edges \
        --attribute-definitions AttributeName=source_sink,AttributeType=S \
        --key-schema AttributeName=source_sink,KeyType=HASH \
        --provisioned-throughput ReadCapacityUnits=25,WriteCapacityUnits=25
