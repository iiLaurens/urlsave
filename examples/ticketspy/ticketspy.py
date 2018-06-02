import os
from urlsave import Parser, Browser, Storage, Bot
import json
import yaml
import time
import schedule
import logging

path = "D:\\Programming\\Python\\urlsave\\examples\\ticketspy"

logging.basicConfig(filename=os.path.join(path, "ticketspy.log"))

def update(bot):
    with open(os.path.join(path, "ticketspy.yml")) as f:
        job = f.read()
    
    with Browser() as driver:
        p = Parser(job, driver)
        p.start()
        
    with Storage(os.path.join(path, "ticketspy.sqlite")) as db:
        db.update_db(p.storage)
        new = [yaml.dump(json.loads(x), allow_unicode=True).replace("\n...\n", "") for x in db.get_new()]
    
    for i in new:
        bot.send(i)


        
def main():
    bot = Bot(os.path.join(path, "ticketspy.bot"))
    schedule.every(1).minutes.do(update, bot)
    
    while True:
        try:
            time.sleep(5)
            schedule.run_pending()
        except (KeyboardInterrupt, SystemExit):
            bot.updater.stop()
            raise
        except:
            logging.exception(f"{Storage.make_timestamp()}: An error occured", exc_info=True)
		

if __name__ == '__main__':
    main()