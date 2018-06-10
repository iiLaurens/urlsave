import os
from urlsave import Parser, Browser, Storage, Bot
import time
import schedule
import logging
import io
from telegram.ext import CommandHandler

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
            db.update_db(p.storage)
        
        s = ""
        history = 0.0
        value = 0.0
        for i in p.storage:
            s += f"*{i['Fund']}:*\n`€{i['Value']:9.2f}  ({i['Value'] - i['History']:7.2f})`\n"
            history += i['History']
            value += i['Value']
            
        s += f"\n*TOTAL:*\n`€{value:9.2f} ({value - history:8.2f})`"
        s += f"\n  p.p.:\n`€{value/5:9.2f} ({(value - history)/5:8.2f})`"
        
        bot.send(s, parse_mode="Markdown")
    except:
        bot.send("Check niet gelukt!")
        raise
        

def check(resp, bot):
    resp.message.reply_text("Bezig met handmatige check...")
    update(bot)
        
    
def main():
    bot = Bot(os.path.join(path, "binck.bot"))
    bot.dp.add_handler(CommandHandler("check", lambda dummy1, resp: check(resp, bot)))
    
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
            logging.exception(f"{Storage.make_timestamp()}: An error occured", exc_info=True)
		

if __name__ == '__main__':
    main()