# -*- coding: utf-8 -*-
"""
server.py — WebSocket сервер для FSOCIETY Messenger
Работает на Render.com
"""
import asyncio
import json
import websockets
from datetime import datetime

# Активные клиенты: {websocket: {"nickname": "...", "user_id": "..."}}
clients = {}


async def handler(websocket):
    """Обрабатывает подключение клиента"""
    nickname = None
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                continue

            msg_type = data.get("type")

            # ===== РЕГИСТРАЦИЯ =====
            if msg_type == "login":
                nickname = data.get("nickname", "Unknown")
                clients[websocket] = {"nickname": nickname}
                print(f"✅ {nickname} подключился")
                # Оповещаем всех
                await broadcast({
                    "type": "user_online",
                    "nickname": nickname,
                }, exclude=websocket)
                # Отправляем список онлайн
                online = [c["nickname"] for c in clients.values()]
                await websocket.send(json.dumps({
                    "type": "online_list",
                    "users": online,
                }))
                continue

            # ===== СООБЩЕНИЯ =====
            if msg_type == "message":
                text = data.get("text", "")
                sender = clients.get(websocket, {}).get("nickname", "Unknown")
                await broadcast({
                    "type": "message",
                    "sender": sender,
                    "text": text,
                    "time": datetime.now().strftime("%H:%M:%S"),
                })
                continue

            # ===== ЗВОНОК: ЗАПРОС =====
            if msg_type == "call_request":
                target = data.get("target")  # ник того, кому звоним
                call_type = data.get("call_type", "audio")  # audio/video
                sender = clients.get(websocket, {}).get("nickname", "Unknown")
                # Находим target
                for ws, info in clients.items():
                    if info["nickname"] == target:
                        await ws.send(json.dumps({
                            "type": "incoming_call",
                            "from": sender,
                            "call_type": call_type,
                        }))
                        print(f"📞 {sender} → {target} ({call_type})")
                        break
                continue

            # ===== ЗВОНОК: ОТВЕТ =====
            if msg_type == "call_answer":
                target = data.get("target")
                accepted = data.get("accepted", False)
                sender = clients.get(websocket, {}).get("nickname", "Unknown")
                for ws, info in clients.items():
                    if info["nickname"] == target:
                        await ws.send(json.dumps({
                            "type": "call_response",
                            "from": sender,
                            "accepted": accepted,
                        }))
                        break
                continue

            # ===== ЗВОНОК: ОТБОЙ =====
            if msg_type == "call_end":
                target = data.get("target")
                sender = clients.get(websocket, {}).get("nickname", "Unknown")
                for ws, info in clients.items():
                    if info["nickname"] == target:
                        await ws.send(json.dumps({
                            "type": "call_ended",
                            "from": sender,
                        }))
                        break
                continue

            # ===== WEBRTC SIGNALING =====
            if msg_type in ("webrtc_offer", "webrtc_answer", "webrtc_ice"):
                target = data.get("target")
                sender = clients.get(websocket, {}).get("nickname", "Unknown")
                data["from"] = sender
                for ws, info in clients.items():
                    if info["nickname"] == target:
                        await ws.send(json.dumps(data))
                        break
                continue

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        if websocket in clients:
            nick = clients[websocket]["nickname"]
            del clients[websocket]
            print(f"❌ {nick} отключился")
            await broadcast({
                "type": "user_offline",
                "nickname": nick,
            })


async def broadcast(data, exclude=None):
    """Отправляет сообщение всем клиентам"""
    if not clients:
        return
    msg = json.dumps(data)
    tasks = []
    for ws in clients.keys():
        if ws != exclude:
            try:
                tasks.append(ws.send(msg))
            except Exception:
                pass
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)


async def main():
    """Запуск сервера"""
    port = 10000  # Render использует PORT из env
    import os
    port = int(os.environ.get("PORT", 10000))
    async with websockets.serve(handler, "0.0.0.0", port):
        print(f"🚀 WebSocket сервер запущен на порту {port}")
        await asyncio.Future()  # бесконечно


if __name__ == "__main__":
    asyncio.run(main())