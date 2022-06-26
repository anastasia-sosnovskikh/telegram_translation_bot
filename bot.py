# using python-telegram-bot
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from collections import defaultdict
from googletrans import Translator, LANGUAGES
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
import logging
import os

# PORT = int(os.environ.get('PORT', 5000))

# getting the token
token_path = "translation_bot_token.txt"
if os.path.isfile(token_path):
    token_file = open(token_path, "r")
    token_value = token_file.read()
    token_file.close()
 
# basic setup
TOKEN = token_value
translator = Translator()
users = defaultdict(lambda: 'en')
my_languages = {'ru', 'en', 'es', 'fr', 'pt', 'uk'}

# helper functions
def get_start_message(update):
	return 'Hello, {}! Type /lang to choose a language to translate your messages to! The default is English.'.format(update.message.chat.first_name)

def get_undefined_message(update):
	return 'Sorry, {}, I did not get that command.'.format(update.message.chat.first_name)

# handlers
def start(update, context):
    context.bot.send_message(
    	chat_id = update.effective_chat.id, 
    	text = get_start_message(update))

def echo(update, context):
	input_message = update.message.text
	from_lang = translator.detect(input_message).lang
	translation = translator.translate(text=input_message, src=from_lang, dest=users[update.effective_chat.id])
	context.bot.send_message(
    	chat_id=update.effective_chat.id, 
    	text='Detected Language: {}.'.format(LANGUAGES[from_lang].title()))
	context.bot.send_message(
    	chat_id=
    		update.effective_chat.id
    		,text=translation.text
    	)

def lang(update, context):
    keyboard_buttons = [
    	InlineKeyboardButton(lang.title(), callback_data=lang_code)
    	for lang_code, lang in LANGUAGES.items()
    	if lang_code in my_languages
    ]

    keyboard = [
    	keyboard_buttons[i:min(i+3, len(keyboard_buttons))]
    	for i in range(0, len(keyboard_buttons), 3)
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please choose the language to translate your messages to:', reply_markup=reply_markup)

def lang_button(update, context):
	query = update.callback_query
	users[update.effective_chat.id] = query.data
	query.answer() # CallbackQueries need to be answered, even if no notification to the user is needed
	query.edit_message_text(text="Your messages will be translated to {}.".format(LANGUAGES[users[update.effective_chat.id]].title()))

def unknown(update, context):
    context.bot.send_message(
    	chat_id = update.effective_chat.id, 
    	text = get_undefined_message(update))

def main():
	updater = Updater(token=TOKEN, use_context=True)
	dispatcher = updater.dispatcher
	logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

	# initialize handlers
	start_handler = CommandHandler('start', start)
	lang_handler = CommandHandler('lang', lang)
	lang_button_handler = CallbackQueryHandler(lang_button)
	echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
	unknown_handler = MessageHandler(Filters.command, unknown)

	# add handlers
	dispatcher.add_handler(start_handler)
	dispatcher.add_handler(echo_handler)
	dispatcher.add_handler(lang_handler)
	dispatcher.add_handler(lang_button_handler)
	dispatcher.add_handler(unknown_handler)

	# start the bot
	updater.start_polling() 

	# updater.start_webhook(listen="0.0.0.0",
    #                       port=int(PORT),
    #                       url_path=TOKEN)
	# updater.bot.setWebhook('https://vast-eyrie-25542.herokuapp.com/' + TOKEN)

	updater.idle()

if __name__ == '__main__':
    main()