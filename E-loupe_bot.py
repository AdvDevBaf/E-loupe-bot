from Settings import *
from sites import OzonSite, WildBerriesSite, GoodsSite
import threading

bot = telegram_bot

audit_data = {}

def get_current_state(user_id):
    try:
        return state[user_id]
    except KeyError as ex:  # Если такого ключа почему-то не оказалось
        error_logger.error(ex.args[0])
        return States.S_START.value


@bot.message_handler(func=lambda message: get_current_state(message.chat.id) == States.S_START.value)
@bot.message_handler(commands=['start'])
def start_message(message):
    if message.text.lower() == 'ozon':
        #audit_data['marketplace'] = str(message.text).lower()
        audit_data[str(message.chat.id)] = {'id': message.chat.id, 'marketplace': str(message.text).lower(),
                                    'brand': ''}
        bot.send_message(message.chat.id, 'Укажите название бренда или ссылку на страницу бренда',
                         reply_markup=keyboard2)
        state[message.chat.id] = States.S_CHOOSE_BRAND_OZON.value
    elif message.text.lower() == 'wildberries':
        audit_data[str(message.chat.id)] = {'id': message.chat.id, 'marketplace': str(message.text).lower(),
                                    'brand': ''}
        bot.send_message(message.chat.id, 'Укажите название бренда или ссылку на страницу бренда',
                         reply_markup=keyboard2)
        state[message.chat.id] = States.S_CHOOSE_BRAND_WB.value
    elif message.text.lower() == 'goods':
        audit_data[str(message.chat.id)] = {'id': message.chat.id, 'marketplace': str(message.text).lower(),
                                            'brand': ''}
        bot.send_message(message.chat.id,'Укажите название бренда или ссылку на страницу бренда',
                         reply_markup=keyboard2)
        state[message.chat.id] = States.S_CHOOSE_BRAND_GOODS.value
    else:
        state[message.chat.id] = States.S_START.value
        bot.send_message(message.chat.id, 'Выбери или напиши маркетплейс', reply_markup=keyboard)

@bot.message_handler(func=lambda message: get_current_state(message.chat.id) == States.S_CHOOSE_BRAND_WB.value)
def choose_brand_wb(message):
    if message.text == 'Указать бренд':
        bot.send_message(message.chat.id, 'Укажи название бренда на вб')
        state[message.chat.id] = States.S_WB_AUDIT.value
    elif message.text == 'Указать ссылку на страницу бренда':
        bot.send_message(message.chat.id, 'Укажите ссылку на страницу бренда')
        state[message.chat.id] = States.S_BRAND_LINK_AUDIT.value
    else:
        bot.send_message(message.chat.id, 'Укажите название бренда или ссылку на страницу бренда',
                         reply_markup=keyboard2)

@bot.message_handler(func=lambda message: get_current_state(message.chat.id) == States.S_CHOOSE_BRAND_OZON.value)
def choose_brand_ozon(message):
    if message.text == 'Указать бренд':
        bot.send_message(message.chat.id, 'Укажи название бренда на озон')
        state[message.chat.id] = States.S_OZON_AUDIT.value
    elif message.text == 'Указать ссылку на страницу бренда':
        bot.send_message(message.chat.id, 'Укажите ссылку на страницу бренда')
        state[message.chat.id] = States.S_BRAND_LINK_AUDIT.value
    else:
        bot.send_message(message.chat.id, 'Укажите название бренда или ссылку на страницу бренда',
                         reply_markup=keyboard2)

@bot.message_handler(func=lambda message: get_current_state(message.chat.id) == States.S_CHOOSE_BRAND_GOODS.value)
def choose_brand_goods(message):
    if message.text == 'Указать бренд':
        bot.send_message(message.chat.id, 'Укажи название бренда на goods')
        state[message.chat.id] = States.S_GOODS_AUDIT.value
    elif message.text == 'Указать ссылку на страницу бренда':
        bot.send_message(message.chat.id, 'Укажите ссылку на страницу бренда')
        state[message.chat.id] = States.S_BRAND_LINK_AUDIT.value
    else:
        bot.send_message(message.chat.id, 'Укажите название бренда или ссылку на страницу бренда',
                         reply_markup=keyboard2)



@bot.message_handler(commands=['reset'])
def set_reset(message):
    state[message.chat.id] = States.S_START.value
    bot.send_message(message.chat.id, 'OK', reply_markup=keyboard)


@bot.message_handler(commands=['help'])
def get_help(message):
    c = ('/start' ,'/help', '/reset')
    bot.send_message(message.chat.id,'Список команд: \n'
                                     '' + str(c[0]) + ' - Запуск бота/Начать работу с ботом\n'
                                     '' + str(c[2]) + ' - Запросить список команд\n'
                                     '' + str(c[3]) + ' - Сброс к началу диалога\n',reply_markup=keyboard)

@bot.message_handler(func=lambda message: get_current_state(message.chat.id) == States.S_OZON_AUDIT.value)
def set_brand(message):
    logger.info(message.text.lower())
    audit_data[str(message.chat.id)]['brand'] = str(message.text).lower()
    logging.info('Marketplace: ' + audit_data[str(message.chat.id)]['marketplace'] +
                 ', Brand: ' + audit_data[str(message.chat.id)]['brand'])
    bot.send_message(message.chat.id, 'Marketplace: ' +audit_data[str(message.chat.id)]['marketplace']+
                     ', Brand: ' + audit_data[str(message.chat.id)]['brand'])
    logger.info(audit_data)

    q.put(message.chat.id)

    state[message.chat.id] = States.S_BRAND_AUDIT.value
    bot.send_message(message.chat.id, 'Начать аудит?', reply_markup=keyboard_q)

@bot.message_handler(func=lambda message: get_current_state(message.chat.id) == States.S_WB_AUDIT.value)
def set_brand(message):
    #audit_data['brand'] = str(message.text).lower()
    audit_data[str(message.chat.id)]['brand'] = str(message.text).lower()
    logging.info('Marketplace: ' + audit_data[str(message.chat.id)]['marketplace'] +
                 ', Brand: ' + audit_data[str(message.chat.id)]['brand'])
    bot.send_message(message.chat.id, 'Marketplace: ' + audit_data[str(message.chat.id)]['marketplace'] +
                     ', Brand: ' + audit_data[str(message.chat.id)]['brand'])
    logger.info(audit_data)
    q.put(message.chat.id)
    state[message.chat.id] = States.S_BRAND_AUDIT.value
    bot.send_message(message.chat.id, 'Начать аудит?',reply_markup=keyboard_q)


@bot.message_handler(func=lambda message: get_current_state(message.chat.id) == States.S_GOODS_AUDIT.value)
def set_brand(message):
    audit_data[str(message.chat.id)]['brand'] = str(message.text).lower()
    logging.info('Marketplace: ' + audit_data[str(message.chat.id)]['marketplace'] +
                 ', Brand: ' + audit_data[str(message.chat.id)]['brand'])
    bot.send_message(message.chat.id, 'Marketplace: ' + audit_data[str(message.chat.id)]['marketplace'] +
                     ', Brand: ' + audit_data[str(message.chat.id)]['brand'])
    logger.info(audit_data)
    q.put(message.chat.id)
    state[message.chat.id] = States.S_BRAND_AUDIT.value
    bot.send_message(message.chat.id, 'Начать аудит?',reply_markup=keyboard_q)


@bot.message_handler(func=lambda message: get_current_state(message.chat.id) == States.S_BRAND_LINK_AUDIT.value)
def set_brand_link(message):
    if 'brand' or 'category' in message.text.lower():
        audit_data[str(message.chat.id)]['brand'] = str(message.text).lower()
        logging.info('Marketplace: ' + audit_data[str(message.chat.id)]['marketplace'] +
                     ', Brand: ' + audit_data[str(message.chat.id)]['brand'])
        bot.send_message(message.chat.id, 'Marketplace: ' + audit_data[str(message.chat.id)]['marketplace'] +
                         ', Brand: ' + audit_data[str(message.chat.id)]['brand'])
        logger.info(audit_data)
        q.put(message.chat.id)
        state[message.chat.id] = States.S_BRAND_AUDIT.value
        bot.send_message(message.chat.id, 'Начать аудит?', reply_markup=keyboard_q)
    else:
        bot.send_message(message.chat.id, 'Укажите ссылку на страницу бренда')

def worker(message):
    bot.send_message(message.chat.id, 'Аудит запущен ⏳')
    send = bot.send_message(message.chat.id, 'Идет обработка: парсим ссылки')
    item = q.get()
    if audit_data[str(message.chat.id)]['marketplace'] == 'ozon':
        f = OzonSite().start(audit_data, item, send.message_id)
    elif audit_data[str(message.chat.id)]['marketplace'] == 'wildberries':
        f = WildBerriesSite().start(audit_data, item, send.message_id)
    else:
        f = GoodsSite().start(audit_data, item, send.message_id)
    q.task_done()
    if f:
        telegram_bot.edit_message_text('Готово', message.chat.id, send.message_id)
        bot.send_document(message.chat.id, open('e-loupe.xlsx', "rb"))
        bot.send_message(message.chat.id, 'Продолжим работу?', reply_markup=keyboard1)
        state[message.chat.id] = States.S_COMPLEX_AUDIT.value


@bot.message_handler(func=lambda message: get_current_state(message.chat.id) == States.S_BRAND_AUDIT.value)
def audit(message):
    if message.text.lower() == 'да':
        threading.Thread(target=worker,name='test', args=(message,),daemon=True).start()
    elif message.text.lower() == 'нет, идем в начало':
        state[message.chat.id] = States.S_START.value
        bot.send_message(message.chat.id, 'Выбери или напиши маркетплейс', reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, 'Начать аудит?', reply_markup=keyboard_q)


'''
#@bot.message_handler(func=lambda message: get_current_state(message.chat.id) == States.S_BRAND_AUDIT.value)
def audit(message):
    bot.send_message(message.chat.id, 'Аудит запущен ⏳')
    send = bot.send_message(message.chat.id, 'Идет обработка: парсим ссылки')
    if fd[str(message.chat.id)]['marketplace'] == 'ozon':
        f = OzonSite().start(fd, message.chat.id, send.message_id)
    else:
        f = WildBerriesSite().start(fd, message.chat.id, send.message_id)
    if f:
        telegram_bot.edit_message_text('Готово', message.chat.id, send.message_id)
        bot.send_document(message.chat.id,open('e-loupe.xlsx',"rb"))
        bot.send_message(message.chat.id, 'Продолжим работу?', reply_markup=keyboard1)
        state[message.chat.id] = States.S_COMPLEX_AUDIT.value
    else:
        bot.send_message(message.chat.id, 'Пока тут пусто')
'''
@bot.message_handler(func=lambda message: get_current_state(message.chat.id) == States.S_COMPLEX_AUDIT.value)
def final(message):
    if message.text.lower() == 'указать другой бренд':
        state[message.chat.id] = States.S_START.value
        bot.send_message(message.chat.id, 'OK', reply_markup=keyboard)
    elif message.text.lower() == 'комплексный аудит':
        bot.send_message(message.chat.id,'Комплексный e-commerce аудит вы можете заказать в performance агентстве Reprise ⚡'
                                         '\nreprisedigital.ru'
                                         '\nmoscow@reprisedigital.ru')

@bot.message_handler(content_types=['text'])
def send_text(message):
        bot.send_message(message.chat.id, 'Прости, я тебя не понимаю. Отправь мне /help, если тебе требуется помощь')

bot.polling()