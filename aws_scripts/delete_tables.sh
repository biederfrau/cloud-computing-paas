#!/bin/bash


aws dynamodb delete-table --table-name visited_urls
aws dynamodb delete-table --table-name edges
