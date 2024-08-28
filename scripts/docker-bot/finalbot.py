"""
This module provides a Discord bot that allows users to register and monitor the market for specific items and enhancement levels. The bot has the following commands:

- `!register <item_id> <enhancement_level>`: Registers the user for the specified item and enhancement level.
- `!remove <item_id> <enhancement_level>`: Removes the user's registration for the specified item and enhancement level.
- `!listall`: Lists all the items the user is registered for.

The bot also periodically checks the market data and sends notifications to users when their registered items are listed.
"""

import discord
from discord.ext import commands
import json
import requests
import asyncio
import aiohttp
import boto3
import os
import logging
import logging_loki
#from compute import compute_sales


intents = discord.Intents.all()
intents.messages = True
intents.guilds = True
client = discord.Client(intents=intents)

bot = commands.Bot(command_prefix='!', intents=intents)


SCALEWAY_REGION = 'fr-par'
SCALEWAY_BUCKET_NAME = 'bdo-market-ids'
TOKEN = os.environ['DISCORD_TOKEN']
SCALEWAY_ACCESS_KEY = os.environ['SCALEWAY_ACCESS_KEY']
SCALEWAY_SECRET_KEY = os.environ['SCALEWAY_SECRET_KEY']
COCKPIT_TOKEN_SECRET_KEY = os.environ['COCKPIT_TOKEN_SECRET_KEY']


s3_client = boto3.client('s3',
    region_name=SCALEWAY_REGION,
    endpoint_url=f'https://s3.{SCALEWAY_REGION}.scw.cloud',
    aws_access_key_id=SCALEWAY_ACCESS_KEY,
    aws_secret_access_key=SCALEWAY_SECRET_KEY
)


handler = logging_loki.LokiHandler(
    url="https://logs.cockpit.fr-par.scw.cloud/loki/api/v1/push",
    tags={"job": "discord-bot"},
    auth=(SCALEWAY_SECRET_KEY, COCKPIT_TOKEN_SECRET_KEY),
    version="1",
)

logger = logging.getLogger("discord-bot")
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def load_registrations():
    try:
        response = s3_client.get_object(Bucket=SCALEWAY_BUCKET_NAME, Key='registrations.json')
        return json.loads(response['Body'].read().decode('utf-8'))
    except s3_client.exceptions.NoSuchKey:
        return {}

def save_registrations(data):
    s3_client.put_object(
        Bucket=SCALEWAY_BUCKET_NAME,
        Key='registrations.json',
        Body=json.dumps(data, indent=4)
    )

async def register_user(user_id, item_id, enhancement_level, email=None):
    registrations = load_registrations()
    user_id_str = str(user_id)

    item_name = await fetch_item_name(item_id, enhancement_level) or "Unknown Item"

    if user_id_str not in registrations:
        registrations[user_id_str] = []

    registration = {
        'item_id': item_id,
        'enhancement_level': enhancement_level,
        'item_name': item_name
    }
    if email:
        registration['email'] = email

    if not any(reg['item_id'] == item_id and reg['enhancement_level'] == enhancement_level for reg in registrations[user_id_str]):
        registrations[user_id_str].append(registration)

    save_registrations(registrations)

def remove_user_registration(user_id, item_id, enhancement_level):
    registrations = load_registrations()
    user_id_str = str(user_id)

    if user_id_str in registrations:
        registrations[user_id_str] = [reg for reg in registrations[user_id_str] if not (reg['item_id'] == item_id and reg['enhancement_level'] == enhancement_level)]

        if not registrations[user_id_str]:
            del registrations[user_id_str]

        save_registrations(registrations)
        return True

    return False

async def fetch_item_name(item_id, enhancement_level):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.arsha.io/v2/eu/item?id={item_id}&lang=en") as response:
            if response.status == 200:
                items = await response.json()
                if isinstance(items, list):
                    for item in items:
                        if isinstance(item, dict) and str(item.get('maxEnhance', 0)) == enhancement_level:
                            return item.get('name')
                elif isinstance(items, dict):
                    if str(items.get('maxEnhance', 0)) == enhancement_level:
                        return items.get('name')
    return None

async def check_market_data():
    while True:
        try:
            response = s3_client.get_object(Bucket=SCALEWAY_BUCKET_NAME, Key='market_data.json')
            market_data = json.loads(response['Body'].read().decode('utf-8'))

            registrations = load_registrations()

            for user_id, user_regs in registrations.items():
                for reg in user_regs:
                    for item in market_data:
                        if item.get('Item ID') == reg.get('item_id') and item.get('Enhancement Level') == reg.get('enhancement_level'):
                            item_name = await fetch_item_name(reg['item_id'], reg['enhancement_level']) or "Item"
                            user = await bot.fetch_user(int(user_id))
                            await user.send(f"{item_name} with enhancement level {reg['enhancement_level']} has been listed at {item['Timestamp']}")
        except Exception as e:
            logger.error(f"An error occurred: {e}")

        await asyncio.sleep(420)  # Check every 7 minutes



@bot.command(name='register')
async def on_register(ctx, item_id: str, enhancement_level: str, email: str = None):
    await register_user(ctx.author.id, item_id, enhancement_level, email)
    response = f"{ctx.author.mention}, you're now registered for item ID {item_id} with enhancement level {enhancement_level}."
    if email:
        response += f" Notifications will also be sent to {email}."
    await ctx.send(response)

@bot.command(name='remove')
async def on_remove(ctx, item_id: str, enhancement_level: str):
    if remove_user_registration(ctx.author.id, item_id, enhancement_level):
        await ctx.send(f"{ctx.author.mention}, your registration for item ID {item_id} with enhancement level {enhancement_level} has been removed.")
    else:
        await ctx.send(f"{ctx.author.mention}, no registration found for item ID {item_id} with enhancement level {enhancement_level}.")

@bot.command(name='listall')
async def on_listall(ctx):
    user_id_str = str(ctx.author.id)
    registrations = load_registrations()

    if user_id_str in registrations:
        registered_items = registrations[user_id_str]
        if registered_items:
            response = "You're registered for the following items:\n"
            for reg in registered_items:
                response += f"Item Name: {reg['item_name']}, ID: {reg['item_id']}, Enhancement Level: {reg['enhancement_level']}\n"
        else:
            response = "You have no registered items."
    else:
        response = "You have no registered items."

    await ctx.send(f"{ctx.author.mention}, {response}")




#Main loop
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    bot.loop.create_task(check_market_data())


if __name__ == "__main__":
    bot.run(TOKEN)


