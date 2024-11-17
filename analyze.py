import os
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv()

# Retrieve credentials from environment
endpoint = os.getenv("endpoint")
key = os.getenv("key")

# Ensure both values are available
if not endpoint or not key:
    raise ValueError("Endpoint and key must be set in .env file")

# Create client with credentials
credentials = CognitiveServicesCredentials(key)
client = ComputerVisionClient(endpoint=endpoint, credentials=credentials)

def read_image(uri):
    numberOfCharsInOperationId = 36
    maxRetries = 10

    try:
        # SDK call to initiate the read (OCR) process
        rawHttpResponse = client.read(uri, language="en", raw=True)

        # Extract operation ID from response headers
        operationLocation = rawHttpResponse.headers["Operation-Location"]
        operationId = operationLocation[-numberOfCharsInOperationId:]

        # Poll the API for the read result
        retry = 0
        result = client.get_read_result(operationId)
        while retry < maxRetries and result.status.lower() in ['notstarted', 'running']:
            time.sleep(1)
            result = client.get_read_result(operationId)
            retry += 1

        if retry == maxRetries:
            return "Max retries reached"

        # Process result if successful
        if result.status == OperationStatusCodes.succeeded:
            res_text = " ".join([line.text for line in result.analyze_result.read_results[0].lines])
            return res_text
        else:
            return f"Error: OCR failed with status {result.status}"
    
    except Exception as e:
        # Log the exception to get more details on what went wrong
        print(f"Error processing image: {str(e)}")
        return f"Error: {str(e)}"
