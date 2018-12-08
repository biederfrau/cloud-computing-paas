aws sqs delete-queue --queue-url https://queue.amazonaws.com/$(aws sts get-caller-identity --output text --query 'Account')/queue-master
aws sqs delete-queue --queue-url https://queue.amazonaws.com/$(aws sts get-caller-identity --output text --query 'Account')/queue-in
