import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Bot, Chat
import requests
import json
from moralis import evm_api
from models import *
import asyncio
import time
import datetime
# import multiprocessing
from multiprocessing import Process
from dotenv import load_dotenv, find_dotenv
import os

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Union
from fastapi import Request

app = FastAPI()


@app.get('/')
async def index():
    return {"Real": "Python"}


class Wallet(BaseModel):
    wallet: str


@app.post('/alert/')
async def alert_all(wallet: Wallet):
    res = wallet.wallet
    chat_ids = all_chat_ids(res)
    print(chat_ids)
    for chat_id in chat_ids:
        print(chat_id)
        send_alert(chat_id=chat_id, wallet=res)

    return f"Alert sended to {chat_id} 🚨"


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Constants
load_dotenv(find_dotenv())
API_KEY = os.environ.get("MORALIS_API_KEY")  # Replace with your Moralis API key
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")  # Replace with your bot token


# Function to retrieve all token purchases from Etherscan
def get_all_token_purchases(wallet_address):
    # Make HTTP request to Etherscan
    params = {
        "address": str(wallet_address),
        "chain": "goerli",
    }
    result = evm_api.token.get_wallet_token_balances(api_key=API_KEY, params=params, )
    res = json.dumps(result, sort_keys=True)
    return res


def send_alert(chat_id, wallet):
    updater = Updater(BOT_TOKEN, use_context=True)
    updater.bot.sendMessage(chat_id=chat_id, text=f"<a href='https://etherscan.io/address/{wallet}'>Wallet</a>"
                                                  f" bought token!", parse_mode="HTML")
# Telegram bot commands

def start(update, context):
    # Bot.send_message(chat_id=343226145, text="HOLA!")
    chat_id = update.message.chat_id
    update.message.reply_text(
        "Hi! I'm a token tracker bot. Send me a wallet address to track the purchases of all tokens in the wallet.")
    print(chat_id)


def track_purchases(update, context):
    # Extract wallet address from user message
    wallet_address = update.message.text
    print("HERE!!!WALET ADDRESS >", wallet_address)
    purchases = get_all_token_purchases(wallet_address)
    if purchases:
        update.message.reply_text(f"The following token were found for {wallet_address} on Etherscan:")
        for token in purchases:
            balance = int(token['balance']) / 10 ** int(token['decimals'])
            update.message.reply_text(f"🪙Token: <b>{token['name']}</b> - {balance} {token['symbol']}💲 | "
                                      f"<a href='https://etherscan.io/address/{token['token_address']} '>Contract</a>",
                                      parse_mode="HTML")

    else:
        update.message.reply_text(f"No token purchases were found for {wallet_address} on Etherscan.")


def add_wallet(update, context):
    wallet_address = context.args[0]
    chat_id = update.message.chat_id
    last_check = get_all_token_purchases(wallet_address)
    add_address(wallet_address, chat_id=chat_id, last_check=last_check)
    update.message.reply_text(f"Wallet: {wallet_address} added, chat_id: {chat_id}")


def check_address(update, context):
    wallet = context.args[0]
    info = get_all_token_purchases(wallet)
    info = json.loads(info)
    update.message.reply_text(f"The following token were found for {wallet} on Etherscan:")
    for token in info:
        print(token)
        balance = int(token['balance']) / 10 ** int(token['decimals'])
        update.message.reply_text(f"🪙Token: <b>{token['name']}</b> - {balance} {token['symbol']}💲 | "
                                      f"<a href='https://etherscan.io/address/{token['token_address']} '>Contract</a>",
                                      parse_mode="HTML")


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def run_api():
    uvicorn.run("main:app", host='0.0.0.0', port=4557, reload=True, workers=3)


# Main function
def run_bot():
    # Create the Updater and pass it your bot's token.
    updater = Updater(BOT_TOKEN, use_context=True)
    # j = updater.job_queue
    # job_daily = j.run_once(cron_jobs, 10)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("add_wallet", add_wallet))
    dp.add_handler(CommandHandler("check", check_address))
    # dp.add_handler(CommandHandler("test", cron_jobs))
    dp.add_handler(MessageHandler(Filters.text, track_purchases))

    # Add error handler
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()


def runInParallel(*fns):
    proc = []
    for fn in fns:
        p = Process(target=fn)
        p.start()
        proc.append(p)
    for p in proc:
        p.join()
    # Run the bot until you press Ctrl-C or the process receives SIG


if __name__ == '__main__':
    runInParallel(run_bot, run_api)
