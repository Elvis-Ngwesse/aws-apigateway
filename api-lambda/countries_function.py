import json
import urllib3
import signal

http = urllib3.PoolManager()

# Custom timeout handler
def timeout_handler(signum, frame):
    raise TimeoutError("Lambda function timed out")

def lambda_handler(event, context):
    # Get stage variables
    stage_variables = event.get("stageVariables", {})
    lambda_timeout = int(stage_variables.get("lambdaTimeout", 30))  # Default 30 seconds

    # Set a timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(lambda_timeout)  # Raise a timeout if execution exceeds this limit

    try:
        url = "https://restcountries.com/v3.1/all"
        response = http.request("GET", url)

        if response.status == 200:
            countries = json.loads(response.data.decode("utf-8"))
            country_names = [country["name"]["common"] for country in countries]
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "lambdaTimeout": lambda_timeout,
                    "countries": country_names
                })
            }
        else:
            return {
                "statusCode": response.status,
                "body": json.dumps({"error": "Failed to fetch countries"})
            }
    except TimeoutError:
        return {
            "statusCode": 504,
            "body": json.dumps({"error": "Function execution timed out"})
        }
    finally:
        signal.alarm(0)  # Disable the timeout alarm
