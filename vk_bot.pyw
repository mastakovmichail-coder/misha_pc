# -*- coding: utf-8 -*-
"""
vk_bot.pyw — VK-бот для FSOCIETY PC CONTROL
Использует commands.py + auth.py
Требует авторизацию через никнейм + Gmail код
"""

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import subprocess
import os
import sys
import time
import random
import requests
import socket
import platform
from PIL import ImageGrab, Image
from io import BytesIO

# ===== ИМПОРТЫ =====
try:
    import commands
    import auth
except ImportError as e:
    print(f"❌ Ошибка: {e}")
    print("Убедись, что commands.py и auth.py лежат рядом с vk_bot.pyw")
    input("Нажми Enter для выхода...")
    sys.exit(1)

# ============================================================
# НАСТРОЙКИ
# ============================================================
TOKEN = "vk1.a.517XnJRVi85ZZ6pBITZA4vBihrMBQ7x43cYW1uGq9joRm8532YibJj0VfrQ_NPBlQ_xb4x8fRUMwbILhKItvPWEiTc1eNLBHKUHdqO2lGCsHi1rQeUw1gsjqcq9v8VRRyUMfBavAsRGCdvZi6i6TyA2Fdia8Ab5_m0BvLdxlVQhu9cKqEyqHsraRiqt-wUAhi3fvALdkEnQheB4fVMpM2g"
GROUP_ID = 241449788

# ===== СОСТОЯНИЯ ПОЛЬЗОВАТЕЛЕЙ =====
# {vk_id: {"state": "waiting_nickname/waiting_code", "nickname": "..."}}
user_states = {}

# ============================================================
# АВТОРИЗАЦИЯ
# ============================================================
try:
    vk_session = vk_api.VkApi(token=TOKEN)
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
except Exception as e:
    print(f"❌ Ошибка авторизации VK: {e}")
    input("Нажми Enter для выхода...")
    sys.exit(1)

# ============================================================
# ФУНКЦИИ
# ============================================================

def send_message(user_id, text, keyboard=None):
    """Отправляет сообщение"""
    try:
        vk.messages.send(
            user_id=user_id,
            message=text[:4000],
            random_id=random.randint(1, 999999),
            keyboard=keyboard.get_keyboard() if keyboard else None
        )
    except Exception as e:
        print(f"Ошибка отправки: {e}")


def send_photo(user_id, photo_path):
    """Отправляет фото"""
    try:
        upload = vk_api.upload.VkUpload(vk_session)
        photo = upload.photo_messages(photo_path)[0]
        vk.messages.send(
            user_id=user_id,
            attachment=f"photo{photo['owner_id']}_{photo['id']}",
            random_id=random.randint(1, 999999)
        )
    except Exception as e:
        send_message(user_id, f"❌ Ошибка фото: {e}")


# ============================================================
# КЛАВИАТУРЫ
# ============================================================

def kb_main():
    kb = VkKeyboard(one_time=False)
    kb.add_button("📸 Скриншот", color=VkKeyboardColor.PRIMARY)
    kb.add_button("📊 Статус", color=VkKeyboardColor.POSITIVE)
    kb.add_line()
    kb.add_button("⛔ Выключить", color=VkKeyboardColor.NEGATIVE)
    kb.add_button("🔄 Перезагрузить", color=VkKeyboardColor.SECONDARY)
    kb.add_line()
    kb.add_button("🔒 Блокировка", color=VkKeyboardColor.SECONDARY)
    kb.add_button("🖼️ Обои", color=VkKeyboardColor.PRIMARY)
    kb.add_line()
    kb.add_button("➡️ Программы", color=VkKeyboardColor.PRIMARY)
    kb.add_button("➡️ Приколы", color=VkKeyboardColor.PRIMARY)
    kb.add_line()
    kb.add_button("➡️ Система", color=VkKeyboardColor.PRIMARY)
    kb.add_button("➡️ Сайты", color=VkKeyboardColor.PRIMARY)
    kb.add_line()
    kb.add_button("👤 Профиль", color=VkKeyboardColor.SECONDARY)
    kb.add_button("❓ Помощь", color=VkKeyboardColor.SECONDARY)
    return kb


def kb_programs():
    kb = VkKeyboard(one_time=False)
    kb.add_button("💻 CMD", color=VkKeyboardColor.SECONDARY)
    kb.add_button("⚡ PowerShell", color=VkKeyboardColor.SECONDARY)
    kb.add_line()
    kb.add_button("📝 Блокнот", color=VkKeyboardColor.SECONDARY)
    kb.add_button("🧮 Калькулятор", color=VkKeyboardColor.SECONDARY)
    kb.add_line()
    kb.add_button("📂 Проводник", color=VkKeyboardColor.SECONDARY)
    kb.add_button("📊 Диспетчер задач", color=VkKeyboardColor.SECONDARY)
    kb.add_line()
    kb.add_button("🎨 Paint", color=VkKeyboardColor.SECONDARY)
    kb.add_button("✂️ Ножницы", color=VkKeyboardColor.SECONDARY)
    kb.add_line()
    kb.add_button("⚙️ Панель управления", color=VkKeyboardColor.SECONDARY)
    kb.add_button("🖥️ Устройства", color=VkKeyboardColor.SECONDARY)
    kb.add_line()
    kb.add_button("⬅️ Назад", color=VkKeyboardColor.NEGATIVE)
    return kb


def kb_jokes():
    kb = VkKeyboard(one_time=False)
    kb.add_button("🎵 Рикролл", color=VkKeyboardColor.PRIMARY)
    kb.add_button("🎵 Рикролл x5", color=VkKeyboardColor.PRIMARY)
    kb.add_line()
    kb.add_button("🎵 Рикролл x10", color=VkKeyboardColor.PRIMARY)
    kb.add_button("🦊 Firefox x10", color=VkKeyboardColor.PRIMARY)
    kb.add_line()
    kb.add_button("🌐 Chrome x10", color=VkKeyboardColor.PRIMARY)
    kb.add_button("📝 Блокнот x10", color=VkKeyboardColor.PRIMARY)
    kb.add_line()
    kb.add_button("💀 Убить explorer", color=VkKeyboardColor.NEGATIVE)
    kb.add_button("🔄 Восст. explorer", color=VkKeyboardColor.POSITIVE)
    kb.add_line()
    kb.add_button("🔊 Макс. громкость", color=VkKeyboardColor.SECONDARY)
    kb.add_button("🔇 Отключить звук", color=VkKeyboardColor.SECONDARY)
    kb.add_line()
    kb.add_button("⬅️ Назад", color=VkKeyboardColor.NEGATIVE)
    return kb


def kb_system():
    kb = VkKeyboard(one_time=False)
    kb.add_button("📊 Статус", color=VkKeyboardColor.POSITIVE)
    kb.add_button("⚡ CPU", color=VkKeyboardColor.PRIMARY)
    kb.add_line()
    kb.add_button("🧠 RAM", color=VkKeyboardColor.PRIMARY)
    kb.add_button("💾 Диск", color=VkKeyboardColor.PRIMARY)
    kb.add_line()
    kb.add_button("🔋 Батарея", color=VkKeyboardColor.PRIMARY)
    kb.add_button("⏱️ Аптайм", color=VkKeyboardColor.PRIMARY)
    kb.add_line()
    kb.add_button("📋 Процессы", color=VkKeyboardColor.SECONDARY)
    kb.add_button("🌐 IP", color=VkKeyboardColor.SECONDARY)
    kb.add_line()
    kb.add_button("📡 Ping Google", color=VkKeyboardColor.SECONDARY)
    kb.add_button("🔄 Flush DNS", color=VkKeyboardColor.SECONDARY)
    kb.add_line()
    kb.add_button("🧹 Очистка Temp", color=VkKeyboardColor.WARNING)
    kb.add_button("🗑️ Очистка корзины", color=VkKeyboardColor.WARNING)
    kb.add_line()
    kb.add_button("⬅️ Назад", color=VkKeyboardColor.NEGATIVE)
    return kb


def kb_sites():
    kb = VkKeyboard(one_time=False)
    kb.add_button("📺 YouTube", color=VkKeyboardColor.PRIMARY)
    kb.add_button("🔍 Google", color=VkKeyboardColor.PRIMARY)
    kb.add_line()
    kb.add_button("📱 VK", color=VkKeyboardColor.PRIMARY)
    kb.add_button("🐙 GitHub", color=VkKeyboardColor.PRIMARY)
    kb.add_line()
    kb.add_button("🎮 Twitch", color=VkKeyboardColor.PRIMARY)
    kb.add_button("💬 Discord", color=VkKeyboardColor.PRIMARY)
    kb.add_line()
    kb.add_button("✈️ Telegram", color=VkKeyboardColor.PRIMARY)
    kb.add_button("👽 Reddit", color=VkKeyboardColor.PRIMARY)
    kb.add_line()
    kb.add_button("🤖 ChatGPT", color=VkKeyboardColor.PRIMARY)
    kb.add_button("📚 Wikipedia", color=VkKeyboardColor.PRIMARY)
    kb.add_line()
    kb.add_button("⬅️ Назад", color=VkKeyboardColor.NEGATIVE)
    return kb


def kb_profile():
    kb = VkKeyboard(one_time=False)
    kb.add_button("👤 Мой профиль", color=VkKeyboardColor.PRIMARY)
    kb.add_button("🔗 Отвязать VK", color=VkKeyboardColor.NEGATIVE)
    kb.add_line()
    kb.add_button("⬅️ Назад", color=VkKeyboardColor.NEGATIVE)
    return kb


# ============================================================
# ЗАПУСК
# ============================================================
print("=" * 60)
print("🔥 FSOCIETY VK BOT")
print("=" * 60)
print(f"📋 Команд: {commands.get_commands_count()}")
print(f"👥 Пользователей: {len(auth.load_users())}")
print("=" * 60)
print("🔥 VK-бот запущен... Ожидание сообщений...")
print("=" * 60)


# ============================================================
# ОБРАБОТКА СООБЩЕНИЙ
# ============================================================
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        user_id = event.user_id
        text = event.text.strip()
        text_lower = text.lower()
        attachments = event.attachments

        # ====================================================
        # ПРОВЕРКА АВТОРИЗАЦИИ
        # ====================================================
        user = auth.get_user_by_vk(user_id)

        if not user:
            # === НЕ АВТОРИЗОВАН ===
            state_data = user_states.get(user_id, {})
            state = state_data.get("state")

            if state == "waiting_code":
                # Ждём код из Gmail
                nickname = state_data["nickname"]
                success, result = auth.vk_login_step2(nickname, text, user_id)

                if success:
                    del user_states[user_id]
                    send_message(user_id, f"✅ Вход выполнен! Добро пожаловать, {nickname}")
                    send_message(user_id, "🔥 Главное меню:", kb_main())
                else:
                    send_message(user_id, f"❌ {result}\nПопробуй ещё раз или напиши /start")
                continue

            elif state == "waiting_nickname":
                # Ждём никнейм
                nickname = text
                success, msg = auth.vk_login_step1(nickname)

                if success:
                    user_states[user_id] = {"state": "waiting_code", "nickname": nickname}
                    send_message(user_id, 
                        "📧 Код отправлен на email.\n"
                        "Введи его сюда (6 цифр)."
                    )
                else:
                    send_message(user_id, f"❌ {msg}\nПопробуй ещё раз или напиши /start")
                continue

            else:
                # Первое сообщение
                if text_lower in ["/start", "начать", "привет", "меню", "/menu"]:
                    user_states[user_id] = {"state": "waiting_nickname"}
                    send_message(user_id,
                        "🔐 FSOCIETY — ВХОД\n\n"
                        "Введи свой никнейм с сайта.\n\n"
                        "Если нет аккаунта — зарегистрируйся:\n"
                        "http://localhost:8080/register"
                    )
                else:
                    send_message(user_id, "🔐 Сначала войди. Напиши /start")
                continue

        # ====================================================
        # АВТОРИЗОВАН — ВСЕ КОМАНДЫ
        # ====================================================
        nickname = user["nickname"]

        # ===== ФОТО (обои) =====
        if attachments and 'photo' in str(attachments):
            try:
                for att in attachments:
                    if att['type'] == 'photo':
                        owner_id = att['photo']['owner_id']
                        photo_id = att['photo']['id']
                        photo_info = vk.photos.getById(photos=f"{owner_id}_{photo_id}")[0]
                        sizes = photo_info['sizes']
                        max_size = max(sizes, key=lambda x: x['width'])
                        url = max_size['url']

                        send_message(user_id, "⏳ Устанавливаю обои...")
                        result = commands.set_wallpaper_url(url)
                        send_message(user_id, f"✅ {result}")
                        break
            except Exception as e:
                send_message(user_id, f"❌ Ошибка: {e}")
            continue

        # ===== ГЛАВНОЕ МЕНЮ =====
        if text_lower in ["/start", "начать", "привет", "меню", "/menu"]:
            send_message(user_id, f"🔥 Привет, {nickname}!\nГлавное меню:", kb_main())

        elif text_lower == "➡️ программы":
            send_message(user_id, "📁 Программы:", kb_programs())

        elif text_lower == "➡️ приколы":
            send_message(user_id, "🎭 Приколы:", kb_jokes())

        elif text_lower == "➡️ система":
            send_message(user_id, "🛠️ Система:", kb_system())

        elif text_lower == "➡️ сайты":
            send_message(user_id, "🌐 Сайты:", kb_sites())

        elif text_lower == "👤 профиль":
            send_message(user_id, "👤 Профиль:", kb_profile())

        elif text_lower == "⬅️ назад":
            send_message(user_id, "🔥 Главное меню:", kb_main())

        # ===== ПРОФИЛЬ =====
        elif text_lower == "👤 мой профиль":
            avatar_info = "Есть" if user.get("avatar") else "Нет"
            send_message(user_id,
                f"👤 Твой профиль:\n\n"
                f"Имя: {user['name']}\n"
                f"Никнейм: {user['nickname']}\n"
                f"Email: {user['email']}\n"
                f"Аватарка: {avatar_info}\n"
                f"VK ID: {user.get('vk_id', 'не привязан')}"
            )

        elif text_lower == "🔗 отвязать vk":
            success, msg = auth.unlink_vk(user["id"])
            if success:
                send_message(user_id, "✅ VK отвязан. Напиши /start чтобы войти снова.")
            else:
                send_message(user_id, f"❌ {msg}")

        # ===== ПОМОЩЬ =====
        elif text_lower == "❓ помощь" or text_lower == "/help":
            send_message(user_id, f"""
📋 FSOCIETY VK BOT

👤 Ты вошёл как: {nickname}

🔹 Управление:
/start — меню
/help — помощь
/screenshot — скриншот
/shutdown — выключить
/restart — перезагрузить
/lock — блокировка
/status — статус ПК

🔹 Сайты:
/site <url> — открыть сайт
/sites <url1,url2> — несколько

🔹 Обои:
/wallpaper <url> — по ссылке
→ или отправь фото в чат

🔹 Своя команда:
/cmd <команда> — выполнить
/list — все команды
            """)

        # ===== СКРИНШОТ =====
        elif text_lower == "📸 скриншот" or text_lower == "/screenshot":
            try:
                send_message(user_id, "📸 Делаю скриншот...")
                img = ImageGrab.grab()
                path = f"screenshot_{int(time.time())}.png"
                img.save(path)
                send_photo(user_id, path)
                os.remove(path)
            except Exception as e:
                send_message(user_id, f"❌ Ошибка: {e}")

        # ===== СТАТУС =====
        elif text_lower == "📊 статус" or text_lower == "/status":
            send_message(user_id, commands.get_status())

        # ===== ПИТАНИЕ =====
        elif text_lower == "⛔ выключить" or text_lower == "/shutdown":
            send_message(user_id, commands.shutdown())

        elif text_lower == "🔄 перезагрузить" or text_lower == "/restart":
            send_message(user_id, commands.restart())

        elif text_lower == "🔒 блокировка" or text_lower == "/lock":
            send_message(user_id, commands.lock_pc())

        # ===== ОБОИ =====
        elif text_lower == "🖼️ обои":
            send_message(user_id, "🖼️ Отправь фото или /wallpaper <url>")

        elif text_lower.startswith("/wallpaper "):
            url = text.split(" ", 1)[1]
            send_message(user_id, commands.set_wallpaper_url(url))

        # ===== САЙТЫ =====
        elif text_lower.startswith("/site "):
            url = text.split(" ", 1)[1]
            send_message(user_id, commands.open_url(url))

        elif text_lower.startswith("/sites "):
            urls = text.split(" ", 1)[1].split(",")
            for u in urls:
                u = u.strip()
                if not u.startswith("http"):
                    u = "https://" + u
                commands.open_url(u)
                time.sleep(0.5)
            send_message(user_id, f"🌐 Открыто {len(urls)} сайтов!")

        # ===== CMD =====
        elif text_lower.startswith("/cmd "):
            cmd = text.split(" ", 1)[1]
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                output = result.stdout or result.stderr or "OK"
                send_message(user_id, f"💻 {output[:3000]}")
            except Exception as e:
                send_message(user_id, f"❌ Ошибка: {e}")

        # ===== СПИСОК КОМАНД =====
        elif text_lower == "/list":
            all_cmds = commands.get_all_commands()
            chunks = [all_cmds[i:i+50] for i in range(0, len(all_cmds), 50)]
            send_message(user_id, f"📋 Всего команд: {len(all_cmds)}")
            for chunk in chunks[:3]:
                send_message(user_id, "• " + "\n• ".join(chunk))

        # ===== ПРОГРАММЫ =====
        elif text_lower == "💻 cmd":
            send_message(user_id, commands.open_cmd())
        elif text_lower == "⚡ powershell":
            send_message(user_id, commands.open_powershell())
        elif text_lower == "📝 блокнот":
            send_message(user_id, commands.open_notepad())
        elif text_lower == "🧮 калькулятор":
            send_message(user_id, commands.open_calc())
        elif text_lower == "📂 проводник":
            send_message(user_id, commands.open_explorer())
        elif text_lower == "📊 диспетчер задач":
            send_message(user_id, commands.open_taskmgr())
        elif text_lower == "🎨 paint":
            send_message(user_id, commands.open_paint())
        elif text_lower == "✂️ ножницы":
            send_message(user_id, commands.open_snippingtool())
        elif text_lower == "⚙️ панель управления":
            send_message(user_id, commands.open_control())
        elif text_lower == "🖥️ устройства":
            send_message(user_id, commands.open_devmgmt())

        # ===== ПРИКОЛЫ =====
        elif text_lower == "🎵 рикролл":
            send_message(user_id, commands.open_rickroll())
        elif text_lower == "🎵 рикролл x5":
            send_message(user_id, commands.open_rickroll_5())
        elif text_lower == "🎵 рикролл x10":
            send_message(user_id, commands.open_rickroll_10())
        elif text_lower == "🦊 firefox x10":
            send_message(user_id, commands.open_firefox_10())
        elif text_lower == "🌐 chrome x10":
            send_message(user_id, commands.open_chrome_10())
        elif text_lower == "📝 блокнот x10":
            send_message(user_id, commands.open_notepad_10())
        elif text_lower == "💀 убить explorer":
            send_message(user_id, commands.kill_explorer())
        elif text_lower == "🔄 восст. explorer":
            send_message(user_id, commands.restore_explorer())
        elif text_lower == "🔊 макс. громкость":
            send_message(user_id, commands.max_volume())
        elif text_lower == "🔇 отключить звук":
            send_message(user_id, commands.mute_volume())

        # ===== СИСТЕМА =====
        elif text_lower == "⚡ cpu":
            send_message(user_id, commands.get_cpu())
        elif text_lower == "🧠 ram":
            send_message(user_id, commands.get_ram())
        elif text_lower == "💾 диск":
            send_message(user_id, commands.get_disk())
        elif text_lower == "🔋 батарея":
            send_message(user_id, commands.get_battery())
        elif text_lower == "⏱️ аптайм":
            send_message(user_id, commands.get_uptime())
        elif text_lower == "📋 процессы":
            send_message(user_id, commands.list_processes())
        elif text_lower == "🌐 ip":
            send_message(user_id, commands.get_ip())
        elif text_lower == "📡 ping google":
            send_message(user_id, commands.ping_google())
        elif text_lower == "🔄 flush dns":
            send_message(user_id, commands.flush_dns())
        elif text_lower == "🧹 очистка temp":
            send_message(user_id, commands.clean_temp())
        elif text_lower == "🗑️ очистка корзины":
            send_message(user_id, commands.empty_recycle())

        # ===== САЙТЫ (КНОПКИ) =====
        elif text_lower == "📺 youtube":
            send_message(user_id, commands.open_youtube())
        elif text_lower == "🔍 google":
            send_message(user_id, commands.open_google())
        elif text_lower == "📱 vk":
            send_message(user_id, commands.open_vk())
        elif text_lower == "🐙 github":
            send_message(user_id, commands.open_github())
        elif text_lower == "🎮 twitch":
            send_message(user_id, commands.open_twitch())
        elif text_lower == "💬 discord":
            send_message(user_id, commands.open_discord())
        elif text_lower == "✈️ telegram":
            send_message(user_id, commands.open_telegram())
        elif text_lower == "👽 reddit":
            send_message(user_id, commands.open_reddit())
        elif text_lower == "🤖 chatgpt":
            send_message(user_id, commands.open_chatgpt())
        elif text_lower == "📚 wikipedia":
            send_message(user_id, commands.open_wikipedia())

        # ===== НЕИЗВЕСТНАЯ =====
        else:
            send_message(user_id, "❌ Неизвестная команда.\nНапиши /help или /start")