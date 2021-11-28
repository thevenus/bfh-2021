#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

import logging
import requests
from requests.auth import HTTPBasicAuth
import json

user_tokens = {}

from telegram import Update, update, user, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import UPDATE_CHOSEN_INLINE_RESULT
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

domain = 'https://revofood.pythonanywhere.com/'

def daxilol(update: Update, context: CallbackContext) -> None:
    """Sends explanation on how to use the bot."""
    chat_id = update.message.chat_id
    keyboard = [
        [
            InlineKeyboardButton("Havanın temperaturu", callback_data='1'),
            InlineKeyboardButton("Havanın rütubəti", callback_data='2'),
        ],
        [InlineKeyboardButton("Gəlir Statistikası", callback_data='3')],
        [InlineKeyboardButton("Satış Statistikası", callback_data='4')],
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


def funksiyalar(update:Update, context: CallbackContext) -> None:
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
    update.message.reply_text("Funksiyalar",reply_markup=reply_markup)

def button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery

    # query.edit_message_text(text=f"Selected option: {query.data}")

    if (query.data == '1'):
        temp(update, context)

    if (query.data == '2'):
        rutubet(update, context)
    
    if (query.data == '3'):
        gelirStatistika(update, context)

    if (query.data == '4'):
        satisStatistika(update, context)

def gelirStatistika(update: Update, context: CallbackContext) -> None:
    if update.message is not None:
        chat_id = update.message.chat.id
        print(update.message.chat.id)
    elif update.callback_query is not None:
        # from a callback message
        chat_id = update.callback_query.message.chat.id
        print(update.callback_query.message.chat.id)
    # chat_id = update.message.chat_id
    try:
        response = requests.get(domain + 'api/income/', headers={'Authorization' : 'Token '+ user_tokens[chat_id]})
    
        gs = 'Bu günkü gəliriniz: '+str(response.json()[0]['today'])+'₼\n' \
            + 'Dünənki gəliriniz: '+str(response.json()[1]['yesterday'])+'₼\n' \
            + 'Son 1 həftədəki gəliriniz: '+str(response.json()[2]['last_one_week'])+'₼\n' \
            + 'Son 1 aydakı gəliriniz: '+str(response.json()[3]['last_one_month'])+'₼\n'
        
        if update.message is not None:
            update.message.reply_text(gs)
        elif update.callback_query is not None:
            update.callback_query.message.reply_text(gs)

        # update.message.reply_text(gs)
    except KeyError:
        if update.message.chat_id is not None:
            update.message.reply_text('Hesabınıza daxil olmamısınız!')
        elif update.callback_query is not None:
            update.callback_query.message.reply_text('Hesabınıza daxil olmamısınız!')
        

def satisStatistika(update: Update, context: CallbackContext) -> None:
    if update.message is not None:
        chat_id = update.message.chat.id
        print(update.message.chat.id)
    elif update.callback_query is not None:
        # from a callback message
        chat_id = update.callback_query.message.chat.id
        print(update.callback_query.message.chat.id)
    try:
        response = requests.get(domain + 'api/sellings/', headers={'Authorization' : 'Token '+ user_tokens[chat_id]})

        ss = 'Bu günkü satışlarınız: '+str(response.json()[0]['today'])+'kq\n' \
            + 'Dünənki satışlarınız: '+str(response.json()[1]['yesterday'])+'kq\n' \
            + 'Son 1 həftədəki satışlarınız: '+str(response.json()[2]['last_one_week'])+'kq\n' \
            + 'Son 1 aydakı satışlarınız: '+str(response.json()[3]['last_one_month'])+'kq\n'
        
        if update.message is not None:
            update.message.reply_text(ss)
        elif update.callback_query is not None:
            update.callback_query.message.reply_text(ss)
    except KeyError:
        if update.message.chat_id is not None:
            update.message.reply_text('Hesabınıza daxil olmamısınız!')
        elif update.callback_query is not None:
            update.callback_query.message.reply_text('Hesabınıza daxil olmamısınız!')

def temp(update: Update, context: CallbackContext) -> None:
    if update.message is not None:
        chat_id = update.message.chat.id
    elif update.callback_query is not None:
        chat_id = update.callback_query.message.chat.id
        response = requests.get(domain + 'api/rest-auth/user/', headers={'Authorization' : 'Token '+ user_tokens[chat_id]})
        

    print(response.json())
    new_response = requests.get(domain + 'api/hardwareDataGet/'+str(response.json()['pk'])+'/')
    print(new_response.json()[-1]['sent_data'])

    if update.message is not None:
            update.message.reply_text('Havanın temperaturu: '+str(json.loads(new_response.json()[-1]['sent_data'])["temp"])+'C')
    elif update.callback_query is not None:
        update.callback_query.message.reply_text('Havanın temperaturu: '+str(json.loads(new_response.json()[-1]['sent_data'])["temp"])+'C')
    # /api/hardwareDataGet/{user_id}/
    # update.message.reply_text('Hesabınıza daxil oldunuz!', reply_markup=reply_markup)
    # user_tokens[chat_id] = response.json()['key']

def rutubet(update: Update, context: CallbackContext) -> None:
    if update.message is not None:
        chat_id = update.message.chat.id
    elif update.callback_query is not None:
        chat_id = update.callback_query.message.chat.id
        response = requests.get(domain + 'api/rest-auth/user/', headers={'Authorization' : 'Token '+ user_tokens[chat_id]})
        

    print(response.json())
    new_response = requests.get(domain + 'api/hardwareDataGet/'+str(response.json()['pk'])+'/')
    print(new_response.json()[-1]['sent_data'])

    if update.message is not None:
            update.message.reply_text('Havanın rütubəti: '+str(json.loads(new_response.json()[-1]['sent_data'])["humidity"]))
    elif update.callback_query is not None:
        update.callback_query.message.reply_text('Havanın rütubəti: '+str(json.loads(new_response.json()[-1]['sent_data'])["humidity"]))

def main() -> None:
    """Run bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("TOKEN")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("daxilol", daxilol))
    dispatcher.add_handler(CommandHandler("gelir_statistika", gelirStatistika))
    dispatcher.add_handler(CommandHandler("satis_statistika", satisStatistika))
    dispatcher.add_handler(CommandHandler("funksiyalar", funksiyalar))
    dispatcher.add_handler(CommandHandler("temp", temp))
    dispatcher.add_handler(CommandHandler("rutubet", rutubet))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()