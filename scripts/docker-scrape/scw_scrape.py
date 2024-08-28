import requests
import json
from scaleway import Client
import os
import logging
import logging_loki
import boto3
import os

#Scaleway regions
SCALEWAY_REGION = 'fr-par'  # or your preferred region
SCALEWAY_BUCKET_NAME = 'bdo-market-ids'

#Scaleway secrets
SCALEWAY_ACCESS_KEY = os.environ['SCALEWAY_ACCESS_KEY']
SCALEWAY_SECRET_KEY = os.environ['SCALEWAY_SECRET_KEY']
COCKPIT_TOKEN_SECRET_KEY = os.environ['COCKPIT_TOKEN_SECRET_KEY']

#SCALEWAY_COCKPIT_ENDPOINT = 'https://api.scaleway.com/cockpit/v1beta1'

#Loki logging handler
handler = logging_loki.LokiHandler(
    url="https://logs.cockpit.fr-par.scw.cloud/loki/api/v1/push",
    tags={"job": "market-id-scraper"},
    auth=(SCALEWAY_SECRET_KEY, COCKPIT_TOKEN_SECRET_KEY),
    version="1",
)

logger = logging.getLogger("market-id-scraper")
print("Logger initialized.")
logger.addHandler(handler)
print("Logger handler added.")
logger.setLevel(logging.INFO)
print("Logger level set.")

s3_client = boto3.client('s3',
    region_name=SCALEWAY_REGION,
    endpoint_url=f'https://s3.{SCALEWAY_REGION}.scw.cloud',
    aws_access_key_id=SCALEWAY_ACCESS_KEY,
    aws_secret_access_key=SCALEWAY_SECRET_KEY
)
def fetch_and_save_data(region):
    api_url = f"https://api.arsha.io/v2/{region}/pearlItems"
    try:
        response = requests.get(api_url)
        print("Response code " + str(response.status_code))
        if response.status_code == 200:
            print("Inside the try")
            print
            data = response.json()
            excluded_ids = [18946, 290006]
            cleaned_data = [
                {
                    "id": item["id"], "name": item["name"]
                } 
                for item in data 
                if ("set" in item["name"].lower() or "box" in item["name"].lower()) 
                and "horse" not in item["name"].lower() 
                and "shai" not in item["name"].lower()
                and "donkey" not in item["name"].lower()
                and item["id"] not in excluded_ids
            ]
            print(f"Initializing Scaleway Object Storage client")
            #Initialize Scaleway Object Storage client
            client = Client(
                access_key=SCALEWAY_ACCESS_KEY,
                secret_key=SCALEWAY_SECRET_KEY
                #region=SCALEWAY_REGION
            )

            json_data = json.dumps(cleaned_data, indent=4)
            print(f"Writing data to Scaleway Object Storage.")
            #client.bucket(SCALEWAY_BUCKET_NAME).object('cleaned_data.json').write(json_data)
            s3_client.put_object(
                Bucket=SCALEWAY_BUCKET_NAME,
                Key='cleaned_data.json',
                Body=json_data
            )
            print("Data successfully saved to Scaleway Object Storage.")
            logger.info("Data successfully saved to Scaleway Object Storage.")
        else:
            print(f"Failed to fetch data from the API. Status Code: {response.status_code}")
            logger.error(f"Failed to fetch data from the API. Status Code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        logger.error(f"An error occurred: {str(e)}")

fetch_and_save_data("eu")
