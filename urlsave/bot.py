# -*- coding: utf-8 -*-
"""
Selenium using headless chrome test script

This is a test script file.
"""

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.ext import messagequeue as mq
import yaml

class Bot(object):
    def __init__(self, bot_config_file):
        self.bot_config_file = bot_config_file
        
        # Load configuration from a (secret) file
        with open(bot_config_file, 'r') as f:
            bot_config = yaml.load(f.read())
            
        self.token = bot_config['token']
        self.chat_ids = set(bot_config.get("chat_ids", []))

        # Start message queue
        self._is_messages_queued_default = True
        self._msg_queue = mq.MessageQueue(all_burst_limit=3, all_time_limit_ms=3000)
        
        self.updater = Updater(self.token)
        self.dp = self.updater.dispatcher

        # on different commands - answer in Telegram
        self.dp.add_handler(CommandHandler("start", self.start))
        self.dp.add_handler(CommandHandler("stop",  self.stop))
        
        self.start_bot()
        
    def start_bot(self):
        # Start the Bot
        self.updater.start_polling()
        
        
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
    
    @mq.queuedmessage
    def send_queue(self, *args, **kwargs):
        return self.updater.bot.send_message(*args, **kwargs)
    
    
    def send(self, msg, parse_mode = "HTML"):
        for chat_id in self.chat_ids:
            isgroup = True if chat_id < 0 else False
            self.send_queue(chat_id=chat_id,
                            text=msg,
                            parse_mode=parse_mode,
                            isgroup = isgroup)
                                          
    def __del__(self):
        try:
            self._msg_queue.stop()
        except:
            pass
        try:
            self.updater.stop()
        except:
            pass