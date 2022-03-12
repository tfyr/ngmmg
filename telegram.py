import requests as requests


def send_mess(chat, text, url, reply_markup=None, parse_mode=None):
    params = {'chat_id': chat, 'text': text}
    if reply_markup:
        params['reply_markup'] = reply_markup
    if parse_mode:
        params['parse_mode'] = parse_mode
    response = requests.post(url + 'sendMessage', data=params)
    return response
