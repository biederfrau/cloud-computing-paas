REGION:=$(shell aws configure get region)

init:
	cp -r ../dynamodb ../pretty.py ../polling_thread.py ../static ../requirements.txt .
	cp ../master.py application.py
	sed -i -e "s/AWS_DEFAULT_REGION: .*/AWS_DEFAULT_REGION: '$(REGION)'/g" .ebextensions/01_envar.config
	eb init -p python-3.6 eb-master --region '$(REGION)'
	@echo "[MAKE] this will take about 5 minutes now"
	-eb create eb-master-env
	-aws iam attach-role-policy --role-name aws-elasticbeanstalk-ec2-role --policy-arn arn:aws:iam::aws:policy/AmazonSQSFullAccess
	-aws iam attach-role-policy --role-name aws-elasticbeanstalk-ec2-role --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
	@echo "[MAKE] we need to wait a while so the server is actually ready (else you will get a blank page)"
	sleep 60
	eb open

clean:
	rm -r dynamodb pretty.py polling_thread.py static requirements.txt application.py
	-aws iam detach-role-policy --role-name aws-elasticbeanstalk-ec2-role --policy-arn arn:aws:iam::aws:policy/AmazonSQSFullAccess
	-aws iam detach-role-policy --role-name aws-elasticbeanstalk-ec2-role --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
	eb terminate
