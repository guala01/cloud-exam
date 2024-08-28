"""
When Items are registered in the Black Desert Online marketplace and are of 10b silver or more value they are placed in a waiting list. 

This scrippt will scrape the waiting list and return the items that are currently in the waiting list.

The `fetch_and_parse_market_data()` function retrieves the market waiting list data from the game's API, parses the response, and returns a list of dictionaries containing the item details.

The `save_to_json()` function takes the parsed market data and saves it to a JSON file named "market_data.json".

The `main()` function calls `fetch_and_parse_market_data()` and then saves the resulting data to a JSON file using `save_to_json()`.
"""

import requests
import datetime
import json
import logging
import logging_loki
import boto3
import os
from kafka import KafkaProducer
#logging.basicConfig(filename='wlist.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
#Scaleway configuration
SCALEWAY_REGION = 'fr-par'
SCALEWAY_BUCKET_NAME = 'bdo-market-ids'
SCALEWAY_ACCESS_KEY = os.environ['SCALEWAY_ACCESS_KEY']
SCALEWAY_SECRET_KEY = os.environ['SCALEWAY_SECRET_KEY']
COCKPIT_TOKEN_SECRET_KEY = os.environ['COCKPIT_TOKEN_SECRET_KEY']
#Kafka configuration
KAFKA_BROKER = os.environ['KAFKA_BROKER']
KAFKA_TOPIC = 'waitinglist-updates'
producer = KafkaProducer(bootstrap_servers=[KAFKA_BROKER])

handler = logging_loki.LokiHandler(
    url="https://logs.cockpit.fr-par.scw.cloud/loki/api/v1/push",
    tags={"job": "waitinglist-function"},
    auth=(SCALEWAY_SECRET_KEY, COCKPIT_TOKEN_SECRET_KEY),
    version="1",
)

logger = logging.getLogger("waitinglist-function")
logger.addHandler(handler)
logger.setLevel(logging.INFO)


s3_client = boto3.client('s3',
    region_name=SCALEWAY_REGION,
    endpoint_url=f'https://s3.{SCALEWAY_REGION}.scw.cloud',
    aws_access_key_id=SCALEWAY_ACCESS_KEY,
    aws_secret_access_key=SCALEWAY_SECRET_KEY
)

def fetch_and_parse_market_data():
    url = "https://eu-trade.naeu.playblackdesert.com/Trademarket/GetWorldMarketWaitList"
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'BlackDesert'
    }

    response = requests.post(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return parse_data(data['resultMsg'])
    else:
        logging.error(f"Error: Received status code {response.status_code}")
        return None

def parse_data(data):
    if data == '0':
        logging.info("No items in the market waiting list.")
        return []

    items = data.split('|')
    parsed_items = []

    for item in items:
        if item:
            details = item.split('-')
            if len(details) == 4:
                timestamp = int(details[3])
                readable_timestamp = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                item_dict = {
                    'Item ID': details[0],
                    'Enhancement Level': details[1],
                    'Price': details[2],
                    'Timestamp': readable_timestamp
                }
                parsed_items.append(item_dict)
            else:
                logging.error(f"Skipping malformed item: {item}")

    return parsed_items

def save_to_json(data, filename="market_data.json"):
    json_data = json.dumps(data, indent=4)
    s3_client.put_object(
        Bucket=SCALEWAY_BUCKET_NAME,
        Key=filename,
        Body=json_data
    )
    logger.info(f"Market data successfully saved to {filename} in Scaleway Object Storage.")
    #Send message to Kafka que
    message = {
        'bucket': SCALEWAY_BUCKET_NAME,
        'key': filename,
        'timestamp': datetime.datetime.now().isoformat()
    }
    producer.send(KAFKA_TOPIC, json.dumps(message).encode('utf-8'))
    producer.flush()
    logger.info(f"Kafka message sent for {filename} update")

def main():
    market_data = fetch_and_parse_market_data()
    if market_data is not None and market_data:
        save_to_json(market_data)
    logger.info("Waiting list data processing completed.")

#not sure I need this was in SO
def handle(event, context):
    main()
    return {"statusCode": 200, "body": "Waiting list data processed successfully"}

if __name__ == "__main__":
    main()
