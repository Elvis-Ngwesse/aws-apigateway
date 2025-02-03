
##########
Create API
##########
- aws apigateway create-rest-api --name "Flask-API" --description "Python application for API Gateway"

#######
Get API
#######
- aws apigateway get-rest-apis
- aws apigateway get-rest-apis --query "items[*].{name:name, id:id}" --output table

