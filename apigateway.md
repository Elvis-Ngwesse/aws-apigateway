

Create a Resource (e.g., /hello)
RESOURCE_ID=$(aws apigateway create-resource --rest-api-id $API_ID --parent-id $ROOT_RESOURCE_ID --path-part "hello" --query "id" --output text)

Create a Lambda Function
If you don’t have a Lambda function, create one first.

aws lambda create-function --function-name "MyLambdaFunction" \
    --runtime python3.8 \
    --role "arn:aws:iam::ACCOUNT_ID:role/execution_role" \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://function.zip

Set up API Gateway → Lambda Integration
aws apigateway put-method \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method POST \
    --authorization-type "NONE"

aws apigateway put-integration \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method POST \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri arn:aws:apigateway:REGION:lambda:path/2015-03-31/functions/arn:aws:lambda:REGION:ACCOUNT_ID:function:MyLambdaFunction/invocations

Grant API Gateway Permissions to Invoke Lambda
aws lambda add-permission \
    --function-name "MyLambdaFunction" \
    --statement-id apigateway-test-1 \
    --action "lambda:InvokeFunction" \
    --principal "apigateway.amazonaws.com" \
    --source-arn "arn:aws:execute-api:REGION:ACCOUNT_ID:$API_ID/*/POST/hello"

Deploy to a Stage (e.g., dev)

aws apigateway create-deployment \
    --rest-api-id $API_ID \
    --stage-name dev

Create a New Stage (e.g., prod)
aws apigateway create-stage \
    --rest-api-id $API_ID \
    --stage-name prod \
    --deployment-id $(aws apigateway get-deployments --rest-api-id $API_ID --query "items[0].id" --output text)

Enable CORS (Optional)
aws apigateway put-method-response \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method OPTIONS \
    --status-code 200 \
    --response-parameters '{"method.response.header.Access-Control-Allow-Origin": true}'

aws apigateway put-integration-response \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method OPTIONS \
    --status-code 200 \
    --response-parameters '{"method.response.header.Access-Control-Allow-Origin": "'*'"}'


Create an API Gateway Integration Layer (Lambda Authorizer)
If you want to use a Lambda Authorizer:

AUTHORIZER_ID=$(aws apigateway create-authorizer \
    --rest-api-id $API_ID \
    --name "MyAuthorizer" \
    --type TOKEN \
    --identity-source "method.request.header.Authorization" \
    --authorizer-uri "arn:aws:apigateway:REGION:lambda:path/2015-03-31/functions/arn:aws:lambda:REGION:ACCOUNT_ID:function:MyLambdaAuthFunction/invocations" \
    --query "id" --output text)

aws lambda add-permission \
    --function-name "MyLambdaAuthFunction" \
    --statement-id auth-permission \
    --action "lambda:InvokeFunction" \
    --principal "apigateway.amazonaws.com" \
    --source-arn "arn:aws:execute-api:REGION:ACCOUNT_ID:$API_ID/authorizers/$AUTHORIZER_ID"

Enable Logging in API Gateway

aws apigateway update-stage \
    --rest-api-id $API_ID \
    --stage-name dev \
    --patch-operations op=replace,path=/accessLogSettings/destinationArn,value="arn:aws:logs:REGION:ACCOUNT_ID:log-group:/aws/apigateway/MyAPILogs"


Enable API Key Authentication
sh
Copy
Edit
API_KEY_ID=$(aws apigateway create-api-key --name "MyApiKey" --enabled --query "id" --output text)

aws apigateway create-usage-plan --name "MyUsagePlan" \
    --throttle rateLimit=10,burstLimit=2 \
    --quota limit=1000,period=MONTH \
    --api-stages apiId=$API_ID,stage=dev \
    --query "id" --output text

aws apigateway create-usage-plan-key \
    --usage-plan-id $API_KEY_ID \
    --key-id $API_KEY_ID \
    --key-type "API_KEY"


Set a Custom Domain for API Gateway
aws apigateway create-domain-name \
    --domain-name "api.example.com" \
    --certificate-arn "arn:aws:acm:REGION:ACCOUNT_ID:certificate/CERTIFICATE_ID"

aws apigateway create-base-path-mapping \
    --domain-name "api.example.com" \
    --rest-api-id $API_ID \
    --stage "dev"



14. Set Throttling and Rate Limits
aws apigateway update-stage \
    --rest-api-id $API_ID \
    --stage-name dev \
    --patch-operations op=replace,path=/throttling/rateLimit,value=100

aws apigateway update-stage \
    --rest-api-id $API_ID \
    --stage-name dev \
    --patch-operations op=replace,path=/throttling/burstLimit,value=50
✅ Limits requests to 100 requests per second with a burst limit of 50.

15. Enable Caching for API Responses

aws apigateway update-stage \
    --rest-api-id $API_ID \
    --stage-name dev \
    --patch-operations op=replace,path=/cacheClusterEnabled,value=true

aws apigateway update-stage \
    --rest-api-id $API_ID \
    --stage-name dev \
    --patch-operations op=replace,path=/cacheClusterSize,value=0.5
✅ Enables caching with 512MB for faster API responses.

16. Enable AWS WAF Protection

aws waf create-web-acl --name "MyAPIGatewayWAF" \
    --scope REGIONAL \
    --default-action Allow={} \
    --rules file://waf-rules.json \
    --visibility-config SampledRequestsEnabled=true,CloudWatchMetricsEnabled=true,MetricName="APIGatewayWAF"

aws wafv2 associate-web-acl \
    --web-acl-arn arn:aws:wafv2:REGION:ACCOUNT_ID:regional/webacl/MyAPIGatewayWAF/WEBACL_ID \
    --resource-arn arn:aws:apigateway:REGION::/restapis/$API_ID/stages/dev
✅ Protects API Gateway from malicious attacks, rate-limiting, and IP filtering.

17. Enable Request Validation

aws apigateway create-request-validator \
    --rest-api-id $API_ID \
    --name "ValidateRequestBodyAndParams" \
    --validate-request-body \
    --validate-request-parameters
✅ Ensures incoming requests contain valid parameters and request body.

18. Set Up Response Transformations

aws apigateway put-method-response \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method GET \
    --status-code 200 \
    --response-models '{"application/json": "Empty"}'

aws apigateway put-integration-response \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method GET \
    --status-code 200 \
    --response-templates '{"application/json": "{\"message\": \"Custom Response\", \"data\": $input.json(\"$.body\")}"}'
✅ Modifies API responses dynamically.

19. Enable Canary Deployments for Testing

aws apigateway update-stage \
    --rest-api-id $API_ID \
    --stage-name dev \
    --patch-operations op=replace,path=/canarySettings/percentTraffic,value=10
✅ Sends 10% of traffic to a new API version for testing.

20. Create WebSocket API Gateway

WEB_SOCKET_API_ID=$(aws apigatewayv2 create-api \
    --name "MyWebSocketAPI" \
    --protocol-type WEBSOCKET \
    --route-selection-expression "$request.body.action" \
    --query "ApiId" --output text)

aws apigatewayv2 create-route \
    --api-id $WEB_SOCKET_API_ID \
    --route-key "sendMessage" \
    --target "integrations/MyLambdaFunction"
✅ Sets up a WebSocket API for real-time messaging.

21. Enable Usage Plans and API Key Restrictions

aws apigateway create-usage-plan \
    --name "BasicPlan" \
    --description "Limited access plan" \
    --api-stages apiId=$API_ID,stage=dev \
    --throttle rateLimit=10,burstLimit=5 \
    --quota limit=1000,period=MONTH
✅ Restricts API access per user with API keys.

22. Enable Custom Domain Name for WebSocket API

aws apigatewayv2 create-domain-name \
    --domain-name "ws.example.com" \
    --domain-name-configurations CertificateArn="arn:aws:acm:REGION:ACCOUNT_ID:certificate/CERTIFICATE_ID"
✅ Maps WebSocket API to a custom domain.

23. Enable Mutual TLS Authentication

aws apigateway create-domain-name \
    --domain-name "api.example.com" \
    --regional-certificate-arn "arn:aws:acm:REGION:ACCOUNT_ID:certificate/CERTIFICATE_ID" \
    --mutual-tls-authentication truststoreUri="s3://my-truststore-bucket/truststore.p12"
✅ Uses Mutual TLS (mTLS) for enhanced security.

24. Create a Custom Gateway Response for Unauthorized Access

aws apigateway put-gateway-response \
    --rest-api-id $API_ID \
    --response-type UNAUTHORIZED \
    --status-code 401 \
    --response-templates '{"application/json": "{\"error\": \"You are not authorized to access this API\"}"}'
✅ Returns custom error messages for unauthorized requests.

25. Enable Request and Response Logging

aws apigateway update-stage \
    --rest-api-id $API_ID \
    --stage-name dev \
    --patch-operations op=replace,path=/accessLogSettings/format,value='{"requestId":"$context.requestId","ip":"$context.identity.sourceIp","requestTime":"$context.requestTime"}'
✅ Logs request details to CloudWatch.

26. Enable CloudFront Distribution for API Gateway

aws cloudfront create-distribution \
    --origin-domain-name "$API_ID.execute-api.REGION.amazonaws.com" \
    --default-root-object index.html \
    --viewer-protocol-policy redirect-to-https
✅ Accelerates API performance using CloudFront caching.

27. Enable JWT Authentication using Cognito

aws apigateway create-authorizer \
    --rest-api-id $API_ID \
    --name "CognitoAuthorizer" \
    --type COGNITO_USER_POOLS \
    --identity-source "method.request.header.Authorization" \
    --provider-arns "arn:aws:cognito-idp:REGION:ACCOUNT_ID:userpool/USER_POOL_ID"
✅ Requires users to authenticate with Cognito JWT tokens.

28. Enable Request Transformation using Mapping Templates

aws apigateway put-integration-request \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method POST \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri arn:aws:apigateway:REGION:lambda:path/2015-03-31/functions/arn:aws:lambda:REGION:ACCOUNT_ID:function:MyLambdaFunction/invocations \
    --request-templates '{
        "application/json": "{ \"body\": $input.json(\"$.data\") }"
    }'