"""
Fetches the latest transaction timestamps and total trades for the Pearl Items of interest from the Black Desert Online trade market API, and inserts the data into a PostgreSQL database.

The function `fetch_latest_transaction_timestamps` takes a list of cleaned item data, represented as a list of dictionaries with `id` and `name` keys, and performs the following steps:

1. Connects to a PostgreSQL database using the provided connection parameters.
2. Inserts a new market snapshot record with the current timestamp, and retrieves the snapshot ID.
3. For each item in the cleaned data:
   - Fetches the latest transaction details for the item from the trade market API.
   - Extracts the latest transaction timestamp and total trades from the response.
   - Inserts the item into the `Items` table if it doesn't already exist.
   - Inserts the item trade data (item ID, snapshot ID, total trades, and amount of orders) into the `ItemTrades` table.
   - Sleeps for 0.5 seconds to avoid rate limiting.
4. Logs a success message and returns a success message.

The function `read_cleaned_data` is a helper function that reads the cleaned item data from a JSON file and returns it as a Python object.

All error loggin goes to main.log`.

For actual use this script should be ran in multithreading to speed up the process.
To avoid getting rate limited by the API, you can use proxies to run multiple queries simultaneously.
"""



import requests
import json
import time
from datetime import datetime
from unpack import unpack
import io
import logging
import os
import psycopg2
import boto3
import logging_loki





#Scaleway regions
SCALEWAY_REGION = 'fr-par'  # or your preferred region
SCALEWAY_BUCKET_NAME = 'bdo-market-ids'

#Scaleway secrets
SCALEWAY_ACCESS_KEY = os.environ['SCALEWAY_ACCESS_KEY']
SCALEWAY_SECRET_KEY = os.environ['SCALEWAY_SECRET_KEY']
COCKPIT_TOKEN_SECRET_KEY = os.environ['COCKPIT_TOKEN_SECRET_KEY']


DB_HOST =  os.environ['PGHOST']
DB_NAME =  os.environ['PGDATABASE']
DB_USER = os.environ['PGUSER']
DB_PASSWORD = os.environ['PGPASSWORD']


conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST
)
conn.autocommit = True

handler = logging_loki.LokiHandler(
    url="https://logs.cockpit.fr-par.scw.cloud/loki/api/v1/push",
    tags={"job": "market-scraper"},
    auth=(SCALEWAY_SECRET_KEY, COCKPIT_TOKEN_SECRET_KEY),
    version="1",
)

logger = logging.getLogger("market-scraper")
logger.addHandler(handler)
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3',
    region_name=SCALEWAY_REGION,
    endpoint_url=f'https://s3.{SCALEWAY_REGION}.scw.cloud',
    aws_access_key_id=SCALEWAY_ACCESS_KEY,
    aws_secret_access_key=SCALEWAY_SECRET_KEY
)
def read_cleaned_data():
    try:
        response = s3_client.get_object(Bucket=SCALEWAY_BUCKET_NAME, Key='cleaned_data.json')
        return json.loads(response['Body'].read().decode('utf-8'))
    except Exception as e:
        logger.error(f"Error reading cleaned data from Scaleway Object Storage: {e}")
        return None



def insert_item(item_id, item_name, cursor):
    cursor.execute("SELECT item_id FROM Items WHERE item_id = %s", (item_id,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO Items (item_id, name) VALUES (%s, %s)", (item_id, item_name))

def insert_market_snapshot(timestamp, cursor):
    cursor.execute("INSERT INTO MarketSnapshots (timestamp) VALUES (%s) RETURNING snapshot_id", (timestamp,))
    snapshot_id = cursor.fetchone()[0]
    return snapshot_id

def insert_item_trade(item_id, snapshot_id, total_trades, amount_of_orders, cursor):
    cursor.execute("""
        INSERT INTO ItemTrades (item_id, snapshot_id, total_trades, amount_of_orders)
        VALUES (%s, %s, %s, %s)
    """, (item_id, snapshot_id, total_trades, amount_of_orders))

def fetch_latest_transaction_timestamps(cleaned_data):
    if cleaned_data is None:
        logger.error("Cleaned data is None, skipping fetch_latest_transaction_timestamps.")
        return "Error: No cleaned data provided."

    url = "https://eu-trade.naeu.playblackdesert.com/Trademarket/GetWorldMarketSubList"
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'BlackDesert'
    }
    url2 = "https://eu-trade.naeu.playblackdesert.com/Trademarket/GetBiddingInfoList"

    cursor = conn.cursor()
    snapshot_id = insert_market_snapshot(datetime.now(), cursor)

    for item in cleaned_data:
        try:
            payload = {"keyType": 0, "mainKey": item["id"]}
            response = requests.post(url, headers=headers, json=payload)

            if response.status_code == 200:
                result_str = response.json().get("resultMsg", "")
                transactions = result_str.split('|')[:-1]  #Exclude the last empty segment
                if transactions:
                    latest_transaction = transactions[-1]  
                    transaction_details = latest_transaction.split('-')

                    timestamp = transaction_details[-1]  
                    total_trades = transaction_details[5] 

                    
                    readable_timestamp = datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')

            payload2 = {"keyType": 0,"mainKey": item["id"],"subKey": 0}
            response2 = requests.post(url2, headers=headers, json=payload2)
            if response2.status_code == 200:
                data = io.BytesIO(response2.content)
                unpacked_data = unpack(data)
                orders_info = unpacked_data.split('|')[0]
                amount_of_orders = orders_info.split('-')[2]

                insert_item(item["id"], item["name"], cursor)
                insert_item_trade(item["id"], snapshot_id, total_trades, amount_of_orders, cursor)
                time.sleep(0.3) #Change the timer to not get rate limited or swap to using proxies to run multiples queries
        except Exception as e:
            logger.error(f"Error processing item {item['id']}: {e}")
            continue

    cursor.close()
    logger.info(f"Updated data successfully saved to the database.")
    return "Updated data with timestamps and total trades successfully saved."


try:
    cleaned_data = read_cleaned_data()
    if cleaned_data:
        print(fetch_latest_transaction_timestamps(cleaned_data))
    else:
        logger.error("Failed to load cleaned data from Scaleway Object Storage.")
except Exception as e:
    logger.error(f"An unexpected error occurred: {e}")



conn.close()
