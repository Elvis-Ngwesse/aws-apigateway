
###############
Create function
###############

* Zip
- zip countries.zip countries_function.py

* Create
- aws lambda create-function \
  --function-name getAllCountries \
  --runtime python3.8 \
  --role arn:aws:iam::908027384199:role/LambdaExecutionRole \
  --handler countries_function.lambda_handler \
  --zip-file fileb://countries.zip \
  --layers arn:aws:lambda:eu-west-2:908027384199:layer:my-layer:1 \
  --region eu-west-2 \
  --memory-size 512 \
  --timeout 30 \
  --tracing-config Mode=Active

* Update function
- aws lambda update-function-configuration \
  --function-name getAllCountries \
  --runtime python3.9 \
  --role arn:aws:iam::908027384199:role/LambdaExecutionRole \
  --handler countries_function.lambda_handler \
  --layers arn:aws:lambda:eu-west-2:908027384199:layer:my-layer:1 \
  --memory-size 512 \
  --timeout 30 \
  --tracing-config Mode=Active \
  --region eu-west-2


* Update code
- aws lambda update-function-code \
  --function-name getAllCountries \
  --zip-file fileb://countries.zip \
  --region eu-west-2



- aws lambda get-function --function-name getAllCountries --region eu-west-2

- aws lambda invoke \
  --function-name getAllCountries \
  --region eu-west-2 \
  --payload '{}' \
  --cli-binary-format raw-in-base64-out \
  /dev/stdout

##################
Create api-gateway
##################
- aws apigatewayv2 create-api \
  --name "Countries-API" \
  --protocol-type "HTTP" \
  --description "API for retrieving country data" \
  --cors-configuration '{"AllowOrigins":["*"], "AllowMethods":["GET", "POST", "OPTIONS"]}'

- get api_id
    aws apigatewayv2 get-apis

- delete api
    aws apigatewayv2 delete-api --api-id $api_id

##################
Create integration
##################
- aws apigatewayv2 create-integration \
  --api-id ldh6i51ca5 \
  --integration-type AWS_PROXY \
  --integration-method POST \
  --integration-uri arn:aws:lambda:eu-west-2:908027384199:function:getAllCountries \
  --payload-format-version 2.0

Delete intergration
- aws apigatewayv2 delete-integration \
  --api-id ldh6i51ca5 \
  --integration-id jxv6z40

############
Create route
############
- aws apigatewayv2 create-route \
  --api-id ldh6i51ca5 \
  --route-key "GET /allcountries" \
  --target "integrations/f33dg5n"  

Get route
- aws apigatewayv2 get-route \
  --api-id ldh6i51ca5 \
  --route-id cu14w69

###########################
Permission to Invoke Lambda
###########################
- Go to API-Gateway
  go to intergration
  look for => Example policy statement
  copy and run permission command

##############
Deploy the API
##############
- aws logs create-log-group --log-group-name /aws/api-gateway/access-logs

- aws apigatewayv2 create-stage \
  --api-id ldh6i51ca5 \
  --stage-name Test \
  --description "Test stage for API deployment" \
  --stage-variables environment=prod,lambdaTimeout=30 \
  --access-log-settings '{"DestinationArn": "arn:aws:logs:eu-west-2:908027384199:log-group:/aws/api-gateway/access-logs", "Format": "$context.requestId"}' \
  --tags Key=Environment,Value=Test

- aws apigatewayv2 create-deployment \
  --api-id ldh6i51ca5 \
  --stage-name Test \
  --description "Initial deployment to Test stage"

########
Curl API
########
curl https://ldh6i51ca5.execute-api.eu-west-2.amazonaws.com/Test/allcountries
