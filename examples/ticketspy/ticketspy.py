import os
from urlsave import Parser, Browser, Storage, Bot
import json
import time
import schedule
import logging

path = os.path.join(".", "examples", "ticketspy")

logging.basicConfig(filename=os.path.join(path, "ticketspy.log"))

def update(bot):
    with open(os.path.join(path, "ticketspy.yml")) as f:
        job = f.read()
    
    with Browser() as driver:
        p = Parser(job, driver)
        p.start()
        
    with Storage(os.path.join(path, "ticketspy.sqlite")) as db:
        db.update_db(p.storage)
        new = [json.loads(x) for x in db.get_new()]
    
    for i in new:
        bot.send(f"<a href='{i['url']}'>{i['text']}</a>")


        
def main():
    bot = Bot(os.path.join(path, "ticketspy.bot"))
    schedule.every(5).minutes.do(update, bot)
    
    while True:
        try:
            time.sleep(5)
            schedule.run_pending()
        except (KeyboardInterrupt, SystemExit):
            os._exit(1)
        except:
            logging.exception(f"{Storage.make_timestamp()}: An error occured", exc_info=True)
		

if __name__ == '__main__':
    main()