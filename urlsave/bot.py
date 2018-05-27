# -*- coding: utf-8 -*-
"""
Selenium using headless chrome test script

This is a test script file.
"""

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import yaml

class Bot(object):
    def __init__(self, bot_config_file):
        self.bot_config_file = bot_config_file
        
        # Load configuration from a (secret) file
        with open(bot_config_file, 'r') as f:
            bot_config = yaml.load(f.read())
            
        self.token = bot_config['token']
        self.chat_ids = set(bot_config.get("chat_ids", []))

        self.updater = Updater(self.token)

        self.dp = self.updater.dispatcher

        # on different commands - answer in Telegram
        self.dp.add_handler(CommandHandler("start", self.start))
        self.dp.add_handler(CommandHandler("stop",  self.stop))
        
    def start_bot(self):
        # Start the Bot
        self.updater.start_polling()
    
        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        #self.updater.idle()
        
        
    def start(self, bot, update):
        """Send a message when the command /start is issued."""
        chat_id = update.message.chat_id
        self.chat_ids.add(chat_id)
        
        update.message.reply_text('Started!')
        
        self.save_config()
    
    def stop(self, bot, update):
        """Send a message when the command /start is issued."""
        chat_id = update.message.chat_id
        self.chat_ids.discard(chat_id)
        
        update.message.reply_text('Stopped!')
        
        self.save_config()
        
    def save_config(self):
        with open(self.bot_config_file, 'w+') as f:
            f.write(yaml.dump({'token': self.token,
                               'chat_ids': list(self.chat_ids)}))
    
    def send(self, msg):
        for chat_id in self.chat_ids:
            self.updater.bot.send_message(chat_id=chat_id,
                                          text=msg, 
                                          parse_mode="Markdown")