import os
from urlsave import Parser, Browser, Storage, Bot
import time
import schedule
import logging
import io
from telegram.ext import CommandHandler
import json

path = os.path.join(".", "examples", "stocks")

logging.basicConfig(filename=os.path.join(path, "errors.log"))

def update(bot):
    try:
        with io.open(os.path.join(path, "binck.yml"),'r',encoding='utf8') as f:
            job = f.read()
        
        with Browser() as driver:
            p = Parser(job, driver)
            p.start()
            
        with Storage(os.path.join(path, "binck.sqlite")) as db:
            db.update_db(p.storage, subset="stocks")
        
        c = get_cash()
        
        s = ""
        history = 0.0
        value = 0.0
        for i in p.storage:
            s += f"*{i['Fund']}:*\n`€{i['Value']:9.2f}  ({i['Value'] - i['History']:7.2f})`\n"
            history += i['History']
            value += i['Value']
        
        s += f"\n*TOTAL (excl. cash):*\n`€{value:9.2f} ({value - history:8.2f})`"
        s += f"\np.p.:\n`€{value/5:9.2f} ({(value - history)/5:8.2f})`"
        s += f"\n\n*Cash:*\n`€{c:9.2f}` (p.p.: `€{c/5:.2f}`)"
        
        bot.send(s, parse_mode="Markdown")
    except:
        bot.send("Check niet gelukt!")
        raise
        
def get_cash():
    with Storage(os.path.join(path, "binck.sqlite")) as db:
        try:
            c = json.loads(db.get_active(subset="cash")[0]).get("value", 0)
        except:
            c = 0
    return c


def cash(resp, bot, c):
    if resp.message.from_user['first_name'] != "Laurens":
        return
    
    try:
        c = float(c)
    except:
        resp.message.reply_text(f"{resp.message.text} is geen geldig getal!")
        return
    
    old = get_cash()
    
    with Storage(os.path.join(path, "binck.sqlite")) as db:
        db.update_db({"value": old + c}, subset="cash")
        
    bot.send(f"Nieuwe euro balans is €{old + c:.2f} euro (delta: €{c:.2f}).")



def check(resp, bot):
    resp.message.reply_text("Bezig met handmatige check...")
    update(bot)
        
    
def main():
    bot = Bot(os.path.join(path, "binck.bot"))
    bot.dp.add_handler(CommandHandler("check", lambda dummy1, resp: check(resp, bot)))
    bot.dp.add_handler(CommandHandler("cash", lambda dummy1, resp, args: cash(resp, bot, args[0]), pass_args=True))
    
    schedule.every().monday.at("17:00").do(update, bot)
    schedule.every().tuesday.at("17:00").do(update, bot)
    schedule.every().wednesday.at("17:00").do(update, bot)
    schedule.every().thursday.at("17:00").do(update, bot)
    schedule.every().friday.at("17:00").do(update, bot)
    
    while True:
        try:
            time.sleep(schedule.idle_seconds())
            schedule.run_pending()
        except (KeyboardInterrupt, SystemExit):
            os._exit(1)
        except:
            raise
            logging.exception(f"{Storage.make_timestamp()}: An error occured", exc_info=True)
		

if __name__ == '__main__':
    main()