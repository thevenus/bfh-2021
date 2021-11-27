#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

import logging
import requests
from requests.auth import HTTPBasicAuth

user_tokens = {}

from telegram import Update, user, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import UPDATE_CHOSEN_INLINE_RESULT
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

domain = 'https://revofood.pythonanywhere.com/'

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
# Best practice would be to replace context with an underscore,
# since context is an unused local variable.
# This being an example and not having context present confusing beginners,
# we decided to have it present as context.
def qosul(update: Update, context: CallbackContext) -> None:
    """Sends explanation on how to use the bot."""
    chat_id = update.message.chat_id
    keyboard = [
        [
            InlineKeyboardButton("Havanın temperaturu", callback_data='1'),
            InlineKeyboardButton("Havanın rütubəti", callback_data='2'),
        ],
        [
            InlineKeyboardButton("Torpağın pH dəyəri", callback_data='3'),
            InlineKeyboardButton("Torpağın nəmişliyi", callback_data='4'),
        ],
        [InlineKeyboardButton("Gəlir Statistikası", callback_data='5')],
        [InlineKeyboardButton("Satış Statistikası", callback_data='6')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        email = context.args[0]
        password = context.args[1]
        response = requests.post(domain + 'api/rest-auth/login/', {'email' : email, 'password' : password})
        if (response.status_code == 200):
            update.message.reply_text('Hesabınıza daxil oldunuz!', reply_markup=reply_markup)
            user_tokens[chat_id] = response.json()['key']
        else:
            update.message.reply_text('Elektron poçt ünvanınız və ya parolunuz yanlışdır!')

    except (IndexError, ValueError):
        update.message.reply_text('İstifadə: /qosul <elektron poçt> <parol>')

def button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery

    # query.edit_message_text(text=f"Selected option: {query.data}")
    
    if (query.data == '5'):
        gelirStatistika(update, context)


def gelirStatistika(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    try:
        response = requests.get(domain + 'api/income/', headers={'Authorization' : 'Token '+ user_tokens[chat_id]})
    
        gs = 'Bu günkü gəliriniz: '+str(response.json()[0]['today'])+'₼\n' \
            + 'Dünənki gəliriniz: '+str(response.json()[1]['yesterday'])+'₼\n' \
            + 'Son 1 həftədəki gəliriniz: '+str(response.json()[2]['last_one_week'])+'₼\n' \
            + 'Son 1 aydakı gəliriniz: '+str(response.json()[3]['last_one_month'])+'₼\n'
        
        update.message.reply_text(gs)
    except KeyError:
        update.message.reply_text('Hesabınıza daxil olmamısınız!')

def satisStatistika(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    try:
        response = requests.get(domain + 'api/sellings/', headers={'Authorization' : 'Token '+ user_tokens[chat_id]})

        ss = 'Bu günkü satışlarınız: '+str(response.json()[0]['today'])+'kq\n' \
            + 'Dünənki satışlarınız: '+str(response.json()[1]['yesterday'])+'kq\n' \
            + 'Son 1 həftədəki satışlarınız: '+str(response.json()[2]['last_one_week'])+'kq\n' \
            + 'Son 1 aydakı satışlarınız: '+str(response.json()[3]['last_one_month'])+'kq\n'
        
        update.message.reply_text(ss)
    except KeyError:
        update.message.reply_text('Hesabınıza daxil olmamısınız!')

def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


def set_timer(update: Update, context: CallbackContext) -> None:
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(context.args[0])
        if due < 0:
            update.message.reply_text('Sorry we can not go back to future!')
            return

        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_once(alarm, due, context=chat_id, name=str(chat_id))

        text = 'Timer successfully set!'
        if job_removed:
            text += ' Old one was removed.'
        update.message.reply_text(text)

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <seconds>')


def unset(update: Update, context: CallbackContext) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Timer successfully cancelled!' if job_removed else 'You have no active timer.'
    update.message.reply_text(text)

def main() -> None:
    """Run bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("2134198856:AAFNng4gwIyLu3KiTKcc_hsEFgXAVeqVzyE")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("qosul", qosul))
    dispatcher.add_handler(CommandHandler("gelir_statistika", gelirStatistika))
    dispatcher.add_handler(CommandHandler("satis_statistika", satisStatistika))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()