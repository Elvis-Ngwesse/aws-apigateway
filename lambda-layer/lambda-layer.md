mkdir -p lambda-layer/python
pip install requests -t lambda-layer/python
cd lambda-layer
zip -r layer.zip python

###################
Create Lambda Layer
###################
- aws lambda publish-layer-version \
  --layer-name my-layer \
  --description "My Lambda Layer with dependencies" \
  --zip-file fileb://layer.zip \
  --compatible-runtimes python3.8 python3.9 python3.10

- aws lambda list-layers --region eu-west-2

- aws lambda get-function-configuration --function-name myLambdaFunction

