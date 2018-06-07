import os
from urlsave import Parser, Browser, Storage, Bot
import json
import time
import schedule
import logging
from telegram.ext import CommandHandler

path = os.path.join(".", "examples", "vacancies")

logging.basicConfig(filename=os.path.join(path, "errors.log"),
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


def loop_files(bot):
    files = [f for f in os.listdir(path) if f.endswith(".yml")]
    if not any(files):
        return
    
    with Browser() as driver:
        for file in files:
            try:
                update(file, bot, driver)
            except:
                logging.exception(f"An exception occured parsing file {file}:", exc_info=True)
                bot.send(f'<i>Error parsing {file} ({Storage.make_timestamp()})</i>')

                
    
def update(file, bot, driver):
    with open(os.path.join(path, file)) as f:
        job = f.read()
    
    p = Parser(job, driver)
    p.start()
        
    with Storage(os.path.join(path, "vacancies.sqlite")) as db:
        db.update_db(p.storage, subset=file)
        new = [json.loads(x) for x in db.get_new(subset=file)]
    
    for i in new:
        division = f' ({i["Division"]})' if i.get("Division") else ''
        bot.send(f"{i['Company'] + division}:\n<a href='{i['Url']}'>{i['Job']}</a>")

def run_cmd(bot, update, telegramBot):
    loop_files(telegramBot)

        
def main():
    bot = Bot(os.path.join(path, "vacancies.bot"))
    bot.dp.add_handler(CommandHandler("run", lambda bot,update, telegrambot: run_cmd(telegrambot)))
    
    schedule.every().day.at("08:00").do(loop_files, bot)
    schedule.every().day.at("18:00").do(loop_files, bot)
        
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