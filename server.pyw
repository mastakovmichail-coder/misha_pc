# -*- coding: utf-8 -*-
"""
server.pyw — HTTP-сервер для FSOCIETY PC CONTROL
Поддерживает: сайт, команды, регистрацию, вход
"""

import http.server
import socketserver
import urllib.parse
import json
import os
import sys
import webbrowser
import base64
import threading
import time

# ===== ИМПОРТЫ =====
try:
    import commands
    import auth
except ImportError as e:
    print(f"❌ Ошибка: {e}")
    print("Убедись, что commands.py и auth.py лежат рядом с server.pyw")
    input("Нажми Enter для выхода...")
    sys.exit(1)

# ===== ПУТЬ К ПАПКЕ =====
if getattr(sys, 'frozen', False):
    DIRECTORY = os.path.dirname(sys.executable)
else:
    DIRECTORY = os.path.dirname(os.path.abspath(__file__))
os.chdir(DIRECTORY)

# ===== НАСТРОЙКИ =====
PORT = 8080

# ============================================================
# ОБРАБОТЧИК
# ============================================================
class MyHandler(http.server.BaseHTTPRequestHandler):
    
    def log_message(self, format, *args):
        pass  # отключаем логи
    
    # --------------------------------------------------------
    # GET-ЗАПРОСЫ
    # --------------------------------------------------------
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)
        
        # ===== ГЛАВНАЯ =====
        if path == "/" or path == "/index.html":
            self.serve_file("index.html", "text/html")
            return
        
        # ===== СТРАНИЦА РЕГИСТРАЦИИ =====
        if path == "/register" or path == "/register.html":
            self.serve_file("register.html", "text/html")
            return
        
        # ===== СТРАНИЦА ВХОДА =====
        if path == "/login" or path == "/login.html":
            self.serve_file("login.html", "text/html")
            return
        
        # ===== ВЫПОЛНЕНИЕ КОМАНДЫ =====
        if path == "/run":
            cmd = query.get("cmd", [""])[0]
            args = query.get("args", [""])[0]
            
            if not cmd:
                self.send_json({"ok": False, "error": "No command"})
                return
            
            arg_list = []
            if args:
                arg_list = [a.strip() for a in args.split(",")]
            
            try:
                result = commands.execute(cmd, *arg_list)
                self.send_json({"ok": True, "result": str(result)})
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)})
            return
        
        # ===== СПИСОК КОМАНД =====
        if path == "/commands":
            try:
                all_cmds = commands.get_all_commands()
                self.send_json({"ok": True, "commands": all_cmds, "count": len(all_cmds)})
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)})
            return
        
        # ===== СТАТУС =====
        if path == "/status":
            try:
                status = commands.get_status()
                self.send_json({"ok": True, "status": status})
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)})
            return
        
        # ===== СКРИНШОТ =====
        if path == "/screenshot":
            try:
                import io
                from PIL import ImageGrab
                img = ImageGrab.grab()
                img_bytes = io.BytesIO()
                img.save(img_bytes, format="JPEG", quality=50)
                img_bytes.seek(0)
                
                self.send_response(200)
                self.send_header("Content-type", "image/jpeg")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                self.wfile.write(img_bytes.read())
            except Exception as e:
                self.send_error(500, str(e))
            return
        
        # ===== ПОЛУЧИТЬ ПОЛЬЗОВАТЕЛЯ =====
        if path == "/user":
            user_id = query.get("id", [""])[0]
            if user_id:
                user = auth.get_user(user_id)
                if user:
                    self.send_json({"ok": True, "user": user})
                else:
                    self.send_json({"ok": False, "error": "Пользователь не найден"})
            else:
                self.send_json({"ok": False, "error": "No id"})
            return
        
        # ===== АВАТАРКА =====
        if path.startswith("/avatars/"):
            avatar_name = path.split("/")[-1]
            avatar_path = os.path.join("avatars", avatar_name)
            if os.path.exists(avatar_path):
                self.serve_file(avatar_path, "image/png")
            else:
                self.send_error(404)
            return
        
        # ===== 404 =====
        self.send_error(404, "Not Found")
    
    # --------------------------------------------------------
    # POST-ЗАПРОСЫ
    # --------------------------------------------------------
    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        
        # Читаем тело
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode("utf-8")) if post_data else {}
        except Exception as e:
            self.send_json({"ok": False, "error": f"JSON error: {e}"})
            return
        
        # ===== РЕГИСТРАЦИЯ ШАГ 1 =====
        if path == "/register_step1":
            try:
                success, msg = auth.register_step1(
                    name=data.get("name", ""),
                    nickname=data.get("nickname", ""),
                    email=data.get("email", ""),
                    password=data.get("password", ""),
                    password2=data.get("password2", ""),
                    avatar_base64=data.get("avatar", None)
                )
                self.send_json({"ok": success, "message": msg})
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)})
            return
        
        # ===== РЕГИСТРАЦИЯ ШАГ 2 =====
        if path == "/register_step2":
            try:
                success, msg = auth.register_step2(
                    email=data.get("email", ""),
                    code=data.get("code", "")
                )
                self.send_json({"ok": success, "message": msg})
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)})
            return
        
        # ===== ВХОД ШАГ 1 =====
        if path == "/login_step1":
            try:
                success, msg = auth.login_step1(
                    nickname=data.get("nickname", ""),
                    password=data.get("password", "")
                )
                self.send_json({"ok": success, "message": msg})
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)})
            return
        
        # ===== ВХОД ШАГ 2 =====
        if path == "/login_step2":
            try:
                email = data.get("email", "")
                code = data.get("code", "")
                success, result = auth.login_step2(email, code)
                
                if success:
                    self.send_json({"ok": True, "user": result, "message": "Вход выполнен"})
                else:
                    self.send_json({"ok": False, "error": result})
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)})
            return
        
        # ===== ЗАГРУЗКА ФАЙЛА =====
        if path == "/upload":
            try:
                filename = data.get("name", "file.bin")
                filedata = data.get("data", "")
                file_bytes = base64.b64decode(filedata)
                
                save_dir = os.path.join(os.path.expanduser("~"), "Downloads")
                os.makedirs(save_dir, exist_ok=True)
                file_path = os.path.join(save_dir, filename)
                
                with open(file_path, "wb") as f:
                    f.write(file_bytes)
                
                if data.get("run", False):
                    os.startfile(file_path)
                
                self.send_json({"ok": True, "path": file_path})
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)})
            return
        
        # ===== ЗАГРУЗКА ОБОЕВ =====
        if path == "/upload_wallpaper":
            try:
                import ctypes
                from io import BytesIO
                from PIL import Image
                
                filedata = data.get("data", "")
                file_bytes = base64.b64decode(filedata)
                
                img = Image.open(BytesIO(file_bytes)).convert("RGB")
                path = os.path.join(os.environ["TEMP"], "wallpaper_upload.jpg")
                img.save(path, "JPEG", quality=95)
                
                ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 3)
                
                self.send_json({"ok": True, "result": "Обои установлены"})
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)})
            return
        
        self.send_error(404)
    
    # --------------------------------------------------------
    # ВСПОМОГАТЕЛЬНЫЕ
    # --------------------------------------------------------
    def serve_file(self, filepath, content_type):
        """Отдаёт файл"""
        if not os.path.exists(filepath):
            self.send_error(404)
            return
        
        with open(filepath, "rb") as f:
            content = f.read()
        
        self.send_response(200)
        self.send_header("Content-type", f"{content_type}; charset=utf-8")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(content)
    
    def send_json(self, data):
        """Отправляет JSON"""
        self.send_response(200)
        self.send_header("Content-type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))


# ============================================================
# ПОИСК СВОБОДНОГО ПОРТА
# ============================================================
def find_free_port(start_port=8080, max_port=8200):
    for port in range(start_port, max_port):
        try:
            with socketserver.TCPServer(("0.0.0.0", port), MyHandler) as test:
                test.server_close()
                return port
        except OSError:
            continue
    return None


def get_local_ip():
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"


# ============================================================
# ЗАПУСК
# ============================================================
def main():
    print("=" * 60)
    print("🔥 FSOCIETY PC CONTROL — СЕРВЕР")
    print("=" * 60)
    print(f"📁 Папка: {DIRECTORY}")
    print(f"📋 Команд: {commands.get_commands_count()}")
    print(f"👥 Пользователей: {len(auth.load_users())}")
    print()
    
    port = find_free_port(PORT)
    if port is None:
        print("❌ Не найден свободный порт")
        input("Enter для выхода...")
        return
    
    local_ip = get_local_ip()
    
    print(f"✅ Сервер запущен!")
    print(f"🌐 Локально:     http://localhost:{port}")
    print(f"📱 На телефоне:  http://{local_ip}:{port}")
    print(f"🔐 Регистрация:  http://localhost:{port}/register")
    print(f"🔑 Вход:         http://localhost:{port}/login")
    print()
    print("🔒 Ctrl+C для остановки")
    print("=" * 60)
    
    try:
        with socketserver.TCPServer(("0.0.0.0", port), MyHandler) as httpd:
            webbrowser.open(f"http://localhost:{port}")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n⛔ Сервер остановлен")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        input("Enter для выхода...")


if __name__ == "__main__":
    main()