USER=$(aws iam get-user --output text --query User.UserName)

aws iam detach-policy --user-name $USER --policy-arn arn:aws:iam::aws:policy/AWSLambdaFullAccess
aws iam detach-policy --user-name $USER --policy-arn arn:aws:iam::aws:policy/AutoScalingFullAccess
aws iam detach-policy --user-name $USER --policy-arn arn:aws:iam::aws:policy/ElasticLoadBalancingFullAccess
aws iam detach-policy --user-name $USER --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
aws iam detach-policy --user-name $USER --policy-arn arn:aws:iam::aws:policy/CloudWatchFullAccess
aws iam detach-policy --user-name $USER --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
aws iam detach-policy --user-name $USER --policy-arn arn:aws:iam::aws:policy/AWSElasticBeanstalkFullAccess
aws iam detach-policy --user-name $USER --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole #???
aws iam detach-policy --user-name $USER --policy-arn arn:aws:iam::aws:policy/AmazonEC2FullAccess
aws iam detach-policy --user-name $USER --policy-arn arn:aws:iam::aws:policy/AmazonSQSFullAccess
