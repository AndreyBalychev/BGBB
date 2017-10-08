#!/usr/bin/python
#coding=utf-8

import telegram
from telegram.ext import Updater
from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.callbackqueryhandler import CallbackQueryHandler
from telegram.ext.conversationhandler import ConversationHandler
import logging
import checker
from storer import Storer

TOKEN_FILENAME = 'token.lst'

# Enable Logging
logging.basicConfig(
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
	level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


storer = Storer('database.db')

COUNTER_NAME, CALCULATION_TYPE, CALCULATION_RATE, BIO = range(4)

# Dictionary to store users by its id
users = {}

class UserInfo:
	def __init__(self, telegram_user):
		self.user = telegram_user
		self.counters = {}
		self.active_counter = None

	def add_active_counter(self):
		self.counters[self.active_counter.name] = self.active_counter
		logger.info("Add active counter %s for user %d" % (self.active_counter.name, self.user.id))

	def add_counter(self, counter):
		self.counters[counter.name] = counter
		logger.info("Add counter %s for user %d" % (counter.name, self.user.id))

class Calculator:
	def __init__(self, param):
		self.param = param
	
	def calc(self, sum):
		return int(sum / param)

	def to_string(self):
		return u"1 балл за %.2f рублей" % (self.param,)

class Counter:
	def __init__(self, name):
		self.name = name
		self.calculator = None

	def to_string(self):
		return u"%s (%s)" % (self.name, self.calculator.to_string())

	def get_balance(self):
		logger.info("Getting balance for card %s" % self.card_number)
		balance = checker.get_balance(self.card_number)
		return balance


def log_params(method_name, update):
	logger.debug("Method: %s\nFrom: %s\nchat_id: %d\nText: %s" %
		(method_name,
			update.message.from_user,
			update.message.chat_id,
			update.message.text))

#####################################################################

def save_data():
	storer.save('users', users)
	
def send_message_without_keybord(bot, update, text):
	reply_markup = telegram.ReplyKeyboardRemove()
	bot.sendMessage(chat_id=update.message.chat_id, text=text, reply_markup=reply_markup)

def get_user(update):
	telegram_user = update.message.from_user
	return users[telegram_user.id]

#####################################################################
# Обработчки команд

def hello(bot, update):
	log_params('hello', update)
	bot.sendMessage(update.message.chat_id, text="Мур")

def save_card(telegram_user, card_number):
	if not users.has_key(telegram_user.id):
		users[telegram_user.id] = UserInfo(telegram_user)
		logger.info("Create user %s" % telegram_user)
	user = users[telegram_user.id]
	if not user.cards.has_key(card_number):
		user.add_card(card_number)
		storer.save('users', users)

def get_balance(bot, update, args):
	log_params('hello', update)
	if len(args) != 1:
		send_message_without_keybord(bot, update, update.message.chat_id, text="Usage:\n/balance 1234567890")
		return
	card_number = args[0]
	balance = checker.get_balance(card_number)
	telegram_user = update.message.from_user
	save_card(telegram_user, card_number)
	response = "Card balance is %.2f rub." % (balance)
	send_message_without_keybord(bot, update, response)

def get_cards_list(bot, update):
	log_params('get_cards_list', update)
	telegram_user = update.message.from_user
	if not users.has_key(telegram_user.id) or len(users[telegram_user.id].cards) == 0:
		response = "You do not have any cards"
		if not users.has_key(telegram_user.id):
			logger.info("Has not record for user %s in db" % telegram_user.id)
		else:
			logger.info("There is %d card for user %s in db" % (len(users[telegram_user.id].cards, telegram_user.id)))
	else:
		response = ""
		cards = users[telegram_user.id].cards
		for card_info in cards.values():
			number = card_info.card_number
			balance = card_info.get_balance()
			response += "%s: %.2f \n" % (number, balance)
	send_message_without_keybord(bot, update, response)

def get_cards_list2(bot, update):
	log_params('get_cards_list', update)
	telegram_user = update.message.from_user
	if not users.has_key(telegram_user.id) or len(users[telegram_user.id].cards) == 0:
		response = "You do not have any cards"
		if not users.has_key(telegram_user.id):
			logger.info("Has not record for user %s in db" % telegram_user.id)
		else:
			logger.info("There is %d card for user %s in db" % (len(users[telegram_user.id].cards, telegram_user.id)))
	else:
		response = ""
		cards = users[telegram_user.id].cards
		for card_info in cards.values():
			number = card_info.card_number
			balance = card_info.get_balance()
			response += "%s: %.2f \n" % (number, balance)
	send_message_without_keybord(bot, update, response)

def unknown_command(bot, update):
	bot.sendMessage(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")

def unknown_message(bot, update):
	bot.sendMessage(chat_id=update.message.chat_id, text="Sorry, I didn't understand that your mean.")

def stop(bot, update):
	jobs = updater.job_queue

def start(bot, update):
	send_message_without_keybord(bot, update, "Hi! I'm BillyGoodBoy bot. I can check balance of your Strelka card.")
	telegram_user = update.message.from_user
	if not users.has_key(telegram_user.id):
		users[telegram_user.id] = UserInfo(telegram_user)
		logger.info("Create user %s" % telegram_user)
		save_data()
	

def test(bot, update):
	user = get_user(update)
	counters = user.counters.values()
	for counter in counters:
		bot.sendMessage(chat_id=update.message.chat_id, text=str(type(counter.name)))
		s = counter.calculator.to_string()
		bot.sendMessage(chat_id=update.message.chat_id, text=u"%s (%s)" % (counter.name, s))
		
#		bot.sendMessage(chat_id=update.message.chat_id, text=str(type(s)))
#		bot.sendMessage(chat_id=update.message.chat_id, text=s)
	return
	
	telegram_user = update.message.from_user
	cards = users[telegram_user.id].cards.keys()
	odd = cards[::2]
	even = cards[1::2]
	
	keys = map(lambda x, y: [x, y if y else ""], odd, even)
	#bot.sendMessage(chat_id=update.message.chat_id, text="This is the test command")
	#custom_keyboard = [[ telegram.Emoji.THUMBS_UP_SIGN, telegram.Emoji.THUMBS_DOWN_SIGN ]]
	args=("123",)
	#key = telegram.keyboardbutton.KeyboardButton("Кнопка", request_contact=None, request_location=None, args)
	custom_keyboard = [[ "/balance 03310208398", "/my" ],["1", "2", "3"]]
	reply_markup = telegram.ReplyKeyboardMarkup(keys, resize_keyboard=True, one_time_keyboard=True)
	bot.sendMessage(chat_id=update.message.chat_id, text="Выберите команду", reply_markup=reply_markup)

def test2(bot, update):
	keyboard = [[telegram.InlineKeyboardButton("Option 1", callback_data='1'),
				telegram.InlineKeyboardButton("Option 2", callback_data='2')],
				[telegram.InlineKeyboardButton("Option 3", callback_data='3')]]
	reply_markup = telegram.InlineKeyboardMarkup(keyboard)
	bot.sendMessage(chat_id=update.message.chat_id, text="Выберите команду", reply_markup=reply_markup)

def callback(bot, update):
	query = update.callback_query
	bot.editMessageText(text="Selected option: %s" % query.data,
						chat_id=query.message.chat_id,
						message_id=query.message.message_id)
	#	bot.sendMessage(chat_id=update.message.chat_id, text="<callback>")

def addcounter(bot, update):
	logger.info("addcounter")
	bot.sendMessage(chat_id=update.message.chat_id, text="Введите имя счетчика")
	return COUNTER_NAME

def choose_calculation_type(bot, update):
	telegram_user = update.message.from_user
	user = users[telegram_user.id]
	counter_name = update.message.text
	logger.info("choose_calculation_type %s" % (counter_name,))
	if user.counters.has_key(counter_name):
		bot.sendMessage(chat_id=update.message.chat_id, text="Счетчик с таким именем уже существует. Выберите другое имя")
		return COUNTER_NAME
	else:
		user.active_counter = Counter(counter_name)
		save_data()
		types = [["01", "02", "03", "04"]]
		reply_markup = telegram.ReplyKeyboardMarkup(types, resize_keyboard=True, one_time_keyboard=True)
		bot.sendMessage(chat_id=update.message.chat_id, text="Выберите тип подсчета", reply_markup=reply_markup)
		return CALCULATION_TYPE

def choose_calculation_rate(bot, update):
	telegram_user = update.message.from_user
	logger.info("choose_calculation_rate")
	user = users[telegram_user.id]
	calculation_type = update.message.text
	if calculation_type == "01":
		counter = user.active_counter
		counter.type = calculation_type
		bot.sendMessage(chat_id=update.message.chat_id, text="Введите ставку")
		return CALCULATION_RATE
	bot.sendMessage(chat_id=update.message.chat_id, text="Выберите тип подсчета")
	return CALCULATION_TYPE

def create_calculator(type, rate):
	if type == "01":
		return Calculator(rate)

def create_counter(bot, update):
	logger.info("create_counter")
	user = get_user(update)
	rate = update.message.text
	rate = float(rate)
	user.active_counter.calculator = create_calculator(user.active_counter.type, rate)
	user.add_active_counter()
	save_data()
	bot.sendMessage(chat_id=update.message.chat_id, text="Счетчик создан")
	return ConversationHandler.END

def cancel(bot, update):
	logger.info("cancel")
	bot.sendMessage(chat_id=update.message.chat_id, text="Операция отменена")
	user = get_user(update)
	user.active_counter = None

def getcounters(bot, update):
	logger.info("getcounters")
	user = get_user(update)
	counters_list = user.counters.values()
	l = [counter.to_string() for counter in counters_list]
#	counters_list = [str(counter) for counter in counters_list]
	response = "\n".join(l)
	bot.sendMessage(chat_id=update.message.chat_id, text=response)

def read_token():
	f = open(TOKEN_FILENAME)
	token = f.readline().strip()
	f.close()
	return token

def main():
	global users
	users = storer.read('users')
	if users is None:
		users = {}
	else:
		logger.info("%d records in users db" % len(users))

	token = read_token()
	updater = Updater(token)
	# Get the dispatcher to register handlers
	dp = updater.dispatcher

	# Add handlers for Telegram messages
#	dp.addUnknownTelegramCommandHandler(unknown_command)
#	dp.addTelegramMessageHandler(unknown_message)

#	dp.add_handler(MessageHandler(Filters.text, unknown_message))

	dp.add_handler(CommandHandler("start", start))
	
	dp.add_handler(CommandHandler("getcounters", getcounters))
#	dp.add_handler(CommandHandler("balance", get_balance))
#	dp.add_handler(CommandHandler("my", get_cards_list))
#	dp.add_handler(CommandHandler("mycards", get_cards_list2))
#	dp.add_handler(CommandHandler("stop", stop))
#	dp.add_handler(CommandHandler("start", start))
	dp.add_handler(CommandHandler("test", test))
#	dp.add_handler(CommandHandler("test2", test2))
#	dp.add_handler(CallbackQueryHandler(callback))
	choose_calculation_rate
	conv_handler = ConversationHandler(
		entry_points=[CommandHandler('addcounter', addcounter)],

		states={
			COUNTER_NAME: [MessageHandler(Filters.text, choose_calculation_type)],

			CALCULATION_TYPE: [MessageHandler(Filters.text, choose_calculation_rate),
					CommandHandler('cancel', cancel)],

			CALCULATION_RATE: [MessageHandler(Filters.text, create_counter),
					CommandHandler('cancel', cancel)]

		},
		
		fallbacks=[CommandHandler('cancel', cancel)]
	)
	dp.add_handler(conv_handler)
#	dp.addTelegramCommandHandler("help", help)
#	dp.addTelegramCommandHandler("addcard", add_card)
#	dp.addTelegramCommandHandler("removecard", remove_card)
#	dp.addTelegramCommandHandler("getcards", get_cards)

	updater.start_polling()

	updater.idle()

if __name__ == '__main__':
	main()