import telebot, json, re
import bd_connector as sqlc

sqlC = sqlc.Connector()
last_message = {}
bot = telebot.TeleBot(json.load(open('config.json'))['release_token'])

@bot.message_handler(commands=['start'])
def start(message):
    bot.delete_message(message.chat.id,message.message_id)
    sqlC.add_new_user(message.chat.id)
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    if sqlC.check_acces(message.chat.id):
        markup.add(telebot.types.KeyboardButton('Меню'))
        msg_text = 'Вы можете добавлять и проверять бонусы'
    else:
        msg_text = f'Обратитесь к Иваненко Даниилу и сбросьте {message.chat.id}'
    bot.send_message(message.chat.id, msg_text, reply_markup= markup)
    
@bot.callback_query_handler(func= lambda callback: True)
def callback_message(callback):
    match callback.data.split('/'):
        case ['1']                                      : menu(callback.message)
        case ['2']                                      : add_bonus_write_info(callback.message)
        case ['3']                                      : show_bonus_write_code(callback.message)
        #case ['4']                                      : show_bonuses_choos_project(callback.message)
        #case ['5', project]                             : show_bonuses_from_project(callback.message, project)
        case ['6']                                      : add_acces_write_tg(callback.message)

@bot.message_handler(content_types=["text"])
def controller(message):
    match message.text.lower().split():
        case ['меню']   : menu(message) if sqlC.check_acces(message.chat.id) else 0
        case _          : bot.delete_message(message.chat.id,message.message_id)
    
def menu(message):
    bot.delete_message(message.chat.id, message.message_id)
    rep_markup = telebot.types.InlineKeyboardMarkup()
    if sqlC.check_acces(message.chat.id):
        rep_markup.add(telebot.types.InlineKeyboardButton('Добавить бонус',callback_data= '2'))
        rep_markup.add(telebot.types.InlineKeyboardButton('Найти бонус',callback_data= '3'))
    if message.chat.id == 943464965:
        rep_markup.add(telebot.types.InlineKeyboardButton('Предоставить доступ',callback_data= '6'))
    msg = bot.send_message(message.chat.id, 'Меню', reply_markup= rep_markup)
    last_message[message.chat.id] = msg.message_id
    
def add_bonus_write_info(message):
    msg_text = 'Укажите информацию из слака.'
    bot.delete_message(message.chat.id,last_message[message.chat.id])
    msg = bot.send_message(message.chat.id, msg_text)
    bot.register_next_step_handler(msg, add_bonus)

def add_bonus(message):
    text = message.text.split('\n')
    for pos in range(0, len(text)):
        line = text[pos]
        match pos:
            case 0  : 
                try:
                    project = line.split(':')[2]
                except:
                    project = line
                pos += 1
            case 2  :
                try:
                    dates = re.findall(r'\d{2}.\d{2}.\d{4}',line)
                    date_start = dates[0]
                    date_end   = dates[1]
                except:
                    date_end = '0'+re.search(r'\d{1}.\d{2}.\d{4}',line)

            case 3  :
                max_win = line.split(': ')[-1:][0]
            case 4  :
                wager = line.split(': ')[-1:][0]
            case 5 | 10 :
                code = line.split(': ')[-1:][0]
            case 6 | 11 :
                need_info = line.split(': ')[-1:][0].split(' (')
                game = need_info[0]
                provider = need_info[1][:-1]
            case 7 | 12 :
                need_info = line.split(':  ')[-1:][0].split(', ')
                price_RUB = need_info[0].replace(' ', '').replace('RUB', '')
                price_KZT = need_info[1].replace(' ', '').replace('KZT', '')
                price_UAH = need_info[2].replace(' ', '').replace('UAH', '')
            case 8 | 13 :
                need_info = line.split(': ')[1:]
                count_spin = need_info[0][:2]
                need_info = need_info[1].split(', ')
                price_spin_RUB = need_info[0].replace(' ', '').replace('RUB', '')
                price_spin_KZT = need_info[1].replace(' ', '').replace('KZT', '')
                price_spin_UAH = need_info[2].replace(' ', '').replace('UAH', '')
            case 9 | 14 :
                code_back = line.split(': ')[-1:][0]
                msg_RUB = f'Вы можете воспользоваться промокодом {code} при внесении депозита от {price_RUB} рублей, вам будет доступно {count_spin} фриспинов по ставке {price_spin_RUB} рублей в игре {game} от провайдера {provider}. Максимальный выигрыш по промокоду {max_win}, вейджер составит x{wager}.'
                msg_KZT = f'Вы можете воспользоваться промокодом {code} при внесении депозита от {price_KZT} тенге, вам будет доступно {count_spin} фриспинов по ставке {price_spin_KZT} тенге в игре {game} от провайдера {provider}. Максимальный выигрыш по промокоду {max_win}, вейджер составит x{wager}.'
                msg_UAH = f'Вы можете воспользоваться промокодом {code} при внесении депозита от {price_UAH} гривен, вам будет доступно {count_spin} фриспинов по ставке {price_spin_UAH} гривен в игре {game} от провайдера {provider}. Максимальный выигрыш по промокоду {max_win}, вейджер составит x{wager}.'
                if sqlC.insert_bonus_info(code, project, wager, max_win, game, provider, price_RUB, price_KZT, price_UAH, count_spin, price_spin_RUB, price_spin_KZT, price_spin_UAH, date_start, date_end, code_back):
                    bot.send_message(message.chat.id,msg_RUB)
                    bot.send_message(message.chat.id,msg_KZT)
                    bot.send_message(message.chat.id,msg_UAH)

def show_bonus_write_code(message):
    msg_text = 'Введите промокод.'
    bot.delete_message(message.chat.id,last_message[message.chat.id])
    msg = bot.send_message(message.chat.id, msg_text)
    bot.register_next_step_handler(msg, show_bonus)

def show_bonus(message):
    code = message.text
    need_info = sqlC.get_bonus_info(code)
    msg_info = f'Проект: {need_info[0]}\nПериод активации: с {need_info[8]} по {need_info[9]}\nВ бэке: {need_info[10]}'
    bot.send_message(message.chat.id, msg_info)
    bot.send_message(message.chat.id, 'RUB')
    msg_RUB = f'Вы можете воспользоваться промокодом {code} при внесении депозита от {need_info[5]} рублей, вам будет доступно {need_info[6]} фриспинов по ставке {need_info[7]} рублей в игре {need_info[3]} от провайдера {need_info[4]}. Максимальный выигрыш по промокоду {need_info[2]}, вейджер составит x{need_info[1]}.'
    bot.send_message(message.chat.id, msg_RUB)
    need_info = sqlC.get_bonus_info(code,'KZT')
    bot.send_message(message.chat.id, 'KZT')
    msg_KZT = f'Вы можете воспользоваться промокодом {code} при внесении депозита от {need_info[5]} тенге, вам будет доступно {need_info[6]} фриспинов по ставке {need_info[7]} тенге в игре {need_info[3]} от провайдера {need_info[4]}. Максимальный выигрыш по промокоду {need_info[2]}, вейджер составит x{need_info[1]}.'
    bot.send_message(message.chat.id, msg_KZT)
    need_info = sqlC.get_bonus_info(code,'UAH')
    bot.send_message(message.chat.id, 'UAH')
    msg_UAH = f'Вы можете воспользоваться промокодом {code} при внесении депозита от {need_info[5]} гривен, вам будет доступно {need_info[6]} фриспинов по ставке {need_info[7]} гривен в игре {need_info[3]} от провайдера {need_info[4]}. Максимальный выигрыш по промокоду {need_info[2]}, вейджер составит x{need_info[1]}.'
    bot.send_message(message.chat.id, msg_UAH)

def add_acces_write_tg(message):
    msg_text = 'Укажите код, предоставленный сотрудником'
    bot.delete_message(message.chat.id,last_message[message.chat.id])
    msg = bot.send_message(message.chat.id, msg_text)
    bot.register_next_step_handler(msg, add_acces)

def add_acces(message):
    telegram = message.text
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    if sqlC.add_acces_to_user(telegram):
        markup.add(telebot.types.KeyboardButton('Меню'))
        msg_new = 'Вы может использовать бота'
        msg_old = 'Сотрудник может использовать бота'
    else:
        msg_new = 'Вы не можете использовать бота'
        msg_old = 'Сотрудник не может использовать бота'
    bot.send_message(message.chat.id,msg_old)
    bot.send_message(telegram,msg_new,reply_markup= markup)

bot.infinity_polling()