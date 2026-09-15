# -*- coding: utf-8 -*-
"""
auth.py — Модуль регистрации и входа для FSOCIETY PC CONTROL
Отправка кодов на email через Gmail SMTP
Привязка VK к аккаунту сайта
"""

import os
import json
import random
import smtplib
import time
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ============================================================
# НАСТРОЙКИ GMAIL
# ============================================================
GMAIL_USER = "fsociety.bot267@gmail.com"
GMAIL_PASS = "hnaupyrsnozgqkdq"  # 16 символов без пробелов
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# ============================================================
# ФАЙЛЫ
# ============================================================
USERS_FILE = "users.json"
AVATARS_DIR = "avatars"
CODE_LIFETIME = 300  # 5 минут

# Создаём папку для аватарок
os.makedirs(AVATARS_DIR, exist_ok=True)

# Хранилище кодов: {email: {"code": "...", "time": ..., "type": "...", "data": {...}}}
pending_codes = {}

# ============================================================
# РАБОТА С ПОЛЬЗОВАТЕЛЯМИ
# ============================================================
def load_users():
    """Загружает пользователей из users.json"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users(users):
    """Сохраняет пользователей в users.json"""
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

# ============================================================
# ГЕНЕРАЦИЯ КОДА
# ============================================================
def generate_code():
    """Генерирует 6-значный код"""
    return str(random.randint(100000, 999999))

# ============================================================
# ОТПРАВКА EMAIL
# ============================================================
def send_email(to_email, code, code_type="register"):
    """Отправляет код на email"""
    try:
        if code_type == "register":
            subject = "FSOCIETY — Код регистрации"
            action = "Ты регистрируешься на нашей платформе."
        elif code_type == "vk_login":
            subject = "FSOCIETY — Вход через VK"
            action = "Ты входишь в VK-бота FSOCIETY."
        else:
            subject = "FSOCIETY — Код входа"
            action = "Ты входишь в свой аккаунт."

        text = f"""
        <html>
        <body style="background:#0a0a0f;color:#00ff88;font-family:monospace;padding:30px;">
            <h1 style="color:#00ff88;">FSOCIETY // PC CONTROL</h1>
            <p>Привет!</p>
            <p>{action}</p>
            <p>Твой код подтверждения:</p>
            <h1 style="color:#ff3366;font-size:36px;letter-spacing:8px;">{code}</h1>
            <p>Код действует 5 минут.</p>
            <p>Если это не ты — просто проигнорируй это письмо.</p>
            <hr style="border-color:#00ff8844;">
            <p style="color:#666;font-size:12px;">FSOCIETY PC CONTROL</p>
        </body>
        </html>
        """

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = GMAIL_USER
        msg["To"] = to_email

        html_part = MIMEText(text, "html", "utf-8")
        msg.attach(html_part)

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASS)
        server.sendmail(GMAIL_USER, to_email, msg.as_string())
        server.quit()

        return True, "Код отправлен на email"

    except smtplib.SMTPAuthenticationError:
        return False, "Ошибка авторизации Gmail. Проверь пароль приложения."
    except smtplib.SMTPException as e:
        return False, f"Ошибка SMTP: {e}"
    except Exception as e:
        return False, f"Ошибка: {e}"

# ============================================================
# РЕГИСТРАЦИЯ (САЙТ)
# ============================================================
def register_step1(name, nickname, email, password, password2, avatar_base64=None):
    """Шаг 1 регистрации: проверка данных и отправка кода"""
    if not name or not nickname or not email or not password:
        return False, "Заполни все поля"

    if password != password2:
        return False, "Пароли не совпадают"

    if len(password) < 4:
        return False, "Пароль слишком короткий (минимум 4 символа)"

    if "@" not in email:
        return False, "Неверный email"

    users = load_users()

    for u in users.values():
        if u.get("nickname", "").lower() == nickname.lower():
            return False, "Такой никнейм уже занят"

    for u in users.values():
        if u.get("email", "").lower() == email.lower():
            return False, "Такая почта уже используется"

    # Сохраняем аватарку
    avatar_path = None
    if avatar_base64:
        try:
            if "," in avatar_base64:
                avatar_base64 = avatar_base64.split(",")[1]

            avatar_bytes = base64.b64decode(avatar_base64)
            avatar_path = os.path.join(AVATARS_DIR, f"{nickname}.png")
            with open(avatar_path, "wb") as f:
                f.write(avatar_bytes)
        except Exception as e:
            return False, f"Ошибка аватарки: {e}"

    code = generate_code()

    pending_codes[email] = {
        "code": code,
        "time": time.time(),
        "type": "register",
        "data": {
            "name": name,
            "nickname": nickname,
            "email": email,
            "password": password,
            "avatar": avatar_path
        }
    }

    success, msg = send_email(email, code, "register")
    if not success:
        return False, msg

    return True, "Код отправлен на email"

def register_step2(email, code):
    """Шаг 2 регистрации: проверка кода и создание аккаунта"""
    if email not in pending_codes:
        return False, "Сначала заполни форму регистрации"

    pending = pending_codes[email]

    if time.time() - pending["time"] > CODE_LIFETIME:
        del pending_codes[email]
        return False, "Код истёк. Запроси новый."

    if pending["code"] != code:
        return False, "Неверный код"

    users = load_users()
    user_id = str(int(time.time()))

    users[user_id] = {
        "id": user_id,
        "name": pending["data"]["name"],
        "nickname": pending["data"]["nickname"],
        "email": pending["data"]["email"],
        "password": pending["data"]["password"],
        "avatar": pending["data"]["avatar"],
        "vk_id": None,
        "created": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    save_users(users)
    del pending_codes[email]

    return True, f"Регистрация успешна! Добро пожаловать, {pending['data']['nickname']}"

# ============================================================
# ВХОД (САЙТ)
# ============================================================
def login_step1(nickname, password):
    """Шаг 1 входа: проверка никнейма и пароля, отправка кода"""
    if not nickname or not password:
        return False, "Заполни все поля"

    users = load_users()

    found_user = None
    for u in users.values():
        if u.get("nickname", "").lower() == nickname.lower():
            found_user = u
            break

    if not found_user:
        return False, "Пользователь не найден"

    if found_user["password"] != password:
        return False, "Неверный пароль"

    code = generate_code()
    email = found_user["email"]

    pending_codes[email] = {
        "code": code,
        "time": time.time(),
        "type": "login",
        "user_id": found_user["id"]
    }

    success, msg = send_email(email, code, "login")
    if not success:
        return False, msg

    return True, "Код отправлен на email"

def login_step2(nickname, code):
    """Шаг 2 входа: проверка кода по nickname"""
    users = load_users()

    found_user = None
    for u in users.values():
        if u.get("nickname", "").lower() == nickname.lower():
            found_user = u
            break

    if not found_user:
        return False, "Пользователь не найден"

    email = found_user["email"]

    if email not in pending_codes:
        return False, "Сначала введи никнейм и пароль"

    pending = pending_codes[email]

    if time.time() - pending["time"] > CODE_LIFETIME:
        del pending_codes[email]
        return False, "Код истёк. Запроси новый."

    if pending["code"] != code:
        return False, "Неверный код"

    user_id = pending["user_id"]
    del pending_codes[email]

    return True, {"user_id": user_id, "message": "Вход выполнен"}

# ============================================================
# VK-ВХОД (ПРИВЯЗКА)
# ============================================================
def vk_login_step1(nickname):
    """Шаг 1 VK-входа: проверка никнейма, отправка кода"""
    if not nickname:
        return False, "Введи никнейм"

    users = load_users()

    found_user = None
    for u in users.values():
        if u.get("nickname", "").lower() == nickname.lower():
            found_user = u
            break

    if not found_user:
        return False, "Пользователь не найден. Зарегистрируйся на сайте."

    code = generate_code()
    email = found_user["email"]

    pending_codes[email] = {
        "code": code,
        "time": time.time(),
        "type": "vk_login",
        "user_id": found_user["id"]
    }

    success, msg = send_email(email, code, "vk_login")
    if not success:
        return False, msg

    return True, "Код отправлен на email"

def vk_login_step2(nickname, code, vk_id):
    """Шаг 2 VK-входа: проверка кода, привязка VK ID"""
    users = load_users()

    found_user = None
    for u in users.values():
        if u.get("nickname", "").lower() == nickname.lower():
            found_user = u
            break

    if not found_user:
        return False, "Пользователь не найден"

    email = found_user["email"]

    if email not in pending_codes:
        return False, "Сначала введи никнейм"

    pending = pending_codes[email]

    if time.time() - pending["time"] > CODE_LIFETIME:
        del pending_codes[email]
        return False, "Код истёк"

    if pending["code"] != code:
        return False, "Неверный код"

    # Привязываем VK ID к аккаунту
    user_id = pending["user_id"]
    users[user_id]["vk_id"] = str(vk_id)
    save_users(users)

    del pending_codes[email]

    return True, {"user_id": user_id, "vk_id": vk_id, "message": "Вход выполнен"}

# ============================================================
# ПОИСК ПОЛЬЗОВАТЕЛЯ
# ============================================================
def get_user(user_id):
    """Возвращает данные пользователя по ID"""
    users = load_users()
    if user_id in users:
        u = users[user_id]
        return {
            "id": u["id"],
            "name": u["name"],
            "nickname": u["nickname"],
            "email": u["email"],
            "avatar": u["avatar"],
            "vk_id": u.get("vk_id")
        }
    return None

def get_user_by_nickname(nickname):
    """Возвращает данные пользователя по никнейму"""
    users = load_users()
    for u in users.values():
        if u.get("nickname", "").lower() == nickname.lower():
            return {
                "id": u["id"],
                "name": u["name"],
                "nickname": u["nickname"],
                "email": u["email"],
                "avatar": u["avatar"],
                "vk_id": u.get("vk_id")
            }
    return None

def get_user_by_vk(vk_id):
    """Возвращает пользователя по VK ID"""
    users = load_users()
    for u in users.values():
        if str(u.get("vk_id", "")) == str(vk_id):
            return {
                "id": u["id"],
                "name": u["name"],
                "nickname": u["nickname"],
                "email": u["email"],
                "avatar": u["avatar"],
                "vk_id": u.get("vk_id")
            }
    return None

# ============================================================
# ОТВЯЗКА VK
# ============================================================
def unlink_vk(user_id):
    """Отвязывает VK от аккаунта"""
    users = load_users()
    if user_id in users:
        users[user_id]["vk_id"] = None
        save_users(users)
        return True, "VK отвязан"
    return False, "Пользователь не найден"