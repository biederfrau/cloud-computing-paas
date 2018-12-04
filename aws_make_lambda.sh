#!/bin/bash


rm ./worker.zip
mkdir ./worker_package
cd worker_package
pip install -r ../lambda_requirements.txt --target .
zip -r9 ../worker.zip .
cd ..
zip -g worker.zip lambda_worker.py
zip -g worker.zip pretty.py
rm -r ./worker_package
