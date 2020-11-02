import db
import var

from telegram import Update, User, Bot, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

import re
import html
import traceback
import json
import logging

logger = logging.getLogger(__name__)


class TeleBot:
    def __init__(self, token, startFuc, pauseFuc):
        self.updater = Updater(token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.bot = Bot(token)
        self.startFuc = startFuc
        self.pauseFuc = pauseFuc
        self.addHandler()

    def sendMsg(self, chatId, msg):
        self.bot.send_message(chatId, msg)

    def auth(self, update, context):
        if db.check(update.message.from_user['id']):
            return True
        self.fail(update, context)
        return False

    def error_handler(self, update, context):
        """Log the error and send a telegram message to notify the developer."""
        logger.error(msg="Exception while handling an update:",
                     exc_info=context.error)

        tb_list = traceback.format_exception(
            None, context.error, context.error.__traceback__)
        tb_string = ''.join(tb_list)

        message = (
            '!!! An exception was Occured !!!\n'
            '<pre>update = {}</pre>\n\n'
            '<pre>{}</pre>'
        ).format(
            html.escape(json.dumps(update.to_dict(),
                                   indent=2, ensure_ascii=False)),
            html.escape(tb_string),
        )

        chatId = db.get('admin', 'chatId', 'akses')
        context.bot.send_message(chat_id=chatId,
                                 text=message, parse_mode=ParseMode.HTML)

    def fail(self, update, context):
        update.message.reply_text(var.temMsg['welcome'])

    def start(self, update, context):
        if not self.auth(update, context):
            return

        if not db.check(update.message.from_user['id']):
            update.message.reply_text(var.temMsg['error'])
            return

        self.startFuc(update.message.from_user['id'])

    def setUrl(self, update, context):
        """
        docstring
        """
        if not self.auth(update, context):
            return

        text = update.message.text.split(' ')
        if len(text) == 2:
            db.addConfig(update.message.from_user['id'], 'url', text[1])
        update.message.reply_text(
            var.temMsg['url'] + db.get(update.message.from_user['id'], 'url'))

    def setPayload(self, update, context):
        """
        docstring
        """
        if not self.auth(update, context):
            return

        text = update.message.text.split(' ')
        if len(text) == 2:
            db.addConfig(
                update.message.from_user['id'], 'payload', text[1])
        update.message.reply_text(
            var.temMsg['payload'] + db.get(update.message.from_user['id'], 'payload'))

    def setTime(self, update, context):
        """
        docstring
        """
        if not self.auth(update, context):
            return

        text = update.message.text.split(' ')
        if len(text) == 2:
            db.addConfig(
                update.message.from_user['id'], 'waktu', text[1])
        update.message.reply_text(
            var.temMsg['waktu'] + db.get(update.message.from_user['id'], 'waktu'))

    def setLibur(self, update, context):
        """
        docstring
        """
        if not self.auth(update, context):
            return

        text = update.message.text.split(' ')
        if len(text) == 2:
            db.addConfig(
                update.message.from_user['id'], 'libur', text[1])
        update.message.reply_text(
            var.temMsg['libur'] + db.get(update.message.from_user['id'], 'libur'))

    def sodiq(self, update, context):
        """
        docstring
        """
        if re.search('^sodiq', update.message.text):
            db.addUser(
                update.message.from_user['id'], update.effective_chat['id'])
            update.message.reply_text(var.temMsg['success'])
            self.help(update, context)
            return
        self.fail(update, context)

    def help(self, update, context):
        """
        docstring
        """
        if not self.auth(update, context):
            return

        update.message.reply_text(var.temMsg['help'])

    def pause(self, update, context):
        """
        docstring
        """
        if not self.auth(update, context):
            return

        text = update.message.text.split(' ')
        if len(text) == 2:
            try:
                long = int(text[1])
                self.pauseFuc(update.message.from_user['id'], long)
            except Exception as e:
                update.message.reply_text('Masukan hanya Angka !!!')
                update.message.reply_text('Error : ' + e.__str__())
                return

        pauseIsoFormat = db.get(update.message.from_user['id'], 'pause')
        update.message.reply_text('Skip Smapai => ' + pauseIsoFormat)

    def addHandler(self):
        self.dispatcher.add_error_handler(self.error_handler)
        self.dispatcher.add_handler(CommandHandler('start', self.start))
        self.dispatcher.add_handler(CommandHandler('url', self.setUrl))
        self.dispatcher.add_handler(CommandHandler('payload', self.setPayload))
        self.dispatcher.add_handler(CommandHandler('waktu', self.setTime))
        self.dispatcher.add_handler(CommandHandler('libur', self.setLibur))
        self.dispatcher.add_handler(CommandHandler('pause', self.pause))
        self.dispatcher.add_handler(CommandHandler('help', self.help))
        self.dispatcher.add_handler(MessageHandler(
            Filters.text & ~Filters.command, self.sodiq))
        self.dispatcher.add_handler(CommandHandler('reset', self.reset))

    def run(self):
        self.updater.start_polling()
        self.updater.idle()

    def reset(self, update, context):
        """
        docstring
        """
        update.message.reply_text('Mereset ...')
        db.addConfig(update.message.from_user['id'], 'trigger', '')
        update.message.reply_text('Layanan Dihentikan')
