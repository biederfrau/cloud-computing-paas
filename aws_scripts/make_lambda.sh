#!/bin/bash


rm -f ./worker.zip
mkdir ./worker_package
cd worker_package
pip install -r ../../lambda_requirements.txt --target .
zip -r9 ../worker.zip .
cd ..
rm -r ./worker_package
cd ..
zip -g ./aws_scripts/worker.zip lambda_worker.py
zip -g ./aws_scripts/worker.zip pretty.py
zip -g ./aws_scripts/worker.zip ./dynamodb/*
cd aws_scripts