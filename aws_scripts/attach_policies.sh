USER=$(aws iam get-user --output text --query User.UserName)

aws iam attach-policy --user-name $USER --policy-arn arn:aws:iam::aws:policy/AWSLambdaFullAccess
aws iam attach-policy --user-name $USER --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole #???

# EB
aws iam attach-policy --user-name $USER --policy-arn arn:aws:iam::aws:policy/AutoScalingFullAccess
aws iam attach-policy --user-name $USER --policy-arn arn:aws:iam::aws:policy/ElasticLoadBalancingFullAccess
aws iam attach-policy --user-name $USER --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
aws iam attach-policy --user-name $USER --policy-arn arn:aws:iam::aws:policy/CloudWatchFullAccess
aws iam attach-policy --user-name $USER --policy-arn arn:aws:iam::aws:policy/AWSElasticBeanstalkFullAccess
# /EB

aws iam attach-policy --user-name $USER --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
aws iam attach-policy --user-name $USER --policy-arn arn:aws:iam::aws:policy/AmazonEC2FullAccess
aws iam attach-policy --user-name $USER --policy-arn arn:aws:iam::aws:policy/AmazonSQSFullAccess
