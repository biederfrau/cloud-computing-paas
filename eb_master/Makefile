init:
	cp -r ../dynamodb ../pretty.py ../polling_thread.py ../static ../requirements.txt .
	cp ../master.py application.py
	eb init -p python-3.6 eb-master --region us-east-2
	@echo "this will take about 5 minutes now"
	-eb create eb-master-env
	-aws iam attach-role-policy --role-name aws-elasticbeanstalk-ec2-role --policy-arn arn:aws:iam::aws:policy/AmazonSQSFullAccess
	-aws iam attach-role-policy --role-name aws-elasticbeanstalk-ec2-role --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
	@echo "we need to wait a while so the server is actually ready (else you will get a blank page)"
	sleep 60
	eb open

clean:
	rm -r dynamodb pretty.py polling_thread.py static requirements.txt application.py
	-aws iam detach-role-policy --role-name aws-elasticbeanstalk-ec2-role --policy-arn arn:aws:iam::aws:policy/AmazonSQSFullAccess
	-aws iam detach-role-policy --role-name aws-elasticbeanstalk-ec2-role --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
	eb terminate
