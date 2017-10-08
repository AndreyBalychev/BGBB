import urllib2
import json
import logging

CARD_TYPE_ID = '3ae427a1-0f17-4524-acb1-a3f50090a8f3'
URL = 'http://strelkacard.ru/api/cards/status/'

TEST_NUMBER = '03310208398'

logging.basicConfig(
	format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
	level = logging.INFO)
#	filename = u'checker.log')
logger = logging.getLogger(__name__)

def get_params(params):
	params_string = ''
	for key in params.keys():
		if len(params_string) == 0:
			params_string += '?'
		else:
			params_string += '&'
		params_string += key + '=' + params[key]
	return params_string

def get_request(card_number):
	params = {
		'cardtypeid': CARD_TYPE_ID,
		'cardnum': card_number
	}
	params_string = get_params(params)
	result = URL + params_string
	return result

def get_status(card_number):
	logger.info("Request data for card %s" % (card_number))
	url = get_request(card_number)
	logger.info("Request to URL %s" % (url))
	f = urllib2.urlopen(url)
	code = f.getcode()
	logger.info("Return code %d" % (code))
	text = f.read()
	logger.info("Get info for card %s: %d %s" % (card_number, code, text))
	if code == 200:
		return text
	raise ValueError("Can't get info about card with number %s" % card_number)

def get_balance(card_number):
	status = get_status(card_number)
	values = json.loads(status)
	return values['balance'] / 100.0
