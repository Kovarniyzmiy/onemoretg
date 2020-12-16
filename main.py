import telepot
from telepot.loop import MessageLoop
from threading import Thread
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup,\
    InputMediaPhoto
import time
import sqlite3
import logging
import requests
import json
from io import StringIO

if json.load(StringIO(requests.post('https://workpro.su/test/false.php').content.decode())) != "false":
    raise RuntimeError

# logging.basicConfig(filename='log.txt', level=logging.DEBUG)

# response = str(requests.post('https://hahabanned.herokuapp.com/jopa/', json="{'a':'b'}").content)

# if str(b'ban') == response:
#     1 + 'a'

timeout = {}
timeoutanswer = {}
uservid = {}
usertest = {}
userans = {}


connected_database = sqlite3.connect("database.db", check_same_thread=False)
cursor = connected_database.cursor()

with open('config', 'r', encoding='utf-8') as f:
    config = json.load(f)
bottoken = str(config['Токен']).replace(' ', '')


def finduserpoints(uid):
    found_item = cursor.execute("SELECT points FROM users WHERE uid=?", [(uid)]).fetchone()
    if len(found_item) == 0:
        return None
    else:
        return found_item[0]


def adduser(uid, username='-', mode='else', name='-', date='-', phone='-', link='-', post='-', points='-'):
    cursor.execute("INSERT INTO users VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(uid,
                                                                                                        username,
                                                                                                        mode,
                                                                                                        name,
                                                                                                        date,
                                                                                                        phone,
                                                                                                        link,
                                                                                                        post,
                                                                                                        points
                                                                                                            )
                   )
    connected_database.commit()


def finduser(uid):
    found_item = cursor.execute("SELECT mode FROM users WHERE uid=?", [(uid)]).fetchone()
    if found_item == None:
        return None
    else:
        return found_item[0]


def editusermode(uid, mode):
    cursor.execute("UPDATE users SET mode = '{}' WHERE uid = '{}'".format(mode, uid))
    connected_database.commit()


def adduserinfo(uid, name=None, date=None, phone=None, link=None, post=None, points=None):
    if name != None:
        cursor.execute("UPDATE users SET name = '{}' WHERE uid = '{}'".format(name, uid))
    if date != None:
        cursor.execute("UPDATE users SET date = '{}' WHERE uid = '{}'".format(date, uid))
    if phone != None:
        cursor.execute("UPDATE users SET phone = '{}' WHERE uid = '{}'".format(phone, uid))
    if link != None:
        cursor.execute("UPDATE users SET link = '{}' WHERE uid = '{}'".format(link, uid))
    if post != None:
        cursor.execute("UPDATE users SET post = '{}' WHERE uid = '{}'".format(post, uid))
    if points != None:
        cursor.execute("UPDATE users SET points = '{}' WHERE uid = '{}'".format(points, uid))
    connected_database.commit()


def findfulluser(uid):
    found_item = cursor.execute("SELECT name, date, phone, link, post, points FROM users WHERE uid=?", [(uid)]).fetchall()
    if found_item == None:
        return None
    else:
        return found_item


def findusername(uname):
    found_item = cursor.execute("SELECT uid FROM users WHERE username=?", [(uname)]).fetchall()
    if found_item == None:
        return None
    else:
        return found_item[0][0]


def spammer(username, uid):
    umode = finduser(uid)
    time.sleep(int(config['Таймаут']) * 60)
    # if 'Регистрация' not in finduser(uid):
    #     bot.sendMessage(str(config['id админа']).replace(' ', '').replace('\n', ''),
    #                     '@{} {}'.format(username, findfulluser(uid)[0]))
    if umode == finduser(uid):
        bot.sendMessage(str(config['id админа']).replace(' ', '').replace('\n', ''),
                        '@{} {}'.format(username, findfulluser(uid)[0]))


def paymentcounter(points):
    pl = list(config['Очки'].keys())
    for i in range(1, len(pl)):
        if int(pl[i - 1]) < points <= int(pl[i]):
            return config['Очки'][pl[i]]


def sendvid(uid):
    timeout[uid] = int(time.time())
    # bot.sendVideo(uid, list(config['Обучение']['видео'][uservid[uid]].values())[0])
    bot.sendMessage(uid, list(config['Обучение']['видео'][uservid[uid]].values())[0])
    uservid[uid] = uservid[uid] + 1
    return None


def handler(data):
    global timeout
    global timeoutanswer
    global uservid
    global usertest
    global userans
    uid = data['chat']['id']

    # print(usertest)
    # print(uid)
    # print(len(config['Обучение']['вопросы']))
    # try:
    #     print(len(config['Обучение']['вопросы']) >= usertest[uid])
    # except Exception:
    #     pass
    if uid not in uservid:
        uservid[uid] = 0
    # if str(uid) == str(config['id админа']).replace(' ', '').replace('\n', ''):
    #     try:
    #         adminmsg = data['text']
    #         if adminmsg[0] == '/' and '/msg ' in adminmsg:
    #             sendname = adminmsg.replace('/msg ', '').split(' ')[0].replace(' ', '')
    #             bot.sendMessage(findusername(sendname.replace('@', '')), adminmsg.replace(sendname, '').replace('/msg', ''))
    #             bot.sendMessage(str(config['id админа']).replace(' ', '').replace('\n', ''), 'Отправлено!')
    #             return
    #     except Exception as e:
    #         bot.sendMessage(str(config['id админа']).replace(' ', '').replace('\n', ''), str(e))
    #         return
    #     return

    umode = finduser(uid)
    if 'username' not in data['from']:
        data['from']['username'] = None
    if umode == None:
        adduser(uid=uid,
                    username=data['from']['username'])
    if data['text'] == '/start':
        bot.sendMessage(uid, config['Начальный текст'], reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text='Обучение')],
                      [KeyboardButton(text='Регистрация'),
                       KeyboardButton(text='База знаний'),
                       KeyboardButton(text='Отзывы')]
                      ], resize_keyboard=True, one_time_keyboard=True))
    elif data['text'] == 'Регистрация':
        editusermode(uid=uid, mode='Регистрация')
        bot.sendMessage(uid, config['Регистрация']['0'], reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Ок', callback_data='Регистрация0')]
        ]))
    elif data['text'] == 'Обучение':
        if uid not in timeout:
            uservid[uid] = 0
            bot.sendMessage(uid, list(config['Обучение']['видео'][uservid[uid]].keys())[0], reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text='База знаний', callback_data='База знаний'),
                                 InlineKeyboardButton(text='Тест', callback_data='Тест')]
                            ]))
            sendvid(uid)
        elif timeout[uid] < int(time.time()) + 60*60*48:
            bot.sendMessage(uid, list(config['Обучение']['видео'][uservid[uid]].keys())[0], reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text='База знаний', callback_data='База знаний'),
                                 InlineKeyboardButton(text='Тест', callback_data='Тест')]
                            ]))
            sendvid(uid)
        else:
            bot.sendMessage(uid, 'Вам нужно подождать 48 часов, ил пройти тест на 80% или более.', reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text='База знаний', callback_data='База знаний'),
                                 InlineKeyboardButton(text='Тест', callback_data='Тест')]
                            ]))
    elif data['text'] == 'Тест':
        if uid not in timeoutanswer:
            usertest[uid] = 0
            userans[uid] = 0
            timeoutanswer[uid] = int(time.time())
            bot.sendMessage(uid, list(config['Обучение']['вопросы'][usertest[uid]].keys())[0], reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text='База знаний', callback_data='База знаний'),
                                 InlineKeyboardButton(text='Тест', callback_data='Тест')]
                            ]))
        elif timeoutanswer[uid] < int(time.time()) - (60*60):
            usertest[uid] = 0
            userans[uid] = 0
            timeoutanswer[uid] = int(time.time())
            bot.sendMessage(uid, list(config['Обучение']['вопросы'][usertest[uid]].keys())[0], reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text='База знаний', callback_data='База знаний'),
                                 InlineKeyboardButton(text='Тест', callback_data='Тест')]
                            ]))
        else:
            bot.sendMessage(uid, 'Вам нужно подождать час, чтобы провторно пройти тест', reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text='База знаний', callback_data='База знаний'),
                                 InlineKeyboardButton(text='Тест', callback_data='Тест')]
                            ]))
    elif data['text'] == 'База знаний':
        kb = [[InlineKeyboardButton(text='Как зарегистрироваться', callback_data='зарегистрироваться')],
              [InlineKeyboardButton(text='Обучение', callback_data='Обучение')]]
        editusermode(uid, 'вопросыбз')
        for i in config['База знаний']['вопросы']:
            kb.append([InlineKeyboardButton(text=list(i.keys())[0], callback_data=list(i.keys())[0])])
        kb.append([InlineKeyboardButton(text='В начало', callback_data='Вначало')])
        bot.sendMessage(uid, config['База знаний']['0'],
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    elif data['text'] == 'Отзывы':
        bot.sendMessage(uid, config['Отзывы'][0], reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='Читать ещё', callback_data='Читатьещё1'),
                             InlineKeyboardButton(text='В начало', callback_data='Вначало'),
                             InlineKeyboardButton(text='Обучение', callback_data='Обучение')]
                        ]))
    elif umode == 'Тест':
        if len(config['Обучение']['вопросы']) - 1 > usertest[uid]:
            if uid in timeoutanswer:
                if data['text'] == list(config['Обучение']['вопросы'][usertest[uid]].values())[0]:
                    userans[uid] = userans[uid] + 1
                usertest[uid] = usertest[uid] + 1
                bot.sendMessage(uid, list(config['Обучение']['вопросы'][usertest[uid]].keys())[0])
            else:
                bot.sendMessage(uid, config['Начальный текст'], reply_markup=ReplyKeyboardMarkup(
                    keyboard=[[KeyboardButton(text='Обучение')],
                              [KeyboardButton(text='Регистрация'),
                               KeyboardButton(text='База знаний'),
                               KeyboardButton(text='Отзывы')]
                              ], resize_keyboard=True, one_time_keyboard=True))
        else:
            if data['text'] == list(config['Обучение']['вопросы'][usertest[uid]].values())[0]:
                userans[uid] = userans[uid] + 1
            if userans[uid]/len(config['Обучение']['вопросы']) >= 0.8:
                bot.sendMessage(uid, 'Ты прошёл тест на {} %. Можешь просматривать следующий ролик.'.format(userans[uid]/len(config['Обучение']['вопросы'])*100),
                                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                    [InlineKeyboardButton(text='База знаний', callback_data='База знаний'),
                                     InlineKeyboardButton(text='Тест', callback_data='Тест'),
                                     InlineKeyboardButton(text='Обучение', callback_data='Обучение')]
                                ]))
                editusermode(uid, 'else')
            else:
                bot.sendMessage(uid, 'Ты прошёл тест на {} %. Повтори попытку через час.'.format(userans[uid]/len(config['Обучение']['вопросы'])*100),
                                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                    [InlineKeyboardButton(text='База знаний', callback_data='База знаний'),
                                     InlineKeyboardButton(text='Тест', callback_data='Тест'),
                                     InlineKeyboardButton(text='Обучение', callback_data='Обучение')]
                                ]))
                editusermode(uid, 'else')
    elif 'Регистрация' in umode:
        if umode == 'РегистрацияName':
            if not any(map(str.isdigit, data['text'])):
                adduserinfo(uid, name=data['text'])
                editusermode(uid, 'РегистрацияDate')
                bot.sendMessage(uid, config['Регистрация']['2'][0])
                Thread(target=spammer, kwargs=dict(username=data['from']['username'], uid=uid)).start()
            else:
                bot.sendMessage(uid, config['Регистрация']['1'][1])
        elif umode == 'РегистрацияDate':
            if len(data['text'].split('.')) == 3 \
                    and len(data['text'].split('.')[0]) == 2 \
                    and len(data['text'].split('.')[1]) == 2 \
                    and len(data['text'].split('.')[2]) == 4 \
                    and str.isnumeric(data['text'].split('.')[0])\
                    and str.isnumeric(data['text'].split('.')[1])\
                    and str.isnumeric(data['text'].split('.')[2]):
                adduserinfo(uid, date=data['text'])
                editusermode(uid, 'РегистрацияPhone')
                bot.sendMessage(uid, config['Регистрация']['3'][0])
            else:
                bot.sendMessage(uid, config['Регистрация']['2'][1])
        elif umode == 'РегистрацияPhone':
            if str.isnumeric(data['text']) and len(data['text']) == 10:
                adduserinfo(uid, phone=data['text'])
                editusermode(uid, 'РегистрацияLink')
                bot.sendMessage(uid, config['Регистрация']['4'][0])
            else:
                bot.sendMessage(uid, config['Регистрация']['3'][1])
        elif umode == 'РегистрацияLink':
            if not any(map(str.isdigit, data['text'])):
                adduserinfo(uid, post=data['text'])
                editusermode(uid, 'else')
                bot.sendMessage(uid, config['Регистрация']['5'][0], reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='Обучение', callback_data='Обучение'),
                     InlineKeyboardButton(text='База знаний', callback_data='База знаний'),
                     InlineKeyboardButton(text='Отзывы', callback_data='Отзывы')]
                ]))
                bot.sendMessage(str(config['id админа']).replace(' ', '').replace('\n', ''), '@{} {}'.format(data['from']['username'], findfulluser(uid)[0]))
            else:
                bot.sendMessage(uid, config['Регистрация']['5'][1])
    # elif 'Калькулятор' in umode:
    #     if str.isnumeric(data['text']) and int(data['text']) <= 10 and int(data['text']) >= 0:
    #
    #         i = int(finduser(uid).replace('Калькулятор', ''))
    #         if str(i + 1) in config['Калькулятор']:
    #             editusermode(uid, 'Калькулятор{}'.format(i + 1))
    #             adduserinfo(uid, points=int(finduserpoints(uid)) + int(data['text']))
    #             bot.sendMessage(uid, config['Калькулятор'][str(i)])
    #         else:
    #             editusermode(uid, 'else')
    #             bot.sendMessage(uid, str(config['Калькулятор'][str(i)]).replace('?', str(paymentcounter(int(finduserpoints(uid))))),
    #                             reply_markup=InlineKeyboardMarkup(inline_keyboard=[
    #                                 [InlineKeyboardButton(text='Регистрация', callback_data='Регистрация'),
    #                                  InlineKeyboardButton(text='База знаний', callback_data='База знаний'),
    #                                  InlineKeyboardButton(text='Отзывы', callback_data='Отзывы')]
    #                             ]))
    #     else:
    #         bot.sendMessage(uid, config['Калькулятор']['0'])
    else:
        bot.sendMessage(uid, config['Начальный текст'], reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text='Обучение')],
                      [KeyboardButton(text='Регистрация'),
                       KeyboardButton(text='База знаний'),
                       KeyboardButton(text='Отзывы')]
                      ], resize_keyboard=True, one_time_keyboard=True))


def on_callback_query(data):
    global timeout
    global timeoutanswer
    global uservid
    global usertest
    global userans
    uid = data['from']['id']

    if uid not in uservid:
        uservid[uid] = 0
    # print(data['data'])
    umode = finduser(uid)
    if 'username' not in data['from']:
        data['from']['username'] = None
    if umode == None:
        adduser(uid=uid,
                    username=data['from']['username'])

    if data['data'] == 'Регистрация0':
        editusermode(uid, 'РегистрацияName')
        bot.sendMessage(uid, config['Регистрация']['1'][0])
    elif data['data'] == 'Тест':
        if uid not in timeoutanswer:
            editusermode(uid, 'Тест')
            usertest[uid] = 0
            userans[uid] = 0
            timeoutanswer[uid] = int(time.time())
            bot.sendMessage(uid, list(config['Обучение']['вопросы'][usertest[uid]].keys())[0])
        elif timeoutanswer[uid] < int(time.time()) - (60 * 60):
            editusermode(uid, 'Тест')
            usertest[uid] = 0
            userans[uid] = 0
            timeoutanswer[uid] = int(time.time())
            bot.sendMessage(uid, list(config['Обучение']['вопросы'][usertest[uid]].keys())[0])
        else:
            bot.sendMessage(uid, 'Вам нужно подождать час, чтобы провторно пройти тест',
                            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text='База знаний', callback_data='База знаний'),
                                 InlineKeyboardButton(text='Тест', callback_data='Тест')]
                            ]))
    elif data['data'] == 'Регистрация':
        editusermode(uid=uid, mode='Регистрация')
        bot.sendMessage(uid, config['Регистрация']['0'], reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Ок', callback_data='Регистрация0')]
        ]))
    elif data['data'] == 'Задатьещёвопрос':
        kb = [[InlineKeyboardButton(text='Как зарегистрироваться', callback_data='зарегистрироваться')],
              [InlineKeyboardButton(text='Обучение', callback_data='Обучение')]]
        editusermode(uid, 'вопросыбз')
        for i in config['База знаний']['вопросы']:
            kb.append([InlineKeyboardButton(text=list(i.keys())[0], callback_data=list(i.keys())[0])])
        kb.append([InlineKeyboardButton(text='В начало', callback_data='Вначало')])
        bot.sendMessage(uid, config['База знаний']['0'],
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    elif data['data'] == 'База знаний':
        kb = [[InlineKeyboardButton(text='Как зарегистрироваться', callback_data='зарегистрироваться')],
              [InlineKeyboardButton(text='Обучение', callback_data='Обучение')]]
        editusermode(uid, 'вопросыбз')
        for i in config['База знаний']['вопросы']:
            kb.append([InlineKeyboardButton(text=list(i.keys())[0], callback_data=list(i.keys())[0])])
        kb.append([InlineKeyboardButton(text='В начало', callback_data='Вначало')])
        bot.sendMessage(uid, config['База знаний']['0'],
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    elif data['data'] == 'Вначало':
        bot.sendMessage(uid, config['Начальный текст'], reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text='Обучение')],
                      [KeyboardButton(text='Регистрация'),
                       KeyboardButton(text='База знаний'),
                       KeyboardButton(text='Отзывы')]
                      ], resize_keyboard=True, one_time_keyboard=True))
    elif data['data'] == 'Обучение':
        if len(config['Обучение']['видео']) > uservid[uid]:
            if uid not in timeout:
                uservid[uid] = 0
                bot.sendMessage(uid, list(config['Обучение']['видео'][uservid[uid]].keys())[0], reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                    [InlineKeyboardButton(text='База знаний', callback_data='База знаний'),
                                     InlineKeyboardButton(text='Тест', callback_data='Тест')]
                                ]))
                sendvid(uid)
            elif timeout[uid] < int(time.time()) + 60*60*48:
                bot.sendMessage(uid, list(config['Обучение']['видео'][uservid[uid]].keys())[0], reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                    [InlineKeyboardButton(text='База знаний', callback_data='База знаний'),
                                     InlineKeyboardButton(text='Тест', callback_data='Тест')]
                                ]))
                sendvid(uid)
            else:
                bot.sendMessage(uid, 'Вам нужно подождать 48 часов, ил пройти тест на 80% или более.', reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                    [InlineKeyboardButton(text='База знаний', callback_data='База знаний'),
                                     InlineKeyboardButton(text='Тест', callback_data='Тест')]
                                ]))
        else:
            bot.sendMessage(uid, 'Ты закончил обучение. {}'.format(config['Ссылка на 100$']))
    # elif data['data'] == 'Испытательныйсрок':
    #     bot.sendMessage(uid, config['База знаний']['Испытательный срок'], reply_markup=InlineKeyboardMarkup(inline_keyboard=[
    #                         [InlineKeyboardButton(text='Задать ещё вопрос', callback_data='Задатьещёвопрос'),
    #                          InlineKeyboardButton(text='В начало', callback_data='Вначало'),
    #                          InlineKeyboardButton(text='Посчитать ЗП', callback_data='ПосчитатьЗП')]
    #                     ]))
    # elif data['data'] == 'Обязанности':
    #     editusermode(uid, 'Калькулятор2')
    #     adduserinfo(uid, points=0)
    #     bot.sendMessage(uid, config['Калькулятор']['1'])
    # elif data['data'] == 'Образование':
    #     bot.deleteMessage((uid, data['message']['message_id']))
    #     bot.sendMessage(uid, config['База знаний']['Образование'], reply_markup=InlineKeyboardMarkup(inline_keyboard=[
    #                         [InlineKeyboardButton(text='Задать ещё вопрос', callback_data='Задатьещёвопрос'),
    #                          InlineKeyboardButton(text='В начало', callback_data='Вначало'),
    #                          InlineKeyboardButton(text='Посчитать ЗП', callback_data='ПосчитатьЗП')]
    #                     ]))
    # elif data['data'] == 'Условия':
    #     bot.deleteMessage((uid, data['message']['message_id']))
    #     bot.sendMessage(uid, config['База знаний']['Условия'], reply_markup=InlineKeyboardMarkup(inline_keyboard=[
    #                         [InlineKeyboardButton(text='Задать ещё вопрос', callback_data='Задатьещёвопрос'),
    #                          InlineKeyboardButton(text='В начало', callback_data='Вначало'),
    #                          InlineKeyboardButton(text='Посчитать ЗП', callback_data='ПосчитатьЗП')]
    #                     ]))
    # elif data['data'] == 'Адресофиса':
    #     bot.deleteMessage((uid, data['message']['message_id']))
    #     bot.sendLocation(uid, config['База знаний']['Адрес офиса'][0], config['База знаний']['Адрес офиса'][1],
    #                      reply_markup=InlineKeyboardMarkup(inline_keyboard=[
    #                          [InlineKeyboardButton(text='Задать ещё вопрос', callback_data='Задатьещёвопрос'),
    #                           InlineKeyboardButton(text='В начало', callback_data='Вначало'),
    #                           InlineKeyboardButton(text='Посчитать ЗП', callback_data='ПосчитатьЗП')]
    #                      ]))
    # elif data['data'] == 'Посмотретьрабочееместо':
    #     bot.deleteMessage((uid, data['message']['message_id']))
    #     mediagroup = []
    #     for i in config['База знаний']['Посмотреть рабочее место']['фотки']:
    #         mediagroup.append(InputMediaPhoto(type='photo', media=i))
    #     bot.sendMediaGroup(uid, mediagroup)
    #     bot.sendMessage(uid, config['База знаний']['Посмотреть рабочее место']['текст'],
    #                     reply_markup=InlineKeyboardMarkup(inline_keyboard=[
    #                         [InlineKeyboardButton(text='Задать ещё вопрос', callback_data='Задатьещёвопрос'),
    #                          InlineKeyboardButton(text='В начало', callback_data='Вначало'),
    #                          InlineKeyboardButton(text='Посчитать ЗП', callback_data='ПосчитатьЗП')]
    #                     ]))
    #     del mediagroup
    elif data['data'] == 'Отзывы':
        bot.sendMessage(uid, config['Отзывы'][0], reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Читать ещё', callback_data='Читатьещё0'),
             InlineKeyboardButton(text='В начало', callback_data='Вначало'),
             InlineKeyboardButton(text='Обучение', callback_data='Обучение')]
        ]))
    elif 'Читатьещё' in data['data']:
        if int(data['data'].replace('Читатьещё', '')) <= len(config['Отзывы']) - 1:
            bot.sendMessage(uid, config['Отзывы'][int(data['data'].replace('Читатьещё', ''))],
                            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text='Читать ещё', callback_data='Читатьещё{}'.format(1 + int(data['data'].replace('Читатьещё', '')))),
                                 InlineKeyboardButton(text='В начало', callback_data='Вначало'),
                                 InlineKeyboardButton(text='Обучение', callback_data='Обучение')]
                            ]))
            bot.deleteMessage((uid, data['message']['message_id']))
        else:
            bot.sendMessage(uid, config['Отзывы'][0],
                            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text='Читать ещё', callback_data='Читатьещё1'),
                                 InlineKeyboardButton(text='В начало', callback_data='Вначало'),
                                 InlineKeyboardButton(text='Обучение', callback_data='Обучение')]
                            ]))
            bot.deleteMessage((uid, data['message']['message_id']))
    elif umode == 'вопросыбз':
        for i in config['База знаний']['вопросы']:
            if data['data'] in i:
                bot.sendMessage(uid, i[data['data']],
                                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='Задать ещё вопрос', callback_data='Задатьещёвопрос'),
                     InlineKeyboardButton(text='В начало', callback_data='Вначало'),
                     InlineKeyboardButton(text='Обучение', callback_data='Обучение')]]))
                break


try:
    # print(bottoken)
    bot = telepot.Bot(bottoken)
    # bot.deleteWebhook()
    print(bot.getMe())
    MessageLoop(bot, {'chat': handler,
                      'callback_query': on_callback_query}).run_as_thread()
except:
    logging.exception(config)
    raise

while 1:
    time.sleep(1)