import json

import MySQLdb
from MySQLdb import IntegrityError

from telegram import send_mess


def get_name(msg):
    if not msg:
        return None
    if 'username' in msg:
        name = msg['username']
    elif 'first_name' in msg:
        name = msg['first_name']
    elif 'last_name' in msg:
        name = msg['last_name']
    return (msg['id'], name,)


def mydb(debug):
    return MySQLdb.connect(host="127.0.0.1" if debug else "localhost",  # your host, usually localhost
                           user="chatbot_mmg",  # your username
                           passwd="",  # your password
                           port=3333,  # $ ssh -L 3333:127.0.0.1:3306 vds -N
                           db="chatbot_mmg")


def get_balance(cursor, from_id):
    cursor.execute('select current_value from user where id=%(id)s', {'id': from_id})
    value, = cursor.fetchone() or (None,)
    return value


init_balance = 1000
transfer_amount = 10
action_plus = 1
action_msg = 0
mmg_chat_id = -1001125974900
test_chat_id = -534237299
telegram_bot_url_mmg = "https://api.telegram.org/bot5084712772:AAFXVoCWYNeeHxMmG0XHnD-ta0oBYYooL3c/"


def init_user(cursor, id):
    try:
        cursor.execute('insert into user (id, current_value) values (%(id)s, %(init_balance)s)',
                       {'id': id, 'init_balance': init_balance, })
    except IntegrityError:
        pass


def parse_mmg_bot_msg(request_body, debug=True):
    r = json.loads(request_body)
    from_username = None
    from_id = rtm_from_id = None
    value = 0
    finish = False

    if r and 'message' in r and 'from' in r['message']:
        msg = r['message']
        if msg and 'text' in msg:
            text = msg['text']
            # if msg['chat']['id'] != mmg_chat_id:
            #     return
            db = mydb(debug)
            with db.cursor() as cursor:

                from_id, from_username, = get_name(msg['from'])
                if msg['chat']['id'] == mmg_chat_id:
                    init_user(cursor, from_id)

                if 'entities' in msg:
                    entities = msg['entities']
                    if len(entities) > 0 and 'type' in entities[0]:
                        type = entities[0]['type']
                        if type == 'bot_command':
                            if text.strip().startswith("/balance"):
                                blnc = get_balance(cursor, from_id)
                                if blnc is None:
                                    blnc = init_balance
                                send_mess(msg['chat']['id'],
                                          "Баланс хуекоинов: {}".format(blnc),
                                          url=telegram_bot_url_mmg,
                                          reply_markup=None
                                          )
                                finish = True

                if not finish and 'reply_to_message' in msg:
                    rtm = msg['reply_to_message']
                    if 'from' in rtm:
                        rtm_from = rtm['from']
                        rtm_from_id, rtm_from_username, = get_name(rtm_from)
                        if msg['chat']['id'] == mmg_chat_id:
                            init_user(cursor, rtm_from_id)
                    if text.strip()[0] == '+':
                        if from_id != rtm_from_id:
                            balance = get_balance(cursor, from_id)
                            if balance is None or balance >= transfer_amount:
                                if msg['chat']['id'] == mmg_chat_id:
                                    cursor.execute('update user set `last`=now(), current_value=current_value - %(transfer_amount)s where id=%(id)s',
                                                   {'id': from_id, 'transfer_amount': transfer_amount,})
                                    cursor.execute('update user set `last`=now(), current_value=current_value + %(transfer_amount)s where id=%(id)s',
                                                   {'id': rtm_from_id, 'transfer_amount': transfer_amount,})
                                value = transfer_amount
                                tg_msg = "{} перевел {} {} хуекоинов".format(from_username, rtm_from_username, value)
                                send_mess(test_chat_id if debug else msg['chat']['id'], tg_msg,
                                          url=telegram_bot_url_mmg,
                                          reply_markup=None
                                          )
                if not finish and msg['chat']['id'] == mmg_chat_id:
                    cursor.execute('''insert into `plus` (`from`, `to`, action, `value`, `text`) values (%(from)s, %(to)s, %(action)s, %(value)s, %(text)s)''',
                               {'from': from_id, 'to': rtm_from_id, 'action': action_msg, 'value': value, 'text': text})
            db.commit()
            db.close()
