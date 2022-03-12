import argparse
from aiohttp import web

from bot import parse_mmg_bot_msg

parser = argparse.ArgumentParser(description="aiohttp server example")
parser.add_argument('--path')
parser.add_argument('--port')


async def handle(request):
    #name = request.match_info.get('name', "Anonymous")
    parse_mmg_bot_msg(request.body.decode('utf-8'), debug=False)
    # msg = json.loads(request.body.decode('utf-8'))

    return web.Response(text="{}", content_type="application/json ")

if __name__ == '__main__':
    app = web.Application()
    app.add_routes([web.post('/ngmmg-bot', handle),
                    # web.get('/{name}', handle),
                    ])
    args = parser.parse_args()
    web.run_app(app, path=args.path, port=args.port)
