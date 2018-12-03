#!/bin/bash


rm ./worker.zip
mkdir ./worker_package
cd worker_package
pip install Pillow --target .
zip -r9 ../worker.zip .
cd ..
zip -g worker.zip lambda_worker.py
rm -r ./worker_package
