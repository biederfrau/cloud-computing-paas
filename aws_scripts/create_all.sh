#!/bin/bash


./create_queues.sh
./create_tables.sh
./create_lambda.sh
./attach_policies.sh
