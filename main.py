from aiohttp import web

from bot import parse_mmg_bot_msg


async def handle(request):
    #name = request.match_info.get('name', "Anonymous")
    text = "Hello"
    parse_mmg_bot_msg(request.text(), debug=False)
    # msg = json.loads(request.body.decode('utf-8'))

    return web.Response(text="{}", content_type="application/json ")

app = web.Application()
app.add_routes([web.get('/ngmmg-bot', handle),
                # web.get('/{name}', handle),
                ])

if __name__ == '__main__':
    web.run_app(app)