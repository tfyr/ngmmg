import json

from bot import get_name, mydb, get_balance, test_chat_id, telegram_bot_url_mmg
from telegram import send_mess

test_msg = '''
        {
            "update_id":142691185,
            "message":{
                "message_id": 47,
                "from":{
                    "id":448010439,
                    "is_bot":false,
                    "first_name":"Nail",
                    "last_name":"Sharipov",
                    "language_code":"ru"
                },
                "chat":{
                    "id":448010439,
                    "first_name":
                    "Nail",
                    "last_name":"Sharipov",
                    "type":"private"
                },
                "date":1647071060,
                "text":"/balance",
                "entities":[
                    {
                        "offset":0,
                        "length":8,
                        "type":"bot_command"
                    }
                ]
            }
        }'''
test_msg_json = json.loads(test_msg)

nash_id = 448010439


def test_get_name():
    id, name, = get_name(test_msg_json['message']['from'])
    assert id == nash_id and name == 'Nail'


def test_mydb():
    db = mydb(debug=True)
    assert db is not None, "can't db connect"
    db.close()


def test_get_balance():
    db = mydb(debug=True)
    assert db is not None
    with db.cursor() as cursor:
        value = get_balance(cursor, 0)
        assert value is None
        value = get_balance(cursor, nash_id)
        assert value is not None and value >= 1000
    db.close()


def test_send_msg():
    ret = send_mess(test_chat_id, "<span class=\"tg-spoiler\">спойлер <s>Х</s></span>",
                    url=telegram_bot_url_mmg,
                    reply_markup=None,
                    parse_mode="HTML",
              )
    assert ret is not None and ret.status_code == 200
#def test_always_fails():
#    assert False

def test_graph():
    db = mydb(debug=True)
    assert db is not None
    nodes = list()
    links = list()
    with db.cursor() as cursor:
        cursor.execute('''select id from user''', )
        for id, in cursor.fetchall():
            grp = int(id) % 10
            nodes.append({"id": id, "group": grp})
        cursor.execute('''select frm,too,count(id), sum(value) 
                            from tran where frm is not null
                           group by frm,too''', )
        for frm, too, cnt, summ in cursor.fetchall():
            links.append({"source": frm, "target": too, "value": cnt})
        with open('result.json', 'w') as fp:
            json.dump({'nodes': nodes, 'links': links}, fp)
    db.close()
