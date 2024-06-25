import telebot
import sqlite3
import re
from telebot import types
from config import TOKEN

bot = telebot.TeleBot(TOKEN)

name, city, descp, my_gen, profs_gen, tg_ch, vk, tiktok = '', '', '', '', '', '', '', ''
tg_text, vk_text, tiktok_text = '', '', ''
p_sender_id = 0  # Отправитель
p_rec_id = 0  # Получатель
age = 1
user_id = 0
admin_id = 1692853398
mail = ''
photo = None
likes = []


def check_link_tg_ch(link):  # Проверка на формат ссылки telegram
    pattern = r'^https://t.me/[a-zA-Z0-9_]+$'
    if re.match(pattern, link):
        return True
    else:
        return False


def check_link_vk(link):  # Проверка на формат ссылки vk
    pattern = r'^https://vk.com/[a-zA-Z0-9_?=&.\u0026]+$'
    if re.match(pattern, link):
        return True
    else:
        return False


def check_link_tiktok(link):  # Проверка на формат ссылки tiktok
    pattern1 = r'^https://www\.tiktok\.com/@[a-zA-Z0-9_?=&.\u0026]+$'
    pattern2 = r'^tiktok.com/@[a-zA-Z0-9_?=&.\u0026]+$'
    if re.match(pattern1, link) or re.match(pattern2, link):
        return True
    else:
        return False


def check_if_reg(message, pers_id):
    conn = sqlite3.connect('kupid.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id=?", (pers_id,))
    res = cur.fetchone()

    if res:
        bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name}")
        get_data()
        main_menu(message)
        print(f'ID пользователя @{message.from_user.username} существует в таблице')
    else:
        bot.send_message(message.chat.id, "Привет. Сейчас зарегистрируем тебя")
        bot.send_message(message.chat.id, "Введите имя")
        bot.register_next_step_handler(message, user_name)
        print(f'ID пользователя @{message.from_user.username} не существует в таблице')

    conn.commit()
    cur.close()
    conn.close()


def get_prof(us_age, us_city, us_gender, search_gender, us_id):
    conn = sqlite3.connect('kupid.db')
    cur = conn.cursor()

    # Параметры для фильтра по гендеру
    gender_condition = ""
    if us_gender == 'f':
        if search_gender == 'm':
            # Женщина ищет мужчину
            gender_condition = "AND my_gen = 'm' AND (profs_gen = 'f' OR profs_gen = 'b')"
        elif search_gender == 'f':
            # Женщина ищет женщину
            gender_condition = "AND my_gen = 'f' AND (profs_gen = 'f' OR profs_gen = 'b')"
        elif search_gender == 'b':
            # Женщина ищет всех
            gender_condition = "AND (profs_gen = 'f' OR profs_gen = 'b')"
    elif us_gender == 'm':
        if search_gender == 'm':
            # Мужчина ищет мужчину
            gender_condition = "AND my_gen = 'm' AND (profs_gen = 'm' OR profs_gen = 'b')"
        elif search_gender == 'f':
            # Мужчина ищет женщину
            gender_condition = "AND my_gen = 'f' AND (profs_gen = 'm' OR profs_gen = 'b')"
        elif search_gender == 'b':
            # Мужчина ищет всех
            gender_condition = "AND (profs_gen = 'm' OR profs_gen = 'b')"

    # Формирование запроса с учетом условий фильтрации
    query = f""" SELECT * FROM users WHERE city = ? AND age BETWEEN ? AND ? 
                 {gender_condition} AND user_id != ? ORDER BY RANDOM() LIMIT 1 """

    # Выполнение запроса
    cur.execute(query, (us_city, us_age - 1, us_age + 1, us_id))

    profile = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    return profile


def get_data():  # Получения данных пользователя
    global name, age, city, photo, descp, user_id, my_gen, profs_gen, tg_ch, vk, tiktok
    conn = sqlite3.connect('kupid.db')
    cur = conn.cursor()
    cur.execute(f'SELECT name, age, city, photo, descp, my_gen, profs_gen, tg_ch, VK, TikTok'
                f' FROM users WHERE user_id = {user_id}')
    user = cur.fetchall()
    for us in user:
        name, age, city, photo, descp, my_gen, profs_gen, tg_ch, vk, tiktok = us


def get_username(us_id):
    try:
        chat_info = bot.get_chat(us_id)
        return chat_info.username
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None


@bot.message_handler(commands=['start'])  # создание команды /start
def start(message):
    global user_id
    user_id = message.from_user.id

    conn = sqlite3.connect('kupid.db')  # создание файла с таблицами
    cur = conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS users ('
                'user_id int,'
                'name varchar(20),'
                'age int,'
                'city varchar(50),'
                'photo BLOB,'
                'descp varchar(1000),'
                'my_gen varchar(1),'
                'profs_gen varchar(1),'
                'tg_ch varchar(50),'
                'VK varchar(50),'
                'TikTok varchar(50))'
                )
    conn.commit()
    cur.close()
    conn.close()

    pers_id = message.from_user.id

    check_if_reg(message, pers_id)


def user_name(message):
    global name
    name = message.text.strip()
    bot.send_message(message.chat.id, "Введите возраст")
    bot.register_next_step_handler(message, user_age)
    print('Введено имя:', name)


def user_age(message):
    global age
    try:
        age = int(message.text.strip())
    except ValueError:  # обработчик ошибок
        bot.send_message(message.chat.id, "Неверный формат. Попробуйте еще раз")
        bot.register_next_step_handler(message, user_age)
        return
    bot.send_message(message.chat.id, "Введите город")
    bot.register_next_step_handler(message, user_city)
    print('Введен возраст:', age)


def user_city(message):
    global city
    city = message.text.strip()
    bot.send_message(message.chat.id, "Прикрепите фото")
    bot.register_next_step_handler(message, user_photo)
    print('Введен город:', city)


def user_photo(message):
    global photo
    if message.content_type == 'photo':
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        photo = bot.download_file(file_info.file_path)
        conn = sqlite3.connect('kupid.db')
        cur = conn.cursor()
        cur.execute('UPDATE users SET photo = ? WHERE user_id = ?', (photo, user_id))
        conn.commit()
        cur.close()
        conn.close()

        print('Прикреплено фото')
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Мужской', callback_data='my_gen_m'))
        markup.add(types.InlineKeyboardButton('Женский', callback_data='my_gen_f'))
        bot.send_message(message.chat.id, "Твой пол?", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Неправильный формат. Попробуйте еще раз")
        bot.register_next_step_handler(message, user_photo)
        return


def user_descp(message):
    global descp
    descp = message.text.strip()
    print('Введено описание:', descp)
    conn = sqlite3.connect('kupid.db')
    cur = conn.cursor()

    cur.execute('INSERT INTO users (name, age, city, photo, descp, user_id, my_gen, profs_gen) '
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (name, age, city, photo, descp, user_id, my_gen, profs_gen))
    conn.commit()
    cur.close()
    conn.close()

    bot.send_message(message.chat.id, 'Регистрация успешна')
    main_menu(message)


@bot.message_handler(commands=['prof_list'])  # Просмотр всех анкет
def prof_list(message):
    if message.chat.id == admin_id:
        conn = sqlite3.connect('kupid.db')
        cur = conn.cursor()
        cur.execute('SELECT * FROM users')
        users = cur.fetchall()

        info = ''
        for el in users:
            info += f'Имя: {el[1]}, Возраст: {el[2]}, Город: {el[3]}, Описание: {el[5]}, id: {el[0]}\n'

        conn.commit()
        cur.close()
        conn.close()
        bot.send_message(message.chat.id, info)
    else:
        bot.send_message(message.chat.id, 'Ошибка. Нет доступа')


@bot.message_handler(commands=['mailing'])  # Рассылка
def mailing(message):
    global admin_id, mail
    if message.chat.id == admin_id:
        # Получение username бота
        bot_info = bot.get_me()
        bot_username = bot_info.username

        mail_main = message.text.replace('/mailing', '', 1).strip()
        mail = f'{mail_main}\n\n@{bot_username}'
        print(mail_main)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Да', callback_data='mailing_call'))
        markup.add(types.InlineKeyboardButton('Нет', callback_data='back_menu'))
        bot.send_message(admin_id, "Сообщение принято. Отправлять?", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Ошибка. Нет доступа')
        main_menu(message)


@bot.message_handler(commands=['delete_user'])  # Удаление пользователя
def delete_user(message):
    if message.chat.id == admin_id:
        del_user_id = message.text.replace('/mailing', '', 1).strip()
        try:
            del_user_name = get_username(del_user_id)
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Да', callback_data='delete_user'))
            markup.add(types.InlineKeyboardButton('Нет', callback_data='back_menu'))
            bot.send_message(admin_id, f"Вы точно хотите удалить анкету {del_user_name}", reply_markup=markup)
            return del_user_id
        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка отправки пользователю {del_user_id}. Попробуйте ещё раз")
            print(f"Ошибка отправки пользователю {del_user_id}. Ошибка: {e}")
    else:
        bot.send_message(message.chat.id, 'Ошибка. Нет доступа')
        main_menu(message)


@bot.message_handler(commands=['menu'])  # Возвращение в главное меню
def menu(message):
    main_menu(message)


@bot.message_handler(commands=['help'])
def help_command(message):
    bot_info = bot.get_me()
    bot_name = bot_info.first_name
    help_text = (f'Привет {message.from_user.first_name}\nБот {bot_name} предназначен для поиска друзей/отношений\n'
                 f'Вот несколько нужных команд:\n/start - запуск бота\n'
                 f'/menu - возвращение в главное меню\n /help - вызов этого сообщения\n\nУдачных поисков')
    bot.send_message(message.chat.id, help_text)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    global likes, p_sender_id, my_gen, profs_gen, p_rec_id
    if call.data == 'mailing_call':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.delete_message(call.message.chat.id, call.message.message_id - 1)
        conn = sqlite3.connect('kupid.db')
        cur = conn.cursor()
        cur.execute('SELECT user_id FROM users')
        mail_id = cur.fetchall()
        for spam_mail_id in mail_id:
            try:
                bot.send_message(spam_mail_id[0], mail)
            except Exception as e:
                error_user = get_username(spam_mail_id[0])
                bot.answer_callback_query(call.id, f"Ошибка отправки пользователю {error_user}",
                                          show_alert=True)
                print(f"Ошибка отправки пользователю {error_user}. Ошибка: {e}")
        conn.commit()
        cur.close()
        conn.close()
        bot.send_message(admin_id, 'Рассылка успешно завершена')
        main_menu(call.message)

    elif call.data == 'delete_user':
        delete_user_id = delete_user(call.message)
        conn = sqlite3.connect('kupid.db')
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE user_id = ?", (delete_user_id,))
        conn.commit()
        cur.close()
        conn.close()
        bot.send_message(call.message.chat.id, 'Пользователь успешно удален')
        main_menu(call.message)

    elif call.data == 'my_gen_m':
        my_gen = 'm'
        print(f'Гендер: {my_gen}')
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Мужской', callback_data='pass'))
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Девушки', callback_data='profs_gen_f')
        btn2 = types.InlineKeyboardButton('Парни', callback_data='profs_gen_m')
        markup.row(btn1, btn2)
        markup.add(types.InlineKeyboardButton('Все', callback_data='profs_gen_b'))
        bot.send_message(call.message.chat.id, 'Кто тебе интересен?', reply_markup=markup)

    elif call.data == 'my_gen_f':
        my_gen = 'f'
        print(f'Гендер: {my_gen}')
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Женский', callback_data='pass'))
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Девушки', callback_data='profs_gen_f')
        btn2 = types.InlineKeyboardButton('Парни', callback_data='profs_gen_m')
        markup.row(btn1, btn2)
        markup.add(types.InlineKeyboardButton('Все', callback_data='profs_gen_b'))
        bot.send_message(call.message.chat.id, 'Кто тебе интересен?', reply_markup=markup)

    elif call.data == 'profs_gen_f':
        profs_gen = 'f'
        print(f'Гендер анкет: {profs_gen}')
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Девушки', callback_data='pass'))
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
        bot.register_next_step_handler(call.message, user_descp)
        bot.send_message(call.message.chat.id, 'Придумайте описание')

    elif call.data == 'profs_gen_m':
        profs_gen = 'm'
        print(f'Гендер анкет: {profs_gen}')
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Парни', callback_data='pass'))
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
        bot.register_next_step_handler(call.message, user_descp)
        bot.send_message(call.message.chat.id, 'Придумайте описание')

    elif call.data == 'profs_gen_b':
        profs_gen = 'b'
        print(f'Гендер анкет: {profs_gen}')
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Все', callback_data='pass'))
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
        bot.register_next_step_handler(call.message, user_descp)
        bot.send_message(call.message.chat.id, 'Придумайте описание')

    elif call.data == 'see_profs':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        see_profs(call.message)

    elif call.data == 'my_prof':
        get_data()
        text = f'{name}, {age}, {city} - {descp}'
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Изменить', callback_data='edit_prof')
        btn2 = types.InlineKeyboardButton('Удалить анкету', callback_data='off_prof')
        markup.row(btn1, btn2)
        markup.add(types.InlineKeyboardButton('Назад', callback_data='mp_back_menu'))
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Ваша анкета:')
        bot.send_photo(call.message.chat.id, photo, text, reply_markup=markup)

    elif call.data == 'mp_back_menu':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.delete_message(call.message.chat.id, call.message.message_id - 1)
        main_menu(call.message)

    elif call.data == 'back_menu':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        main_menu(call.message)

    elif call.data == 'sp_back_menu':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('➡️', callback_data='pass'))
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
        main_menu(call.message)

    elif call.data == 'like':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('💘', callback_data='pass'))
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
        profile = get_prof(age, city, my_gen, profs_gen, user_id)
        if profile:
            p_rec_id = profile[0]
            try:
                likes.append(user_id)
                print(f'ID лайков: {likes}')
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton('Да', callback_data='see_like'))
                markup.add(types.InlineKeyboardButton('Позже', callback_data='later_see_like'))
                bot.send_message(p_rec_id, 'Кому-то понравилась твоя анкета. Хочешь посмотреть?', reply_markup=markup)
                see_profs(call.message)
            except telebot.apihelper.ApiException:
                print("Ошибка отправки сообщения")
        else:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Вернуться в главное меню'))
            bot.send_message(call.message.chat.id, 'Профиль не найден', reply_markup=markup)
            print("Профиль не найден")

    elif call.data == 'dislike':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('👎', callback_data='pass'))
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=markup)
        see_profs(call.message)

    elif call.data == 'see_like':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Да', callback_data='pass'))
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=markup)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('💘', callback_data='double_like'))
        markup.add(types.InlineKeyboardButton('👎', callback_data='like_dislike'))
        conn = sqlite3.connect('kupid.db')
        cur = conn.cursor()
        for el in likes:
            p_sender_id = el
            likes.pop(0)
            cur.execute(f'SELECT name, age, city, photo, descp FROM users WHERE user_id = {p_sender_id}')
            prof_info = cur.fetchall()

            for us in prof_info:
                p_name, p_age, p_city, p_photo, p_descp = us
                text = f'{p_name}, {p_age}, {p_city} - {p_descp}'
                bot.send_photo(call.message.chat.id, p_photo, text, reply_markup=markup)
        conn.commit()
        cur.close()
        conn.close()

    elif call.data == 'later_see_like':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Позже', callback_data='pass'))
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=markup)
        main_menu(call.message)

    elif call.data == 'double_like':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('💘', callback_data='pass'))
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=markup)
        send_username = get_username(p_sender_id)
        rec_username = get_username(p_rec_id)

        if send_username:
            bot.send_message(p_rec_id, f"У вас взаимная симпатия с @{send_username}")
            print(f"Username отправителя: @{send_username}")
        else:
            bot.send_message(p_rec_id, "Не удалось получить username")
            print("Не удалось получить username отправителя")

        if rec_username:
            bot.send_message(p_sender_id, f"У вас взаимная симпатия с @{rec_username}")
            print(f"Username получателя: @{rec_username}")
        else:
            bot.send_message(p_sender_id, "Не удалось получить username")
            print("Не удалось получить username получателя")

    elif call.data == 'off_prof':
        conn = sqlite3.connect('kupid.db')
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Зарегистрироваться заново', callback_data='reg_again'))
        bot.send_message(call.message.chat.id, 'Анкета успешно удалена', reply_markup=markup)
        # Удаление кнопок
        markup = types.InlineKeyboardMarkup()
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=markup)
        cur.close()
        conn.close()

    elif call.data == 'edit_prof':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Изменить интересы поиска', callback_data='edit_profs_gen'))
        markup.add(types.InlineKeyboardButton('Зарегистрироваться заново', callback_data='reg_again'))
        markup.add(types.InlineKeyboardButton('Главное меню', callback_data='mp_back_menu'))
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=markup)

    elif call.data == 'edit_profs_gen':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.delete_message(call.message.chat.id, call.message.message_id - 1)
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Девушки', callback_data='new_profs_gen_f')
        btn2 = types.InlineKeyboardButton('Парни', callback_data='new_profs_gen_m')
        markup.row(btn1, btn2)
        markup.add(types.InlineKeyboardButton('Все', callback_data='new_profs_gen_b'))
        bot.send_message(call.message.chat.id, "Кто вам интересен?", reply_markup=markup)

    elif call.data == 'new_profs_gen_f':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Девушки', callback_data='new_profs_gen_b'))
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=markup)
        conn = sqlite3.connect('kupid.db')
        cur = conn.cursor()
        new_profs_gen = 'f'
        cur.execute("UPDATE users SET profs_gen = ? WHERE user_id = ?", (new_profs_gen, user_id))
        conn.commit()
        cur.close()
        conn.close()
        bot.send_message(call.message.chat.id, "Интересы поиска обновлены")
        main_menu(call.message)

    elif call.data == 'new_profs_gen_m':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Парни', callback_data='new_profs_gen_b'))
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=markup)
        conn = sqlite3.connect('kupid.db')
        cur = conn.cursor()
        new_profs_gen = 'm'
        cur.execute("UPDATE users SET profs_gen = ? WHERE user_id = ?", (new_profs_gen, user_id))
        conn.commit()
        cur.close()
        conn.close()
        bot.send_message(call.message.chat.id, "Интересы поиска обновлены")
        main_menu(call.message)

    elif call.data == 'new_profs_gen_b':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Все', callback_data='new_profs_gen_b'))
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=markup)
        conn = sqlite3.connect('kupid.db')
        cur = conn.cursor()
        new_profs_gen = 'b'
        cur.execute("UPDATE users SET profs_gen = ? WHERE user_id = ?", (new_profs_gen, user_id))
        conn.commit()
        cur.close()
        conn.close()
        bot.send_message(call.message.chat.id, "Интересы поиска обновлены")
        main_menu(call.message)

    elif call.data == 'reg_again':
        # Удаление кнопки
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Зарегистрироваться заново', callback_data='pass'))
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=markup)
        bot.send_message(call.message.chat.id, "Введите имя")
        bot.register_next_step_handler(call.message, user_name)

    elif call.data == 'bind_soc':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Telegram канал', callback_data='Tg_ch'))
        markup.add(types.InlineKeyboardButton('ВКонтакте', callback_data='VK'))
        markup.add(types.InlineKeyboardButton('TikTok', callback_data='TikTok'))
        btn1 = types.InlineKeyboardButton('Отвязать соцсети', callback_data='off_bind')
        btn2 = types.InlineKeyboardButton('Главное меню', callback_data='back_menu')
        markup.row(btn1, btn2)
        bot.send_message(call.message.chat.id, 'Выберите соцсеть', reply_markup=markup)

    elif call.data == 'off_bind':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Отвязать соцсети', callback_data='pass'))
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=markup)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Telegram канал', callback_data='off_Tg_ch'))
        markup.add(types.InlineKeyboardButton('ВКонтакте', callback_data='off_VK'))
        markup.add(types.InlineKeyboardButton('TikTok', callback_data='off_TikTok'))
        markup.add(types.InlineKeyboardButton('Главное меню', callback_data='back_menu'))
        bot.send_message(call.message.chat.id, 'Выберите соцсеть', reply_markup=markup)

    elif call.data == 'off_Tg_ch':
        conn = sqlite3.connect('kupid.db')
        cur = conn.cursor()
        cur.execute("UPDATE users SET tg_ch = NULL WHERE user_id = ?", (user_id,))
        conn.commit()
        bot.send_message(call.message.chat.id, 'Telegram канал отвязан')
        cur.close()
        conn.close()
        main_menu(call.message)

    elif call.data == 'off_VK':
        conn = sqlite3.connect('kupid.db')
        cur = conn.cursor()
        cur.execute("UPDATE users SET VK = NULL WHERE user_id = ?", (user_id,))
        conn.commit()
        bot.send_message(call.message.chat.id, 'Профиль ВКонтакте отвязан')
        cur.close()
        conn.close()
        main_menu(call.message)

    elif call.data == 'off_Tg_ch':
        conn = sqlite3.connect('kupid.db')
        cur = conn.cursor()
        cur.execute("UPDATE users SET TikTok = NULL WHERE user_id = ?", (user_id,))
        conn.commit()
        bot.send_message(call.message.chat.id, 'Профиль TikTok отвязан')
        cur.close()
        conn.close()
        main_menu(call.message)

    elif call.data == 'Tg_ch':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Telegram канал', callback_data='pass'))
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=markup)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Главное меню', callback_data='mp_back_menu'))
        bot.send_message(call.message.chat.id, 'Пришлите ссылку-приглашение в канал', reply_markup=markup)
        bot.register_next_step_handler(call.message, bind_tg_ch)

    elif call.data == 'VK':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('ВКонтакте', callback_data='pass'))
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=markup)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Главное меню', callback_data='mp_back_menu'))
        bot.send_message(call.message.chat.id, 'Пришлите ссылку на ваш профиль', reply_markup=markup)
        bot.register_next_step_handler(call.message, bind_vk)

    elif call.data == 'TikTok':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('TikTok', callback_data='pass'))
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=markup)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Главное меню', callback_data='mp_back_menu'))
        bot.send_message(call.message.chat.id, 'Пришлите ссылку на ваш профиль', reply_markup=markup)
        bot.register_next_step_handler(call.message, bind_tiktok)


def bind_tg_ch(message):
    global tg_ch
    tg_ch = message.text.strip()
    if message.text.startswith('https://t.me/'):
        if check_link_tg_ch(message.text):
            conn = sqlite3.connect('kupid.db')
            cur = conn.cursor()
            cur.execute('UPDATE users SET tg_ch = ? WHERE user_id = ?', (tg_ch, user_id))
            conn.commit()
            cur.close()
            conn.close()
            bot.send_message(message.chat.id, "Telegram канал привязан")
            main_menu(message)
        else:
            bot.reply_to(message, "Попробуйте другую ссылку")
            bot.send_message(message.chat.id, 'Пришлите ссылку-приглашение в канал')
            bot.register_next_step_handler(message, bind_tg_ch)
    else:
        bot.reply_to(message, "Попробуйте формат https://t.me/...")
        bot.send_message(message.chat.id, 'Пришлите ссылку-приглашение в канал')
        bot.register_next_step_handler(message, bind_tg_ch)


def bind_vk(message):
    global vk
    vk = message.text.strip()
    if message.text.startswith('https://vk.com/'):
        if check_link_vk(message.text):
            conn = sqlite3.connect('kupid.db')
            cur = conn.cursor()
            cur.execute('UPDATE users SET VK = ? WHERE user_id = ?', (vk, user_id))
            conn.commit()
            cur.close()
            conn.close()
            bot.send_message(message.chat.id, "Профиль ВКонтакте привязан")
            main_menu(message)
        else:
            bot.reply_to(message, "Попробуйте другую ссылку")
            bot.send_message(message.chat.id, 'Пришлите ссылку на ваш профиль')
            bot.register_next_step_handler(message, bind_vk)
    else:
        bot.reply_to(message, "Попробуйте формат https://vk.com/...")
        bot.send_message(message.chat.id, 'Пришлите ссылку на ваш профиль')
        bot.register_next_step_handler(message, bind_vk)


def bind_tiktok(message):
    global tiktok
    tiktok = message.text.strip()
    print(tiktok)
    if message.text.startswith('https://www.tiktok.com/') or message.text.startswith('tiktok.com/@'):
        if check_link_tiktok(message.text):
            conn = sqlite3.connect('kupid.db')
            cur = conn.cursor()
            cur.execute('UPDATE users SET TikTok = ? WHERE user_id = ?', (tiktok, user_id))
            conn.commit()
            cur.close()
            conn.close()
            bot.send_message(message.chat.id, "Профиль TikTok привязан")
            main_menu(message)
        else:
            bot.reply_to(message, "Попробуйте другую ссылку")
            bot.send_message(message.chat.id, 'Пришлите ссылку на ваш профиль')
            bot.register_next_step_handler(message, bind_tiktok)
    else:
        bot.reply_to(message, "Попробуйте формат: 'tiktok.com/@'")
        bot.send_message(message.chat.id, 'Пришлите ссылку на ваш профиль')
        bot.register_next_step_handler(message, bind_tiktok)


def see_profs(message):
    global tg_text, vk_text, tiktok_text
    get_data()
    profile = get_prof(age, city, my_gen, profs_gen, user_id)
    if profile:
        if profile[8] is None or profile[9] is None or profile[10] is None:
            if profile[8] is None:
                tg_text = 'Не привязан'
            else:
                tg_text = f'<a href="{profile[8]}">Ссылка на канал</a>'
            if profile[9] is None:
                vk_text = 'Не привязан'
            else:
                vk_text = f'<a href="{profile[9]}">Ссылка на профиль ВК</a>'
            if profile[10] is None:
                tiktok_text = 'Не привязан'
            else:
                tiktok_text = f'<a href="{profile[10]}">Ссылка на профиль TikTok</a>'
            text = (f"{profile[1]}, {profile[2]}, {profile[3]} - {profile[5]}\n\nПривязанные соцсети:\n"
                    f"Telegram канал: {tg_text}\nВКонтакте: {vk_text}\nTikTok: {tiktok_text}")
        else:
            text = f"{profile[1]}, {profile[2]}, {profile[3]} - {profile[5]}"
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('💘', callback_data='like')
        btn2 = types.InlineKeyboardButton('👎', callback_data='dislike')
        markup.row(btn1, btn2)
        markup.add(types.InlineKeyboardButton('➡️', callback_data='sp_back_menu'))
        bot.send_photo(message.chat.id, profile[4], text, reply_markup=markup, parse_mode='HTML')
        print(f'Нашлась анкета {text}')
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Главное меню', callback_data='back_menu'))
        bot.send_message(message.chat.id, "Анкеты не найдены", reply_markup=markup)


def main_menu(message):
    global user_id
    user_id = message.chat.id
    get_data()
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Смотреть анкеты', callback_data='see_profs'))
    markup.add(types.InlineKeyboardButton('Моя анкета', callback_data='my_prof'))
    markup.add(types.InlineKeyboardButton('Привязка соцсетей', callback_data='bind_soc'))
    bot.send_message(message.chat.id, 'Выберите действие', reply_markup=markup)


bot.infinity_polling()
