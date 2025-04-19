import telebot
from User import User
token = '7949687658:AAFGH6xu29fIuGOuvh2iMZOXevsWzTcCAqo'

bot = telebot.TeleBot(token)

users = []

base_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
base_markup.add(telebot.types.KeyboardButton('/register'))
base_markup.add(telebot.types.KeyboardButton('/set_chat'))
base_markup.add(telebot.types.KeyboardButton('/swith_name'))

def find_user_by_chatID(chatID):
    for user in users:
        if user.user_chat == chatID:
            return user
    return None
       
def find_user_by_username(username):
    for user in users:
        if user.username == username:
            return user
    return None

@bot.message_handler(commands=['start'])#первое что выведит под после старта
def start_message(message):
    bot.send_message(message.chat.id, 'Привет я бот для отправки анонимных сообщений!')
    bot.send_message(message.chat.id, 'Вот мой список команд:')
    bot.send_message(message.chat.id, '/register- регистрация\n'
                                      '/set_chat - установка чата для сообщений\n'
                                      '/switch_name - смена имени\n', reply_markup=base_markup)
                        

@bot.message_handler(commands=['register'])
def register_user(message):
    user = find_user_by_chatID(message.chat.id)
    if user is None:
        msg = bot.send_message(message.chat.id,'Введите ваше имя')
        bot.register_next_step_handler(msg, create_user, message.chat.id)
    else:
        bot.send_message(message.chat.id, f'Вы уже зарегистрированы, ваше имя:{user.username}')

def create_user(message, chatID):
    if find_user_by_username(message.text) is not None:
        msg = bot.send_message(message.chat.id, 'Такое имя уже используется!, пожалуйста выберите другое!')#проверяем,есть ли такое имя
        bot.register_next_step_handler(msg, create_user, message.chat.id)
        return
    user = User(message.text, chatID, None)
    users.append(user)
    bot.send_message(message.chat.id, "Вы успешно зарегистрировались!")

@bot.message_handler(commands=['switch_name'])
def switch_name(message):#команда для смены имени
    user = find_user_by_chatID(message.chat.id)
    if user is None:
        bot.send_message(message.chat.id, 'Вы еще не зарегистрированы! Команда: /register')#что бы поменять имя, смотрим зарег. ли пользователь
    else:
        msg = bot.send_message(message.chat.id, 'Ваше новое имя')
        bot.register_next_step_handler(msg, name_switch, message.chat.id)
def name_switch(message, chatID):
    if find_user_by_username(message.text) is not None:#проверяем,есть ли такое имя, если да то просим поменять
        msg = bot.send_message(message.chat.id, 'Такое имя уже используется!, пожалуйста выберите другое!')
        bot.register_next_step_handler(msg, name_switch, message.chat.id)
        return
    user = find_user_by_chatID(chatID)#ищем польз.по чату
    user.username = message.text
    bot.send_message(chatID,'Ваше имя изменено')

@bot.message_handler(commands=['set_chat'])
def set_chat(message):
    user = find_user_by_chatID(message.chat.id)
    if user is not None:
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        for user in users:
            markup.add(telebot.types.KeyboardButton(user.username))
        msg = bot.send_message(message.chat.id, 'Выберите чат:', reply_markup=markup)
        bot.register_next_step_handler(msg, set_current_chat, message.chat.id)
    else:
        bot.send_message(message.chat.id, 'Для начала зарегестрируйтесь, команда: /register')

def set_current_chat(message, chatID):
    other_user = find_user_by_username(message.text)
    removeMarkup = telebot.types.ReplyKeyboardRemove()
    if other_user is not None:
        user = find_user_by_chatID(chatID)#ищем польз. в чате 
        user.current_chat = other_user.user_chat# ecли польз. нашел по имени другого польз. то устонавливаем чат а если нет то нет
        bot.send_message(chatID, "Чат успешно установлен!", reply_markup=removeMarkup)
    else:
        bot.send_message(chatID, "Пользователя с таким именем нет!", reply_markup=removeMarkup)

@bot.message_handler(content_types='text')
def text_message(message):
    user = find_user_by_chatID(message.chat.id)
    if user is None:#если пользователя нет то пишем что надо зарег.
        bot.send_message(message.chat.id,'Для начала нужно зарегестрироваться! Команда /register')
        return
    if user.current_chat is None:#есть ли текущий чат,если нет то нужно установить его
        bot.send_message(message.chat.id, ' Для начала нужно установить чат! Команда: /set_chat')
        return
    bot.send_message(user.current_chat, f'Анонимное сообщение: {message.text}')
    bot.send_message(message.chat.id, 'Ваше сообщение доставлено')



bot.infinity_polling()

   




