import argparse
from aiohttp import web
import logging

from bot import parse_mmg_bot_msg

parser = argparse.ArgumentParser(description="aiohttp server example")
parser.add_argument('--path')
parser.add_argument('--port')


async def handle(request):
    #name = request.match_info.get('name', "Anonymous")
    if request.body_exists:
        parse_mmg_bot_msg(await request.read(), debug=False)
    # msg = json.loads(request.body.decode('utf-8'))

    return web.Response(text="{}", content_type="application/json ")

if __name__ == '__main__':
    app = web.Application()
    app.add_routes([web.post('/ngmmg-bot', handle),
                    # web.get('/{name}', handle),
                    ])
    args = parser.parse_args()
    # logging.basicConfig(level=logging.DEBUG)
    web.run_app(app, path=args.path, port=args.port, )
