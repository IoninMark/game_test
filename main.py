from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

import json
import uuid


app = FastAPI()

active_connctions = []


@app.get('/')
async def index():
    # Генерируем ID игрока и отправляем в шаблон
    player_id = f'player_{uuid.uuid4().hex[:8]}'
    with open('index.html', 'r') as f:
        html_content = f.read()
        html_content = html_content.replace("{{player_id}}", player_id)
        return HTMLResponse(html_content)


@app.websocket('/ws/{player_id}')
async def ws_endpoint(websocket: WebSocket, player_id: str):
    await websocket.accept()
    active_connctions.append((websocket, player_id))

    try:
        while True:
            data = await websocket.receive_text()
            action = json.loads(data)

            # Распространяем действие всем игрокам
            for conn, _ in active_connctions:
                await conn.send_text(json.dumps({
                    'player': player_id,
                    'action': action['payload']
                }))
    except WebSocketDisconnect:
        active_connctions.remove((websocket, player_id))
