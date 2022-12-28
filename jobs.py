import schedule
from main import *
from models import *
import time
import requests


def job():
    wallets = all_from_job()
    print("go go go |", time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    total_wallets = len(wallets)]
    print(f"Total Wallets 🔐: {total_wallets}",time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    for wallet in wallets:
        info = get_all_token_purchases(wallet)
        checked = check_1(wallet)
        if info == checked:
            print(f"Checked 📝 - {wallet}. Nothing Changed! |", time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
            # update.message.reply_text("1 min, not changed")
        else:
            print(f"❗️Checked - {wallet}. Update DETECTED❗️ |", time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
            url = 'http://127.0.0.1:4557/alert/'
            myobj = {'wallet': wallet}

            x = requests.post(url, json=myobj)

            print(x.text, time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
            update = edit_last_check(wallet, info)
            print(update, time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    return print("All wallets passed! |", time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))

schedule.every(30).seconds.do(job)
print("Jobs started 🚀🚀🚀 |", time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
while True:
    schedule.run_pending()
    time.sleep(1)