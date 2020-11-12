from enum import Enum
import telebot
import logging
import queue

class States(Enum):
    """
    Мы используем словарь, в которой храним всегда строковые данные,
    поэтому и тут будем использовать тоже строки (str)
    """
    S_START = "0"  # Начало нового диалога
    S_SET_WEBSITE = '1'
    S_OZON_AUDIT = "2"
    S_WB_AUDIT = "3"
    S_BRAND_AUDIT = "4"
    S_COMPLEX_AUDIT = "5"
    S_BRAND_LINK_AUDIT = "6"
    S_CHOOSE_BRAND_OZON = "7"
    S_CHOOSE_BRAND_WB = "8"
    S_CHOOSE_BRAND_GOODS = "9"
    S_GOODS_AUDIT = "10"

def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')

# first file logger
logger = setup_logger('logger', 'bot_logfile.log')
logger.info('This is just info message')

# second file logger
error_logger = setup_logger('error_logger', 'error_logfile.log')
error_logger.error('This is an error message')


header = {'User-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:79.0)' + \
                                ' Gecko/20100101 Firefox/79.0',
                  # Создаем заголовок, чтобы сайты не воспринимали нас как бота
                  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                  'Accept-language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3'}
cookies = dict(cookies_are='session=4b082e00-074c-75f7-4761-4fb12bbb343b; __utma=12798129.510440631.1596800516.'
                                   '1596800516.1596800516.1; __utmc=12798129;' + \
                                   ' __utmz=12798129.1596800516.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|' + \
                                   'utmctr=(not%20provided); __gads=ID=19506182921d16b7:T=1596800516:S=ALNI' + \
                                   '_MY-XwLcuZvDvxMnb7lEx3kAG7ideQ; __qca=P0-23977826-1596800516655;' + \
                                   ' _ga=GA1.2.1387315142.1596800524; _gid=GA1.2.525403005.1596800524')
soup_type = 'lxml'

telegram_bot = telebot.TeleBot('1353557120:AAGG4wYEsW0E0riTI4PjfbF_MCJKVEKLQ78')

keyboard = telebot.types.ReplyKeyboardMarkup(True,one_time_keyboard=True)
keyboard.row('Ozon','Wildberries','Goods')

keyboard1 = telebot.types.ReplyKeyboardMarkup(True,one_time_keyboard=True)
keyboard1.row('Указать другой бренд','Комплексный аудит')

keyboard2 = telebot.types.ReplyKeyboardMarkup(True,one_time_keyboard=True)
keyboard2.row('Указать бренд')
keyboard2.row('Указать ссылку на страницу бренда')

keyboard_q = telebot.types.ReplyKeyboardMarkup(True,one_time_keyboard=True)
keyboard_q.row('Да','Нет, идем в начало')

state = {}
q = queue.Queue()