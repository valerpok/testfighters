import argparse
import asyncio
import json
from aiohttp import web, WSMsgType


class SocketsList:
    sockets = {}

    # Structure: {game_id: [sockets]}

    @classmethod
    def get_game_with_ws(cls, ws):
        for game, value in cls.sockets.items():
            for socket in value:
                if socket == ws:
                    return game

    @classmethod
    def remove_ws(cls, ws):
        game = SocketsList.get_game_with_ws(ws)
        cls.sockets[game].remove(ws)

        if not cls.sockets[game]:
            del cls.sockets[game]


class NotificationsQueue:
    queue = {}

    @classmethod
    def add_notification(cls, ws, payload):
        cls.queue[ws] = payload


def callback(connection, pid, channel, payload):
    payload = json.loads(payload)

    sockets_with_current_game = SocketsList.sockets.get(payload['game_id'], None)
    if sockets_with_current_game:

        print('I am sending notifications to {} sockets'.format(len(sockets_with_current_game)))

        for socket in sockets_with_current_game:

            # if not True:
            #     SocketsList.remove_ws(socket)
            #     print('socket removed because cant prepare')
            # else:
            try:
                socket.send_json(payload['updates'])
                print('NOTIFICATION {} WITH STATUS "{}" SENT TO GAME {}'.format(
                    str(payload['notification_id']),
                    str(payload['updates']['status']),
                    str(payload['game_id']))
                )
            except Exception as e:
                SocketsList.remove_ws(socket)
                print('removed socket according to sending error {}'.format(e))

    else:
        # SocketsList.sockets[payload['game_id']] = [ws, ]
        print('Something strange happen -- came payload with game_id without sockets')


async def wshandler(request):
    print("Connected")

    ws = web.WebSocketResponse(heartbeat=5)
    await ws.prepare(request)

    async for msg in ws:

        if msg.type == WSMsgType.TEXT:

            if msg.data == 'close':
                await ws.close()

            else:
                print('Received message with data {}'.format(msg.data))

                # While ws connection client send game_id={number} message
                # After that, I add dict with game_id and WebSocketResponse instance to
                # SocketsList.sockets

                if msg.data.startswith('game_id'):
                    _, game_id = msg.data.split('=')

                    game_id = int(game_id)
                    sockets_with_current_game = SocketsList.sockets.get(game_id, None)
                    if sockets_with_current_game:
                        sockets_with_current_game.append(ws)
                    else:
                        SocketsList.sockets[game_id] = [ws, ]

                    print('added socket', SocketsList.sockets)

                    await ws.send_json({'status': 'initiate'})

                # if msg.data == 'drop me':
                #     SocketsList.remove_ws(ws)
                #     print('Socket removed by request')

        if msg.type == web.MsgType.close:
            SocketsList.remove_ws(ws)
            print('Socket removed after close msg')
            await ws.close()
            break

    try:
        SocketsList.remove_ws(ws)
        print('socket removed in handler')
    except KeyError:
        print('key error')

    print('Connection closed')
    return ws


def main():
    parser = argparse.ArgumentParser(description="aiohttp server")
    parser.add_argument('--path')
    parser.add_argument('--port')
    args = parser.parse_args()

    app = web.Application()
    app.router.add_get('/', wshandler)

    loop = asyncio.get_event_loop()
    loop.create_task(listener())
    loop.create_task(web.run_app(app, host='0.0.0.0', port=int(args.port), path=args.path))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print('\nCtrl-C caught. Exiting...')
    finally:
        loop.close()


if __name__ == "__main__":
    main()
