# -*- coding: utf-8 -*-
"""FSOCIETY Messenger v7.1 — Speeky-Style (Fixed Painter Conflict)"""
import sys, os, json, hashlib, sqlite3, datetime, random, shutil, socket, threading, time, subprocess, math
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QGraphicsOpacityEffect,
    QListWidget, QListWidgetItem, QTextEdit, QScrollArea,
    QFrame, QStackedWidget, QCheckBox, QComboBox, QSlider,
    QSpinBox, QFileDialog, QMessageBox, QMenu, QDialog,
    QFormLayout, QGroupBox, QTabWidget, QGridLayout, QInputDialog
)
from PyQt6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QTimer, QSize,
    QPoint, QPointF, QRect, QRectF, pyqtSignal, QThread
)
from PyQt6.QtGui import (
    QFont, QIcon, QPixmap, QColor, QPalette, QAction,
    QMovie, QCursor, QPainter, QImage, QLinearGradient, QBrush,
    QPen, QRadialGradient
)

# ===== МОДУЛИ =====
try:
    from calls import CallDialog
    CALLS_OK = True
except ImportError:
    CALLS_OK = False

try:
    import commands
    COMMANDS_OK = True
except ImportError:
    COMMANDS_OK = False

try:
    import vk_bot
    VK_BOT_OK = True
except ImportError:
    VK_BOT_OK = False

APP = "FSOCIETY"
APP_VERSION = "7.1.0"
DEV_EMAIL = "mastakov.michail@gmail.com"
DB_PATH = "messenger.db"
CFG_PATH = "config.json"
STICKERS_DIR = "stickers"
GIFS_DIR = "gifs"
AVATARS_DIR = "avatars"
DOWNLOADS_DIR = "downloads"

for d in [STICKERS_DIR, GIFS_DIR, AVATARS_DIR, DOWNLOADS_DIR]:
    os.makedirs(d, exist_ok=True)

# ============================================================
# ПАЛИТРЫ
# ============================================================
PALETTES = {
    "speeky_blue": {
        "name": "🌌 Speeky Blue",
        "bg": ("#0A0E1A", "#0F1420"),
        "card": "#141A28", "card2": "#1E2438",
        "text": "#EAF0FF", "text2": "#7A8BA8",
        "accent1": "#5B8DEF", "accent2": "#3D6FE8", "accent_hover": "#7BA5FF",
        "danger": "#FF5C7C", "warning": "#FFB84D", "success": "#4ADE80",
        "bubble_me1": "#3D6FE8", "bubble_me2": "#5B8DEF",
    },
    "speeky_purple": {
        "name": "💜 Speeky Purple",
        "bg": ("#0F0A1A", "#150F25"),
        "card": "#1A1428", "card2": "#241A38",
        "text": "#F0E8FF", "text2": "#9080B0",
        "accent1": "#A855F7", "accent2": "#8B3FE8", "accent_hover": "#C084FC",
        "danger": "#FF5C7C", "warning": "#FFB84D", "success": "#4ADE80",
        "bubble_me1": "#8B3FE8", "bubble_me2": "#A855F7",
    },
    "speeky_green": {
        "name": "🌿 Speeky Green",
        "bg": ("#08140E", "#0F1A14"),
        "card": "#0E1F18", "card2": "#14302A",
        "text": "#E8FFF0", "text2": "#80A890",
        "accent1": "#10B981", "accent2": "#059669", "accent_hover": "#34D399",
        "danger": "#FF5C7C", "warning": "#FFB84D", "success": "#4ADE80",
        "bubble_me1": "#059669", "bubble_me2": "#10B981",
    },
    "speeky_sunset": {
        "name": "🌅 Speeky Sunset",
        "bg": ("#1A0A12", "#25101C"),
        "card": "#2A1420", "card2": "#3A1C2E",
        "text": "#FFE8EC", "text2": "#B08090",
        "accent1": "#F43F5E", "accent2": "#E11D48", "accent_hover": "#FB7185",
        "danger": "#FF5C7C", "warning": "#FFB84D", "success": "#4ADE80",
        "bubble_me1": "#E11D48", "bubble_me2": "#F43F5E",
    },
}

def get_palette(name):
    return PALETTES.get(name, PALETTES["speeky_blue"])

# ============================================================
# ANIMATED BACKGROUND (упрощённый, без blobs)
# ============================================================
class AnimatedBackground(QWidget):
    def __init__(self, parent=None, palette_key="speeky_blue"):
        super().__init__(parent)
        self.palette_key = palette_key
        self.t = 0.0
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(90)  # 11 FPS

    def set_palette(self, key):
        self.palette_key = key
        self.update()

    def _tick(self):
        self.t += 0.03
        if self.t > 2 * math.pi:
            self.t -= 2 * math.pi
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        pal = get_palette(self.palette_key)
        c1 = QColor(pal["bg"][0])
        c2 = QColor(pal["bg"][1])

        # Плавная пульсация между 2 цветами
        k = 0.5 + 0.5 * math.sin(self.t)
        mix_r = int(c1.red() + (c2.red() - c1.red()) * k)
        mix_g = int(c1.green() + (c2.green() - c1.green()) * k)
        mix_b = int(c1.blue() + (c2.blue() - c1.blue()) * k)
        mix = QColor(mix_r, mix_g, mix_b)

        grad = QLinearGradient(0, 0, w, h)
        grad.setColorAt(0.0, c1)
        grad.setColorAt(0.5, mix)
        grad.setColorAt(1.0, c2)
        p.fillRect(self.rect(), QBrush(grad))
        p.end()

# ============================================================
# GLASS CARD (QSS-версия)
# ============================================================
class GlassCard(QFrame):
    def __init__(self, parent=None, palette_key="speeky_blue", radius=28):
        super().__init__(parent)
        self.palette_key = palette_key
        self.radius = radius
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._apply_style()

    def set_palette(self, key):
        self.palette_key = key
        self._apply_style()

    def _apply_style(self):
        pal = get_palette(self.palette_key)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {pal['card']};
                border: 1.5px solid rgba(255, 255, 255, 22);
                border-radius: {self.radius}px;
            }}
        """)

# ============================================================
# GLOW BUTTON (QSS-версия)
# ============================================================
class GlowButton(QPushButton):
    def __init__(self, text="", parent=None, palette_key="speeky_blue"):
        super().__init__(text, parent)
        self.palette_key = palette_key
        self.setMinimumHeight(54)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_style()

    def set_palette(self, key):
        self.palette_key = key
        self._apply_style()

    def _apply_style(self):
        pal = get_palette(self.palette_key)
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {pal['accent1']}, stop:1 {pal['accent2']});
                border: none;
                border-radius: 16px;
                padding: 14px 28px;
                color: white;
                font-size: 14px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {pal['accent_hover']}, stop:1 {pal['accent1']});
            }}
            QPushButton:pressed {{
                background: {pal['accent2']};
            }}
        """)

# ============================================================
# CIRCLE ICON BUTTON (QSS-версия)
# ============================================================
class CircleIconButton(QPushButton):
    def __init__(self, text="", parent=None, palette_key="speeky_blue", size=46):
        super().__init__(text, parent)
        self.palette_key = palette_key
        self.setFixedSize(size, size)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_style()

    def set_palette(self, key):
        self.palette_key = key
        self._apply_style()

    def _apply_style(self):
        pal = get_palette(self.palette_key)
        r = self.width() // 2
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(255, 255, 255, 15);
                border: 1.5px solid rgba(255, 255, 255, 25);
                border-radius: {r}px;
                color: {pal['text']};
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: {pal['accent2']};
                border: 1.5px solid {pal['accent1']};
                color: white;
            }}
        """)

# ============================================================
# GRADIENT TITLE (paintEvent, но без дочерних виджетов — ок)
# ============================================================
class GradientTitle(QLabel):
    def __init__(self, text="", parent=None, size=36, palette_key="speeky_blue"):
        super().__init__(text, parent)
        self.palette_key = palette_key
        self.size = size
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def set_palette(self, key):
        self.palette_key = key
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        pal = get_palette(self.palette_key)

        grad = QLinearGradient(0, 0, self.width(), 0)
        grad.setColorAt(0, QColor(pal["accent1"]))
        grad.setColorAt(1, QColor(pal["accent_hover"]))

        f = QFont("Inter", self.size, QFont.Weight.Black)
        f.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, -1.5)
        p.setFont(f)

        p.setPen(QPen(QBrush(grad), 1))
        p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())
        p.end()

# ============================================================
# GLASS INPUT (QSS)
# ============================================================
class GlassInput(QLineEdit):
    def __init__(self, placeholder="", parent=None, palette_key="speeky_blue"):
        super().__init__(parent)
        self.palette_key = palette_key
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(56)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._apply_style()

    def set_palette(self, key):
        self.palette_key = key
        self._apply_style()

    def _apply_style(self):
        pal = get_palette(self.palette_key)
        self.setStyleSheet(f"""
            QLineEdit {{
                background-color: rgba(30, 38, 55, 0.55);
                border: 1.5px solid rgba(255, 255, 255, 20);
                border-radius: 16px;
                padding: 14px 20px;
                color: {pal['text']};
                font-size: 14px;
                font-family: 'Inter', 'Segoe UI';
                selection-background-color: {pal['accent1']};
            }}
            QLineEdit:focus {{
                border: 1.5px solid {pal['accent1']};
                background-color: rgba(40, 50, 70, 0.7);
            }}
        """)

# ============================================================
# MESSAGE BUBBLE (QSS-версия)
# ============================================================
class MessageBubble(QFrame):
    def __init__(self, parent=None, is_me=False, palette_key="speeky_blue"):
        super().__init__(parent)
        self.is_me = is_me
        self.palette_key = palette_key
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setMaximumWidth(560)
        self._apply_style()

    def _apply_style(self):
        pal = get_palette(self.palette_key)
        if self.is_me:
            self.setStyleSheet(f"""
                QFrame {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {pal['bubble_me1']}, stop:1 {pal['bubble_me2']});
                    border-radius: 20px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {pal['card2']};
                    border: 1px solid rgba(255, 255, 255, 20);
                    border-radius: 20px;
                }}
            """)

# ============================================================
# CONFIG
# ============================================================
DEFAULT_CFG = {
    "theme": "speeky_blue",
    "font_size": 14, "animations": True, "notifications": True,
    "sounds": True, "message_preview": True, "call_notifications": True,
    "online_status": True, "read_receipts": True, "typing_indicator": True,
    "save_history": True, "video_calls": True, "audio_calls": True,
    "sticker_size": 128, "gif_autoplay": True, "enter_to_send": True,
    "dev_mode": False, "language": "ru", "auto_login": False,
    "last_user": "", "last_password": "", "remember_me": False,
    "server_port": 5555, "server_ip": "127.0.0.1",
    "vk_bot_enabled": True,
}

class Config:
    def __init__(self):
        self.data = dict(DEFAULT_CFG)
        self.load()
    def load(self):
        if os.path.exists(CFG_PATH):
            try:
                with open(CFG_PATH, "r", encoding="utf-8") as f:
                    self.data.update(json.load(f))
                if self.data.get("theme") not in PALETTES:
                    self.data["theme"] = "speeky_blue"
            except Exception:
                pass
    def save(self):
        try:
            with open(CFG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    def get(self, k, d=None): return self.data.get(k, d)
    def set(self, k, v): self.data[k] = v; self.save()

# ============================================================
# DB
# ============================================================
class DB:
    def __init__(self):
        self.c = sqlite3.connect(DB_PATH)
        self.cur = self.c.cursor()
        self.mk()
    def mk(self):
        self.cur.execute("""CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nickname TEXT UNIQUE, email TEXT UNIQUE,
            password TEXT, avatar TEXT,
            is_dev INTEGER DEFAULT 0, created TEXT)""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS messages(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT, receiver TEXT, text TEXT,
            created TEXT, is_group INTEGER DEFAULT 0)""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS groups(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE, creator TEXT, created TEXT)""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS group_members(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_name TEXT, member TEXT)""")
        self.c.commit()
    def h(self, p): return hashlib.sha256(p.encode()).hexdigest()
    def reg(self, n, e, p, dev=False):
        try:
            self.cur.execute(
                "INSERT INTO users(nickname,email,password,is_dev,created) VALUES(?,?,?,?,?)",
                (n, e, self.h(p), 1 if dev else 0,
                 datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            self.c.commit()
            return True, "OK"
        except sqlite3.IntegrityError as ex:
            if "nickname" in str(ex): return False, "Ник занят"
            if "email" in str(ex): return False, "Email занят"
            return False, str(ex)
    def login(self, l, p):
        self.cur.execute("SELECT * FROM users WHERE nickname=? OR email=?", (l, l))
        u = self.cur.fetchone()
        if not u: return None, "Не найден"
        if u[3] != self.h(p): return None, "Неверный пароль"
        return {"id": u[0], "nickname": u[1], "email": u[2],
                "avatar": u[4], "is_dev": bool(u[5])}, "OK"
    def save_msg(self, s, r, t, is_group=0):
        self.cur.execute(
            "INSERT INTO messages(sender,receiver,text,created,is_group) VALUES(?,?,?,?,?)",
            (s, r, t, datetime.datetime.now().strftime("%H:%M:%S"), is_group))
        self.c.commit()
    def find_user(self, query):
        self.cur.execute(
            "SELECT nickname, email, is_dev FROM users WHERE nickname LIKE ? OR email LIKE ?",
            (f"%{query}%", f"%{query}%"))
        return self.cur.fetchall()
    def create_group(self, name, creator):
        try:
            self.cur.execute(
                "INSERT INTO groups(name,creator,created) VALUES(?,?,?)",
                (name, creator, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            self.cur.execute(
                "INSERT INTO group_members(group_name,member) VALUES(?,?)",
                (name, creator))
            self.c.commit()
            return True, "OK"
        except sqlite3.IntegrityError:
            return False, "Группа уже существует"
    def get_groups(self, user):
        self.cur.execute("SELECT group_name FROM group_members WHERE member=?", (user,))
        return [r[0] for r in self.cur.fetchall()]

# ============================================================
# BOT
# ============================================================
class FSOCIETYBot:
    def __init__(self, db):
        self.db = db
        self.commands = {
            "/start": self.cmd_start, "/help": self.cmd_help,
            "/time": self.cmd_time, "/date": self.cmd_date,
            "/whoami": self.cmd_whoami, "/users": self.cmd_users,
            "/groups": self.cmd_groups, "/create_group": self.cmd_create_group,
            "/ping": self.cmd_ping, "/echo": self.cmd_echo,
        }
    def handle(self, text, user):
        text = text.strip()
        if not text.startswith("/"): return None
        parts = text.split(" ", 1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        if cmd in self.commands: return self.commands[cmd](args, user)
        return f"❌ Неизвестная команда: {cmd}\nНапиши /help"
    def cmd_start(self, args, user):
        return f"👋 Привет, {user['nickname']}!\n\nЯ — FSOCIETY Bot 🤖\nНапиши /help"
    def cmd_help(self, args, user):
        return ("📋 Команды:\n/start /help /time /date /whoami\n"
                "/users /groups /create_group <название>\n/ping /echo <текст>")
    def cmd_time(self, args, user): return f"🕐 {datetime.datetime.now().strftime('%H:%M:%S')}"
    def cmd_date(self, args, user): return f"📅 {datetime.datetime.now().strftime('%d.%m.%Y')}"
    def cmd_whoami(self, args, user):
        badge = " 🎖" if user.get("is_dev") else ""
        return f"👤 {user['nickname']}{badge}\n📧 {user['email']}"
    def cmd_users(self, args, user):
        self.db.cur.execute("SELECT nickname, is_dev FROM users")
        users = self.db.cur.fetchall()
        text = f"👥 Пользователи ({len(users)}):\n"
        for nick, dev in users: text += f"• {nick}{' 🎖' if dev else ''}\n"
        return text
    def cmd_groups(self, args, user):
        g = self.db.get_groups(user["nickname"])
        if not g: return "📭 У тебя нет групп."
        return "👥 Твои группы:\n" + "\n".join(f"• {x}" for x in g)
    def cmd_create_group(self, args, user):
        if not args: return "❌ /create_group <название>"
        ok, msg = self.db.create_group(args.strip(), user["nickname"])
        return f"✅ Группа «{args.strip()}» создана!" if ok else f"❌ {msg}"
    def cmd_ping(self, args, user): return "🏓 Pong!"
    def cmd_echo(self, args, user): return f"🔊 {args}" if args else "❌ /echo <текст>"

# ============================================================
# NETWORK
# ============================================================
class NetworkClient(QThread):
    message_received = pyqtSignal(str, str, str)
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    def __init__(self, host, port, nickname, parent=None):
        super().__init__(parent)
        self.host = host; self.port = port; self.nickname = nickname
        self.running = True; self.sock = None
    def run(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.sock.sendall(f"LOGIN:{self.nickname}\n".encode("utf-8"))
            self.connected.emit()
            buffer = ""
            while self.running:
                data = self.sock.recv(4096)
                if not data: break
                buffer += data.decode("utf-8", errors="ignore")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line.startswith("MSG:"):
                        parts = line[4:].split("|", 2)
                        if len(parts) == 3:
                            self.message_received.emit(parts[0], parts[1], parts[2])
        except Exception as e:
            print(f"Network error: {e}")
        finally:
            self.disconnected.emit()
    def send_message(self, text):
        if self.sock:
            try:
                msg = f"MSG:{self.nickname}|{text}|{datetime.datetime.now().strftime('%H:%M:%S')}\n"
                self.sock.sendall(msg.encode("utf-8"))
            except Exception: pass
    def stop(self):
        self.running = False
        if self.sock:
            try: self.sock.close()
            except Exception: pass

def run_server(port):
    clients = {}
    def handle(conn, addr):
        try:
            data = conn.recv(1024).decode("utf-8").strip()
            if data.startswith("LOGIN:"):
                nickname = data[6:]
                clients[nickname] = conn
                print(f"✅ {nickname} подключился")
                buffer = ""
                while True:
                    data = conn.recv(4096)
                    if not data: break
                    buffer += data.decode("utf-8", errors="ignore")
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        if line.startswith("MSG:"):
                            for nick, c in clients.items():
                                if nick != nickname:
                                    try: c.sendall((line + "\n").encode("utf-8"))
                                    except Exception: pass
        except Exception: pass
        finally:
            for nick, c in list(clients.items()):
                if c == conn: del clients[nick]
            try: conn.close()
            except Exception: pass
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind(("0.0.0.0", port))
        server.listen(10)
        print(f"🚀 Сервер на порту {port}")
    except Exception as e:
        print(f"❌ Сервер: {e}"); return
    while True:
        try:
            conn, addr = server.accept()
            threading.Thread(target=handle, args=(conn, addr), daemon=True).start()
        except Exception: break

# ============================================================
# STICKER / GIF PANELS
# ============================================================
class StickerPanel(QDialog):
    sticker_selected = pyqtSignal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cfg = parent.cfg if parent and hasattr(parent, "cfg") else None
        self.palette_key = self.cfg.get("theme") if self.cfg else "speeky_blue"
        self.setWindowTitle("Стикеры"); self.setFixedSize(500, 620)
        L = QVBoxLayout(self); L.setSpacing(16); L.setContentsMargins(24, 24, 24, 24)
        title = QLabel("🎨 Стикеры"); title.setStyleSheet("font-size: 24px; font-weight: 800;")
        L.addWidget(title)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        self.gw = QWidget(); self.grid = QGridLayout(self.gw); self.grid.setSpacing(14)
        scroll.setWidget(self.gw); L.addWidget(scroll, 1)
        add = GlowButton("+ Добавить стикер", palette_key=self.palette_key)
        add.clicked.connect(self.add); L.addWidget(add)
        self.load()
    def load(self):
        while self.grid.count():
            c = self.grid.takeAt(0)
            if c.widget(): c.widget().deleteLater()
        files = []
        if os.path.exists(STICKERS_DIR):
            for f in os.listdir(STICKERS_DIR):
                if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")):
                    files.append(os.path.join(STICKERS_DIR, f))
        if not files:
            ph = QLabel("Нет стикеров."); ph.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid.addWidget(ph, 0, 0); return
        r, c = 0, 0
        for p in files:
            b = CircleIconButton("", palette_key=self.palette_key, size=100)
            b.setIcon(QIcon(p)); b.setIconSize(QSize(88, 88))
            b.clicked.connect(lambda ch, p=p: self.sel(p))
            self.grid.addWidget(b, r, c); c += 1
            if c >= 4: c = 0; r += 1
    def sel(self, p): self.sticker_selected.emit(p); self.close()
    def add(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Стикеры", "", "Images (*.png *.jpg *.jpeg *.gif *.webp)")
        for f in files:
            try: shutil.copy(f, os.path.join(STICKERS_DIR, os.path.basename(f)))
            except Exception: pass
        self.load()

class GifPanel(QDialog):
    gif_selected = pyqtSignal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cfg = parent.cfg if parent and hasattr(parent, "cfg") else None
        self.palette_key = self.cfg.get("theme") if self.cfg else "speeky_blue"
        self.setWindowTitle("GIF"); self.setFixedSize(500, 620)
        L = QVBoxLayout(self); L.setSpacing(16); L.setContentsMargins(24, 24, 24, 24)
        title = QLabel("🎬 GIF"); title.setStyleSheet("font-size: 24px; font-weight: 800;")
        L.addWidget(title)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        self.gw = QWidget(); self.grid = QGridLayout(self.gw); self.grid.setSpacing(14)
        scroll.setWidget(self.gw); L.addWidget(scroll, 1)
        add = GlowButton("+ Добавить GIF", palette_key=self.palette_key)
        add.clicked.connect(self.add); L.addWidget(add)
        self.load()
    def load(self):
        while self.grid.count():
            c = self.grid.takeAt(0)
            if c.widget(): c.widget().deleteLater()
        files = []
        if os.path.exists(GIFS_DIR):
            for f in os.listdir(GIFS_DIR):
                if f.lower().endswith((".gif", ".mp4", ".webm", ".webp")):
                    files.append(os.path.join(GIFS_DIR, f))
        if not files:
            ph = QLabel("Нет GIF."); ph.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid.addWidget(ph, 0, 0); return
        r, c = 0, 0
        for p in files:
            b = CircleIconButton("", palette_key=self.palette_key, size=100)
            if p.lower().endswith(".gif"): b.setIcon(QIcon(p))
            else: b.setText("🎬")
            b.setIconSize(QSize(88, 88))
            b.clicked.connect(lambda ch, p=p: self.sel(p))
            self.grid.addWidget(b, r, c); c += 1
            if c >= 4: c = 0; r += 1
    def sel(self, p): self.gif_selected.emit(p); self.close()
    def add(self):
        files, _ = QFileDialog.getOpenFileNames(self, "GIF", "", "GIF (*.gif *.mp4 *.webm *.webp)")
        for f in files:
            try: shutil.copy(f, os.path.join(GIFS_DIR, os.path.basename(f)))
            except Exception: pass
        self.load()

# ============================================================
# LOGIN PAGE
# ============================================================
class LoginPage(QWidget):
    logged = pyqtSignal(dict)
    def __init__(self, db, cfg, parent=None):
        super().__init__(parent)
        self.db = db; self.cfg = cfg; self.parent_window = parent
        self.palette_key = cfg.get("theme")

        self.bg = AnimatedBackground(self, self.palette_key)
        self.bg.setGeometry(0, 0, 2000, 2000)

        self.card = GlassCard(self, self.palette_key, radius=32)
        self.card.setFixedSize(460, 640)
        CL = QVBoxLayout(self.card)
        CL.setContentsMargins(44, 50, 44, 50)
        CL.setSpacing(16)

        pal = get_palette(self.palette_key)
        logo = QLabel("◈")
        logo.setStyleSheet(f"font-size: 72px; color: {pal['accent1']}; font-weight: 900; background: transparent;")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter); CL.addWidget(logo)

        self.title = GradientTitle("FSOCIETY", size=38, palette_key=self.palette_key)
        self.title.setFixedHeight(64); CL.addWidget(self.title)

        sub = QLabel("Твой защищённый мессенджер")
        sub.setStyleSheet(f"color: {pal['text2']}; font-size: 13px; background: transparent;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter); CL.addWidget(sub)
        CL.addSpacing(30)

        self.li = GlassInput("Никнейм или Email", palette_key=self.palette_key)
        self.li.setText(cfg.get("last_user", ""))
        CL.addWidget(self.li)

        self.pi = GlassInput("Пароль", palette_key=self.palette_key)
        self.pi.setEchoMode(QLineEdit.EchoMode.Password)
        if cfg.get("remember_me", False): self.pi.setText(cfg.get("last_password", ""))
        CL.addWidget(self.pi)

        self.err = QLabel("")
        self.err.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.err.setStyleSheet(f"color: {pal['danger']}; font-size: 12px; background: transparent;")
        self.err.setVisible(False); CL.addWidget(self.err)

        self.remember = QCheckBox("Запомнить меня")
        self.remember.setChecked(cfg.get("remember_me", False))
        self.remember.setStyleSheet(f"""
            QCheckBox {{ color: {pal['text']}; font-size: 13px; spacing: 10px; background: transparent; }}
            QCheckBox::indicator {{
                width: 20px; height: 20px; border-radius: 7px;
                border: 2px solid rgba(255, 255, 255, 30);
                background: rgba(30, 38, 55, 0.6);
            }}
            QCheckBox::indicator:checked {{
                background: {pal['accent1']}; border: 2px solid {pal['accent1']};
            }}
        """)
        CL.addWidget(self.remember)
        CL.addSpacing(12)

        self.login_btn = GlowButton("ВОЙТИ В АККАУНТ", palette_key=self.palette_key)
        self.login_btn.clicked.connect(self.do); CL.addWidget(self.login_btn)

        reg = QPushButton("Нет аккаунта? Зарегистрироваться")
        reg.setCursor(Qt.CursorShape.PointingHandCursor)
        reg.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {pal['accent1']};
                font-size: 13px; font-weight: 600; padding: 8px; border: none; }}
            QPushButton:hover {{ color: {pal['accent_hover']}; }}
        """)
        reg.clicked.connect(lambda: self.parent_window.switch(1)); CL.addWidget(reg)

        CL.addStretch()
        v = QLabel(f"v{APP_VERSION} • @Fsociety_python")
        v.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.setStyleSheet(f"color: {pal['text2']}; font-size: 10px; background: transparent;")
        CL.addWidget(v)

        self.pi.returnPressed.connect(self.do)
        self._fade_in(self.card)

    def _fade_in(self, w):
        eff = QGraphicsOpacityEffect(w); w.setGraphicsEffect(eff)
        a = QPropertyAnimation(eff, b"opacity")
        a.setDuration(900); a.setStartValue(0); a.setEndValue(1)
        a.setEasingCurve(QEasingCurve.Type.OutCubic); a.start()
        self._anim = a

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.bg.setGeometry(0, 0, self.width(), self.height())
        self.card.move((self.width() - self.card.width()) // 2,
                       (self.height() - self.card.height()) // 2)

    def refresh_palette(self, key):
        self.palette_key = key
        self.bg.set_palette(key); self.card.set_palette(key)
        self.title.set_palette(key)
        self.li.set_palette(key); self.pi.set_palette(key)
        self.login_btn.set_palette(key)
        pal = get_palette(key)
        self.err.setStyleSheet(f"color: {pal['danger']}; font-size: 12px; background: transparent;")

    def do(self):
        l = self.li.text().strip(); p = self.pi.text().strip()
        if not l or not p:
            self.err.setText("✕ Заполни поля"); self.err.setVisible(True); return
        u, m = self.db.login(l, p)
        if not u:
            self.err.setText(f"✕ {m}"); self.err.setVisible(True); return
        if self.remember.isChecked():
            self.cfg.set("last_user", l); self.cfg.set("last_password", p)
            self.cfg.set("remember_me", True)
        else:
            self.cfg.set("last_user", ""); self.cfg.set("last_password", "")
            self.cfg.set("remember_me", False)
        self.logged.emit(u)

# ============================================================
# REGISTER PAGE
# ============================================================
class RegisterPage(QWidget):
    def __init__(self, db, cfg, parent=None):
        super().__init__(parent)
        self.db = db; self.cfg = cfg; self.parent_window = parent
        self.palette_key = cfg.get("theme")
        self.bg = AnimatedBackground(self, self.palette_key)
        self.bg.setGeometry(0, 0, 2000, 2000)

        self.card = GlassCard(self, self.palette_key, radius=32)
        self.card.setFixedSize(460, 740)
        CL = QVBoxLayout(self.card)
        CL.setContentsMargins(44, 44, 44, 44); CL.setSpacing(14)

        self.title = GradientTitle("СОЗДАТЬ АККАУНТ", size=22, palette_key=self.palette_key)
        self.title.setFixedHeight(40); CL.addWidget(self.title)

        pal = get_palette(self.palette_key)
        sub = QLabel("Присоединяйся к FSOCIETY")
        sub.setStyleSheet(f"color: {pal['text2']}; font-size: 13px; background: transparent;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter); CL.addWidget(sub)
        CL.addSpacing(18)

        self.ni = GlassInput("Никнейм", palette_key=self.palette_key); CL.addWidget(self.ni)
        self.ei = GlassInput("Email", palette_key=self.palette_key); CL.addWidget(self.ei)
        self.p1 = GlassInput("Пароль", palette_key=self.palette_key)
        self.p1.setEchoMode(QLineEdit.EchoMode.Password); CL.addWidget(self.p1)
        self.p2 = GlassInput("Повтори пароль", palette_key=self.palette_key)
        self.p2.setEchoMode(QLineEdit.EchoMode.Password); CL.addWidget(self.p2)

        h = QLabel("💡 Email mastakov.michail@gmail.com = значок 🎖")
        h.setStyleSheet(f"color: {pal['warning']}; font-size: 11px; background: transparent;")
        h.setAlignment(Qt.AlignmentFlag.AlignCenter); h.setWordWrap(True); CL.addWidget(h)

        self.err = QLabel("")
        self.err.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.err.setStyleSheet(f"color: {pal['danger']}; font-size: 12px; background: transparent;")
        self.err.setVisible(False); CL.addWidget(self.err)
        CL.addSpacing(10)

        self.reg_btn = GlowButton("СОЗДАТЬ АККАУНТ", palette_key=self.palette_key)
        self.reg_btn.clicked.connect(self.do); CL.addWidget(self.reg_btn)

        back = QPushButton("← Назад")
        back.setCursor(Qt.CursorShape.PointingHandCursor)
        back.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {pal['accent1']};
                font-size: 13px; font-weight: 600; padding: 8px; border: none; }}
            QPushButton:hover {{ color: {pal['accent_hover']}; }}
        """)
        back.clicked.connect(lambda: self.parent_window.switch(0)); CL.addWidget(back)
        self._fade_in(self.card)

    def _fade_in(self, w):
        eff = QGraphicsOpacityEffect(w); w.setGraphicsEffect(eff)
        a = QPropertyAnimation(eff, b"opacity")
        a.setDuration(900); a.setStartValue(0); a.setEndValue(1)
        a.setEasingCurve(QEasingCurve.Type.OutCubic); a.start()
        self._anim = a

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.bg.setGeometry(0, 0, self.width(), self.height())
        self.card.move((self.width() - self.card.width()) // 2,
                       (self.height() - self.card.height()) // 2)

    def refresh_palette(self, key):
        self.palette_key = key
        self.bg.set_palette(key); self.card.set_palette(key)
        self.title.set_palette(key)
        self.ni.set_palette(key); self.ei.set_palette(key)
        self.p1.set_palette(key); self.p2.set_palette(key)
        self.reg_btn.set_palette(key)

    def do(self):
        n = self.ni.text().strip(); e = self.ei.text().strip()
        p = self.p1.text().strip(); p2 = self.p2.text().strip()
        if not n or not e or not p:
            self.err.setText("✕ Заполни поля"); self.err.setVisible(True); return
        if p != p2:
            self.err.setText("✕ Пароли не совпадают"); self.err.setVisible(True); return
        if len(p) < 6:
            self.err.setText("✕ Минимум 6 символов"); self.err.setVisible(True); return
        if "@" not in e or "." not in e:
            self.err.setText("✕ Неверный email"); self.err.setVisible(True); return
        dev = (e.lower() == DEV_EMAIL.lower())
        ok, m = self.db.reg(n, e, p, dev)
        if not ok:
            self.err.setText(f"✕ {m}"); self.err.setVisible(True); return
        if dev: QMessageBox.information(self, "🎖", "Добро пожаловать, разработчик!")
        else: QMessageBox.information(self, "OK", "Аккаунт создан!")
        self.parent_window.login_page.li.setText(n)
        self.parent_window.switch(0)

# ============================================================
# CHAT PAGE
# ============================================================
class ChatPage(QWidget):
    def __init__(self, db, cfg, parent=None):
        super().__init__(parent)
        self.db = db; self.cfg = cfg; self.parent_window = parent
        self.user = None; self.chat = None
        self.network = None; self.is_group = False
        self.palette_key = cfg.get("theme")
        self.bot = FSOCIETYBot(db)

        self.bg = AnimatedBackground(self, self.palette_key)
        self.bg.setGeometry(0, 0, 3000, 3000)

        M = QHBoxLayout(self)
        M.setContentsMargins(0, 0, 0, 0); M.setSpacing(0)

        # Sidebar
        self.sidebar = GlassCard(self, self.palette_key, radius=0)
        self.sidebar.setFixedWidth(340)
        SL = QVBoxLayout(self.sidebar)
        SL.setContentsMargins(20, 24, 20, 24); SL.setSpacing(16)

        top = QHBoxLayout()
        self.av = CircleIconButton("?", palette_key=self.palette_key, size=48)
        top.addWidget(self.av)
        info = QVBoxLayout(); info.setSpacing(3)
        pal = get_palette(self.palette_key)
        self.pn = QLabel("—")
        self.pn.setStyleSheet(f"color: {pal['text']}; font-weight: 700; font-size: 15px; background: transparent;")
        info.addWidget(self.pn)
        self.status = QLabel("● Не подключен")
        self.status.setStyleSheet(f"color: {pal['danger']}; font-size: 11px; background: transparent;")
        info.addWidget(self.status)
        top.addLayout(info); top.addStretch()

        pc_btn = CircleIconButton("🖥️", palette_key=self.palette_key, size=42)
        pc_btn.setToolTip("Управление ПК")
        pc_btn.clicked.connect(lambda: self.parent_window.switch(4))
        top.addWidget(pc_btn)

        sb_btn = CircleIconButton("⚙", palette_key=self.palette_key, size=42)
        sb_btn.clicked.connect(lambda: self.parent_window.switch(3))
        top.addWidget(sb_btn)
        SL.addLayout(top)

        self.search = GlassInput("🔍 Поиск людей...", palette_key=self.palette_key)
        self.search.setMinimumHeight(48)
        self.search.returnPressed.connect(lambda: self.search_users(self.search.text()))
        SL.addWidget(self.search)

        sec = QLabel("ЧАТЫ")
        sec.setStyleSheet(f"color: {pal['text2']}; font-size: 11px; font-weight: 700; letter-spacing: 1.5px; background: transparent;")
        SL.addWidget(sec)

        self.cl = QListWidget()
        self.cl.setStyleSheet(self._list_style())
        for c in ["💬 Избранное", "👥 Общий чат", "🤖 Бот"]:
            self.cl.addItem(c)
        self.cl.itemClicked.connect(self.open_chat)
        SL.addWidget(self.cl, 1)

        nc = GlowButton("+ Новый чат", palette_key=self.palette_key)
        nc.setMinimumHeight(46); nc.clicked.connect(self.new_chat); SL.addWidget(nc)
        grp = GlowButton("+ Группа", palette_key=self.palette_key)
        grp.setMinimumHeight(46); grp.clicked.connect(self.new_group); SL.addWidget(grp)
        conn = GlowButton("🔌 Подключиться", palette_key=self.palette_key)
        conn.setMinimumHeight(46); conn.clicked.connect(self.connect_server); SL.addWidget(conn)

        M.addWidget(self.sidebar)

        # Chat area
        ch = QFrame()
        ch.setStyleSheet("background: transparent;")
        CL = QVBoxLayout(ch)
        CL.setContentsMargins(0, 0, 0, 0); CL.setSpacing(0)

        hd = QFrame()
        hd.setStyleSheet(f"""
            QFrame {{
                background-color: {pal['card']};
                border-bottom: 1px solid rgba(255, 255, 255, 15);
            }}
        """)
        hd.setFixedHeight(84)
        HL = QHBoxLayout(hd)
        HL.setContentsMargins(28, 14, 28, 14)

        self.ct = QLabel("Выбери чат")
        self.ct.setStyleSheet(f"color: {pal['text']}; font-size: 19px; font-weight: 800; background: transparent;")
        HL.addWidget(self.ct); HL.addStretch()

        for txt, tip, fn in [("📞", "Аудио", self.call_audio),
                              ("📹", "Видео", self.call_video),
                              ("📁", "Файл", self.attach_file)]:
            b = CircleIconButton(txt, palette_key=self.palette_key, size=46)
            b.setToolTip(tip); b.clicked.connect(fn); HL.addWidget(b)

        CL.addWidget(hd)

        self.sa = QScrollArea()
        self.sa.setWidgetResizable(True)
        self.sa.setStyleSheet("background: transparent; border: none;")
        self.mw = QWidget()
        self.mw.setStyleSheet("background: transparent;")
        self.ml = QVBoxLayout(self.mw)
        self.ml.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.ml.setSpacing(12); self.ml.setContentsMargins(28, 28, 28, 28)
        self.sa.setWidget(self.mw)
        CL.addWidget(self.sa, 1)

        ip = QFrame()
        ip.setStyleSheet(f"""
            QFrame {{
                background-color: {pal['card']};
                border-top: 1px solid rgba(255, 255, 255, 15);
            }}
        """)
        IL = QHBoxLayout(ip)
        IL.setContentsMargins(24, 16, 24, 16); IL.setSpacing(12)

        for txt, tip, fn in [("😊", "Эмодзи", self.emoji),
                              ("🎨", "Стикеры", self.sticker),
                              ("🎬", "GIF", self.gif),
                              ("📎", "Файл", self.attach_file)]:
            b = CircleIconButton(txt, palette_key=self.palette_key, size=46)
            b.setToolTip(tip); b.clicked.connect(fn); IL.addWidget(b)

        self.mi = GlassInput("Написать сообщение...", palette_key=self.palette_key)
        self.mi.setMinimumHeight(46)
        self.mi.returnPressed.connect(self.send)
        IL.addWidget(self.mi, 1)

        send = CircleIconButton("➤", palette_key=self.palette_key, size=46)
        send.clicked.connect(self.send); IL.addWidget(send)
        CL.addWidget(ip)
        M.addWidget(ch, 1)

    def _list_style(self):
        pal = get_palette(self.palette_key)
        return f"""
            QListWidget {{ background: transparent; border: none; padding: 4px; outline: none; }}
            QListWidget::item {{
                background-color: transparent; border-radius: 14px;
                padding: 14px 18px; margin: 4px 2px;
                color: {pal['text']}; font-size: 14px; font-weight: 500;
            }}
            QListWidget::item:hover {{ background-color: rgba(255, 255, 255, 10); }}
            QListWidget::item:selected {{
                background-color: {pal['accent2']}; color: white; font-weight: 700;
            }}
        """

    def set_user(self, u):
        self.user = u
        self.pn.setText(u["nickname"])
        self.av.setText(u["nickname"][0].upper())
        for g in self.db.get_groups(u["nickname"]):
            item_text = f"👥 {g}"
            items = [self.cl.item(i).text() for i in range(self.cl.count())]
            if item_text not in items: self.cl.addItem(item_text)

    def open_chat(self, item):
        self.chat = item.text(); self.ct.setText(item.text())
        self.is_group = item.text().startswith("👥")
        self.clear(); self.add("Система", f"Чат: {item.text()}")

    def clear(self):
        while self.ml.count():
            c = self.ml.takeAt(0)
            if c.widget(): c.widget().deleteLater()

    def add(self, s, txt, time_str=None):
        time_str = time_str or datetime.datetime.now().strftime("%H:%M")
        pal = get_palette(self.palette_key)
        is_me = self.user and s == self.user["nickname"]

        bubble = MessageBubble(self, is_me=is_me, palette_key=self.palette_key)
        L = QVBoxLayout(bubble)
        L.setContentsMargins(16, 12, 16, 12); L.setSpacing(4)

        if not is_me and self.user:
            sl = QLabel(s)
            sl.setStyleSheet(f"color: {pal['accent1']}; font-size: 12px; font-weight: 700; background: transparent;")
            L.addWidget(sl)

        tl = QLabel(txt); tl.setWordWrap(True)
        tl.setStyleSheet(f"color: {'white' if is_me else pal['text']}; font-size: 14px; background: transparent;")
        L.addWidget(tl)

        tml = QLabel(time_str)
        tml.setStyleSheet(f"color: {'rgba(255,255,255,0.75)' if is_me else pal['text2']}; font-size: 10px; background: transparent;")
        tml.setAlignment(Qt.AlignmentFlag.AlignRight); L.addWidget(tml)

        wrapper = QWidget(); wrapper.setStyleSheet("background: transparent;")
        w = QHBoxLayout(wrapper)
        w.setContentsMargins(0, 0, 0, 0)
        if is_me: w.addStretch(); w.addWidget(bubble)
        else: w.addWidget(bubble); w.addStretch()
        self.ml.addWidget(wrapper)
        QTimer.singleShot(50, lambda: self.sa.verticalScrollBar().setValue(
            self.sa.verticalScrollBar().maximum()))

    def add_image(self, path, max_size=200):
        bubble = MessageBubble(self, is_me=True, palette_key=self.palette_key)
        L = QVBoxLayout(bubble)
        L.setContentsMargins(12, 12, 12, 12)
        if path.lower().endswith(".gif"):
            lbl = QLabel(); movie = QMovie(path)
            movie.setScaledSize(QSize(max_size, max_size))
            lbl.setMovie(movie); movie.start()
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("background: transparent;")
        else:
            lbl = QLabel()
            pix = QPixmap(path).scaled(max_size, max_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            lbl.setPixmap(pix); lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("background: transparent;")
        L.addWidget(lbl)
        tm = QLabel(datetime.datetime.now().strftime("%H:%M"))
        tm.setStyleSheet("color: rgba(255,255,255,0.75); font-size: 10px; background: transparent;")
        tm.setAlignment(Qt.AlignmentFlag.AlignRight); L.addWidget(tm)
        wrapper = QWidget(); wrapper.setStyleSheet("background: transparent;")
        w = QHBoxLayout(wrapper)
        w.setContentsMargins(0, 0, 0, 0)
        w.addStretch(); w.addWidget(bubble)
        self.ml.addWidget(wrapper)
        QTimer.singleShot(50, lambda: self.sa.verticalScrollBar().setValue(
            self.sa.verticalScrollBar().maximum()))

    def send(self):
        txt = self.mi.text().strip()
        if not txt or not self.user: return
        if self.chat and "🤖" in self.chat:
            self.add(self.user["nickname"], txt); self.mi.clear()
            QTimer.singleShot(500, lambda: self.bot_reply(txt)); return
        self.add(self.user["nickname"], txt)
        if self.chat: self.db.save_msg(self.user["nickname"], self.chat, txt,
                                        1 if self.is_group else 0)
        if self.network and self.network.isRunning(): self.network.send_message(txt)
        self.mi.clear()

    def bot_reply(self, txt):
        r = self.bot.handle(txt, self.user)
        if r: self.add("🤖 FSOCIETY Bot", r)

    def new_chat(self):
        t, ok = QInputDialog.getText(self, "Новый чат", "Никнейм:")
        if ok and t: self.cl.addItem(f"💬 {t}")

    def new_group(self):
        name, ok = QInputDialog.getText(self, "Новая группа", "Название:")
        if ok and name:
            ok2, msg = self.db.create_group(name, self.user["nickname"])
            if ok2: self.cl.addItem(f"👥 {name}")
            else: QMessageBox.warning(self, "Ошибка", msg)

    def search_users(self, query):
        query = query.strip()
        if not query: return
        results = self.db.find_user(query)
        if not results:
            QMessageBox.information(self, "Поиск", "❌ Не найден"); return
        nick, ok = QInputDialog.getItem(self, "Результаты", "Выбери:",
            [f"{n}{' 🎖' if d else ''}" for n, e, d in results], 0, False)
        if ok and nick:
            clean = nick.replace(" 🎖", "").strip()
            it = f"💬 {clean}"
            items = [self.cl.item(i).text() for i in range(self.cl.count())]
            if it not in items: self.cl.addItem(it)
            for i in range(self.cl.count()):
                if self.cl.item(i).text() == it:
                    self.cl.setCurrentRow(i)
                    self.open_chat(self.cl.item(i))
                    break

    def connect_server(self):
        ip, ok = QInputDialog.getText(self, "Сервер", "IP:",
                                       text=self.cfg.get("server_ip"))
        if not ok or not ip: return
        port, ok = QInputDialog.getInt(self, "Сервер", "Порт:",
                                        self.cfg.get("server_port"))
        if not ok: return
        self.cfg.set("server_ip", ip); self.cfg.set("server_port", port)
        self.network = NetworkClient(ip, port, self.user["nickname"])
        pal = get_palette(self.palette_key)
        self.network.connected.connect(lambda: self.status.setText("● Подключен"))
        self.network.connected.connect(lambda: self.status.setStyleSheet(
            f"color: {pal['success']}; font-size: 11px; background: transparent;"))
        self.network.disconnected.connect(lambda: self.status.setText("● Отключен"))
        self.network.message_received.connect(self.on_network_message)
        self.network.start()

    def on_network_message(self, s, t, ts): self.add(s, t, ts)

    def emoji(self):
        es = ["😊", "😂", "❤️", "🔥", "👍", "🎉", "😎", "🤔", "😢", "😡",
              "🥳", "😴", "🤯", "🥰", "😇", "🤡", "💀", "👻", "🤖", "👽",
              "🎃", "😈", "💩", "🙃"]
        m = QMenu(self)
        pal = get_palette(self.palette_key)
        m.setStyleSheet(f"""
            QMenu {{ background-color: {pal['card']};
                border: 1px solid rgba(255,255,255,20);
                border-radius: 14px; padding: 8px; }}
            QMenu::item {{ padding: 10px 20px; border-radius: 10px; font-size: 20px; }}
            QMenu::item:selected {{ background-color: {pal['accent2']}; }}
        """)
        for e in es:
            a = QAction(e, self)
            a.triggered.connect(lambda c, em=e: self.mi.insert(em))
            m.addAction(a)
        m.exec(QCursor.pos())

    def sticker(self):
        p = StickerPanel(self)
        p.sticker_selected.connect(self.send_sticker)
        p.exec()
    def send_sticker(self, path):
        if not self.user: return
        self.add_image(path, 150)
        if self.chat: self.db.save_msg(self.user["nickname"], self.chat, f"[STICKER]{path}")
    def gif(self):
        p = GifPanel(self)
        p.gif_selected.connect(self.send_gif)
        p.exec()
    def send_gif(self, path):
        if not self.user: return
        self.add_image(path, 250)
        if self.chat: self.db.save_msg(self.user["nickname"], self.chat, f"[GIF]{path}")
    def attach_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выбери файл")
        if path and self.user:
            fname = os.path.basename(path)
            self.add(self.user["nickname"], f"📎 {fname}")
            try: shutil.copy(path, os.path.join(DOWNLOADS_DIR, fname))
            except Exception: pass
    def call_audio(self):
        if CALLS_OK: d = CallDialog(self, "audio"); d.exec()
        else: QMessageBox.information(self, "📞", "calls.py не найден")
    def call_video(self):
        if CALLS_OK: d = CallDialog(self, "video"); d.exec()
        else: QMessageBox.information(self, "📹", "calls.py не найден")

    def refresh_palette(self, key):
        self.palette_key = key
        self.bg.set_palette(key); self.sidebar.set_palette(key)
        self.cl.setStyleSheet(self._list_style())

# ============================================================
# PC PANEL
# ============================================================
class PCPanelPage(QWidget):
    def __init__(self, db, cfg, parent=None):
        super().__init__(parent)
        self.db = db; self.cfg = cfg; self.parent_window = parent
        self.user = None
        self.palette_key = cfg.get("theme")
        self.bg = AnimatedBackground(self, self.palette_key)
        self.bg.setGeometry(0, 0, 3000, 3000)

        L = QVBoxLayout(self)
        L.setContentsMargins(40, 30, 40, 30); L.setSpacing(20)

        top = QHBoxLayout()
        back = CircleIconButton("←", palette_key=self.palette_key, size=46)
        back.clicked.connect(lambda: self.parent_window.switch(2))
        top.addWidget(back); top.addStretch()
        self.title = GradientTitle("🖥️ УПРАВЛЕНИЕ ПК", size=26, palette_key=self.palette_key)
        self.title.setFixedHeight(50); top.addWidget(self.title); top.addStretch()
        L.addLayout(top)

        if not COMMANDS_OK:
            warn = QLabel("⚠️ commands.py не найден")
            warn.setAlignment(Qt.AlignmentFlag.AlignCenter)
            warn.setStyleSheet(f"color: {get_palette(self.palette_key)['warning']}; font-size: 14px;")
            L.addWidget(warn); L.addStretch(); return

        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        container = QWidget(); container.setStyleSheet("background: transparent;")
        CL = QVBoxLayout(container); CL.setSpacing(20)

        # Быстрые
        g1 = self._grp("⚡ Быстрые действия")
        g1l = QGridLayout(g1); g1l.setSpacing(14)
        for i, (txt, fn) in enumerate([
            ("📸 Скриншот", self.act_screenshot),
            ("📊 Статус ПК", self.act_status),
            ("🎥 Камера", self.act_camera),
            ("📥 Downloader", self.act_downloader)]):
            b = GlowButton(txt, palette_key=self.palette_key)
            b.setMinimumHeight(60); b.clicked.connect(fn)
            g1l.addWidget(b, i // 2, i % 2)
        CL.addWidget(g1)

        # Питание
        g2 = self._grp("🔌 Питание")
        g2l = QGridLayout(g2); g2l.setSpacing(14)
        for i, (txt, fn) in enumerate([
            ("🔒 Блокировка", self.act_lock),
            ("⛔ Выключить", self.act_shutdown),
            ("🔄 Перезагрузить", self.act_restart),
            ("💤 Сон", self.act_sleep)]):
            b = GlowButton(txt, palette_key=self.palette_key)
            b.setMinimumHeight(60); b.clicked.connect(fn)
            g2l.addWidget(b, i // 2, i % 2)
        CL.addWidget(g2)

        # Программы
        g3 = self._grp("📂 Программы")
        g3l = QGridLayout(g3); g3l.setSpacing(14)
        for i, (txt, fn) in enumerate([
            ("💻 CMD", self.act_cmd),
            ("⚡ PowerShell", self.act_powershell),
            ("📝 Блокнот", self.act_notepad),
            ("🧮 Калькулятор", self.act_calc),
            ("📂 Проводник", self.act_explorer),
            ("📊 Диспетчер", self.act_taskmgr)]):
            b = GlowButton(txt, palette_key=self.palette_key)
            b.setMinimumHeight(56); b.clicked.connect(fn)
            g3l.addWidget(b, i // 3, i % 3)
        CL.addWidget(g3)

        # Своя команда
        g4 = self._grp("⌨️ Своя команда")
        g4l = QVBoxLayout(g4)
        self.cmd_input = GlassInput("Введи команду CMD...", palette_key=self.palette_key)
        g4l.addWidget(self.cmd_input)
        run = GlowButton("▶ Выполнить", palette_key=self.palette_key)
        run.clicked.connect(self.act_custom_cmd); g4l.addWidget(run)
        self.cmd_output = QTextEdit()
        self.cmd_output.setReadOnly(True)
        self.cmd_output.setMaximumHeight(150)
        pal = get_palette(self.palette_key)
        self.cmd_output.setStyleSheet(f"""
            QTextEdit {{
                background-color: rgba(20, 26, 40, 0.7);
                border: 1px solid rgba(255,255,255,15);
                border-radius: 14px; padding: 12px;
                color: {pal['text']}; font-family: Consolas; font-size: 12px;
            }}
        """)
        g4l.addWidget(self.cmd_output)
        CL.addWidget(g4)

        # VK-бот
        g5 = self._grp("🤖 VK-бот")
        g5l = QVBoxLayout(g5)
        st = QLabel("✅ VK-бот доступен" if VK_BOT_OK else "❌ vk_bot.py не найден")
        st.setStyleSheet(f"color: {pal['success'] if VK_BOT_OK else pal['danger']}; font-size: 13px; background: transparent;")
        g5l.addWidget(st)
        vk_btn = GlowButton("🔥 Запустить VK-бот в фоне", palette_key=self.palette_key)
        vk_btn.clicked.connect(self.act_start_vk); g5l.addWidget(vk_btn)
        CL.addWidget(g5)

        CL.addStretch()
        scroll.setWidget(container); L.addWidget(scroll, 1)

    def _grp(self, title):
        g = QGroupBox(title)
        pal = get_palette(self.palette_key)
        g.setStyleSheet(f"""
            QGroupBox {{
                color: {pal['accent1']};
                border: 1.5px solid rgba(255,255,255,15);
                border-radius: 18px; margin-top: 20px; padding: 22px;
                font-weight: 700; font-size: 14px;
                background-color: rgba(20, 26, 40, 0.55);
            }}
            QGroupBox::title {{
                subcontrol-origin: margin; left: 20px; padding: 0 10px;
            }}
        """)
        return g

    def set_user(self, u): self.user = u
    def resizeEvent(self, e):
        super().resizeEvent(e); self.bg.setGeometry(0, 0, self.width(), self.height())
    def refresh_palette(self, key):
        self.palette_key = key
        self.bg.set_palette(key); self.title.set_palette(key)

    def act_screenshot(self):
        try:
            from PIL import ImageGrab
            path = f"screenshot_{int(time.time())}.png"
            ImageGrab.grab().save(path)
            QMessageBox.information(self, "Скриншот", f"Сохранён: {path}")
        except Exception as e: QMessageBox.warning(self, "Ошибка", str(e))
    def act_status(self):
        try: QMessageBox.information(self, "Статус", str(commands.get_status()))
        except Exception as e: QMessageBox.warning(self, "Ошибка", str(e))
    def act_camera(self): QMessageBox.information(self, "Камера", "См. VK-бот")
    def act_downloader(self):
        url, ok = QInputDialog.getText(self, "Downloader", "Ссылка:")
        if ok and url: QMessageBox.information(self, "OK", "См. VK-бот")
    def act_lock(self):
        try: commands.lock_pc()
        except Exception: pass
    def act_shutdown(self):
        if QMessageBox.question(self, "Выключить", "Точно?") == QMessageBox.StandardButton.Yes:
            try: commands.shutdown()
            except Exception: pass
    def act_restart(self):
        if QMessageBox.question(self, "Перезагрузить", "Точно?") == QMessageBox.StandardButton.Yes:
            try: commands.restart()
            except Exception: pass
    def act_sleep(self):
        try: os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        except Exception: pass
    def act_cmd(self):
        try: commands.open_cmd()
        except Exception: pass
    def act_powershell(self):
        try: commands.open_powershell()
        except Exception: pass
    def act_notepad(self):
        try: commands.open_notepad()
        except Exception: pass
    def act_calc(self):
        try: commands.open_calc()
        except Exception: pass
    def act_explorer(self):
        try: commands.open_explorer()
        except Exception: pass
    def act_taskmgr(self):
        try: commands.open_taskmgr()
        except Exception: pass
    def act_custom_cmd(self):
        cmd = self.cmd_input.text().strip()
        if not cmd: return
        try:
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            self.cmd_output.setText((r.stdout or r.stderr or "OK")[:3000])
        except Exception as e: self.cmd_output.setText(f"Ошибка: {e}")
    def act_start_vk(self):
        if not VK_BOT_OK:
            QMessageBox.warning(self, "Ошибка", "vk_bot.py не найден"); return
        def run_vk():
            try: vk_bot.start_vk_bot()
            except Exception as e: print(f"❌ VK: {e}")
        threading.Thread(target=run_vk, daemon=True).start()
        QMessageBox.information(self, "OK", "VK-бот запущен в фоне")

# ============================================================
# SETTINGS
# ============================================================
class SettingsPage(QWidget):
    def __init__(self, cfg, parent=None):
        super().__init__(parent)
        self.cfg = cfg; self.parent_window = parent
        self.palette_key = cfg.get("theme")
        self.bg = AnimatedBackground(self, self.palette_key)
        self.bg.setGeometry(0, 0, 3000, 3000)

        L = QVBoxLayout(self)
        L.setContentsMargins(40, 30, 40, 30)

        top = QHBoxLayout()
        back = CircleIconButton("←", palette_key=self.palette_key, size=46)
        back.clicked.connect(lambda: self.parent_window.switch(2))
        top.addWidget(back); top.addStretch()
        self.title = GradientTitle("НАСТРОЙКИ", size=28, palette_key=self.palette_key)
        self.title.setFixedHeight(50); top.addWidget(self.title); top.addStretch()
        L.addLayout(top)

        tabs = QTabWidget()
        pal = get_palette(self.palette_key)
        tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1.5px solid rgba(255,255,255,15);
                border-radius: 20px;
                background-color: rgba(20, 26, 40, 0.6); top: -1px;
            }}
            QTabBar::tab {{
                background: transparent; color: {pal['text2']};
                padding: 14px 28px; border-radius: 12px;
                margin: 6px 4px; font-weight: 600; font-size: 13px;
            }}
            QTabBar::tab:hover {{ color: {pal['text']}; }}
            QTabBar::tab:selected {{
                background: {pal['accent2']}; color: white; font-weight: 700;
            }}
        """)
        L.addWidget(tabs)
        tabs.addTab(self.tab_appearance(), "🎨 Внешний вид")
        tabs.addTab(self.tab_notif(), "🔔 Уведомления")
        tabs.addTab(self.tab_server(), "🌐 Сервер")
        tabs.addTab(self.tab_about(), "ℹ О программе")

    def tab_appearance(self):
        w = QWidget(); w.setStyleSheet("background: transparent;")
        L = QVBoxLayout(w)
        pal = get_palette(self.palette_key)
        g = QGroupBox("Тема")
        g.setStyleSheet(f"""
            QGroupBox {{ color: {pal['accent1']};
                border: 1.5px solid rgba(255,255,255,15);
                border-radius: 18px; margin-top: 20px; padding: 22px;
                font-weight: 700; background-color: rgba(20, 26, 40, 0.55); }}
            QGroupBox::title {{ subcontrol-origin: margin; left: 20px; padding: 0 10px; }}
        """)
        gl = QFormLayout(g)
        self.theme_combo = QComboBox()
        for k, v in PALETTES.items(): self.theme_combo.addItem(v["name"], k)
        idx = self.theme_combo.findData(self.cfg.get("theme"))
        if idx >= 0: self.theme_combo.setCurrentIndex(idx)
        self.theme_combo.currentIndexChanged.connect(self.on_theme)
        self.theme_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: rgba(30, 38, 55, 0.6);
                border: 1.5px solid rgba(255,255,255,20);
                border-radius: 14px; padding: 12px 16px;
                color: {pal['text']}; font-size: 14px;
            }}
        """)
        gl.addRow("Тема:", self.theme_combo)
        L.addWidget(g); L.addStretch()
        return w

    def on_theme(self):
        k = self.theme_combo.currentData()
        self.cfg.set("theme", k)
        self.parent_window.apply_palette(k)

    def tab_notif(self):
        w = QWidget(); w.setStyleSheet("background: transparent;")
        L = QVBoxLayout(w)
        pal = get_palette(self.palette_key)
        g = QGroupBox("Уведомления")
        g.setStyleSheet(f"""
            QGroupBox {{ color: {pal['accent1']};
                border: 1.5px solid rgba(255,255,255,15);
                border-radius: 18px; margin-top: 20px; padding: 22px;
                font-weight: 700; background-color: rgba(20, 26, 40, 0.55); }}
            QGroupBox::title {{ subcontrol-origin: margin; left: 20px; padding: 0 10px; }}
        """)
        gl = QVBoxLayout(g)
        for k, l in [("notifications", "Показывать"), ("sounds", "Звуки")]:
            cb = QCheckBox(l); cb.setChecked(self.cfg.get(k, True))
            cb.setStyleSheet(f"""
                QCheckBox {{ color: {pal['text']}; font-size: 14px; spacing: 10px; background: transparent; }}
                QCheckBox::indicator {{
                    width: 20px; height: 20px; border-radius: 7px;
                    border: 2px solid rgba(255,255,255,30);
                    background: rgba(30, 38, 55, 0.6);
                }}
                QCheckBox::indicator:checked {{ background: {pal['accent1']}; border: 2px solid {pal['accent1']}; }}
            """)
            cb.toggled.connect(lambda v, kk=k: self.cfg.set(kk, v))
            gl.addWidget(cb)
        L.addWidget(g); L.addStretch()
        return w

    def tab_server(self):
        w = QWidget(); w.setStyleSheet("background: transparent;")
        L = QVBoxLayout(w)
        pal = get_palette(self.palette_key)
        g = QGroupBox("Сервер")
        g.setStyleSheet(f"""
            QGroupBox {{ color: {pal['accent1']};
                border: 1.5px solid rgba(255,255,255,15);
                border-radius: 18px; margin-top: 20px; padding: 22px;
                font-weight: 700; background-color: rgba(20, 26, 40, 0.55); }}
            QGroupBox::title {{ subcontrol-origin: margin; left: 20px; padding: 0 10px; }}
        """)
        gl = QFormLayout(g)
        self.sip = GlassInput("", palette_key=self.palette_key)
        self.sip.setText(self.cfg.get("server_ip", "127.0.0.1"))
        gl.addRow("IP:", self.sip)
        self.sport = QSpinBox(); self.sport.setRange(1024, 65535)
        self.sport.setValue(self.cfg.get("server_port", 5555))
        self.sport.setStyleSheet(f"""
            QSpinBox {{ background-color: rgba(30, 38, 55, 0.6);
                border: 1.5px solid rgba(255,255,255,20);
                border-radius: 14px; padding: 12px 16px;
                color: {pal['text']}; font-size: 14px; }}
        """)
        gl.addRow("Порт:", self.sport)
        save = GlowButton("Сохранить", palette_key=self.palette_key)
        save.clicked.connect(self.save_server); gl.addRow(save)
        L.addWidget(g)
        start = GlowButton("🚀 Запустить сервер", palette_key=self.palette_key)
        start.clicked.connect(self.start_server); L.addWidget(start)
        L.addStretch()
        return w

    def save_server(self):
        self.cfg.set("server_ip", self.sip.text())
        self.cfg.set("server_port", self.sport.value())
        QMessageBox.information(self, "OK", "Сохранено")

    def start_server(self):
        port = self.sport.value()
        threading.Thread(target=run_server, args=(port,), daemon=True).start()
        QMessageBox.information(self, "Сервер", f"Сервер на порту {port}")

    def tab_about(self):
        w = QWidget(); w.setStyleSheet("background: transparent;")
        L = QVBoxLayout(w); L.setAlignment(Qt.AlignmentFlag.AlignTop)
        pal = get_palette(self.palette_key)
        t = QLabel(f"<h1 style='color:{pal['accent1']}'>{APP}</h1>")
        t.setAlignment(Qt.AlignmentFlag.AlignCenter); L.addWidget(t)
        v = QLabel(f"Версия: {APP_VERSION}")
        v.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.setStyleSheet(f"color: {pal['text2']}; font-size: 13px;"); L.addWidget(v)
        dev = QLabel(f"Разработчик: <b>@Fsociety_python</b><br>Email: {DEV_EMAIL}")
        dev.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dev.setStyleSheet(f"color: {pal['text']}; font-size: 13px;"); L.addWidget(dev)
        L.addStretch()
        return w

    def resizeEvent(self, e):
        super().resizeEvent(e); self.bg.setGeometry(0, 0, self.width(), self.height())
    def refresh_palette(self, key):
        self.palette_key = key
        self.bg.set_palette(key); self.title.set_palette(key)

# ============================================================
# MAIN WINDOW
# ============================================================
class MainWindow(QMainWindow):
    def __init__(self, db, cfg):
        super().__init__()
        self.db = db; self.cfg = cfg
        self.palette_key = cfg.get("theme")
        self.setWindowTitle(APP); self.setMinimumSize(1350, 850)

        root = QWidget(); root.setObjectName("MainRoot")
        root.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setCentralWidget(root)

        rl = QVBoxLayout(root); rl.setContentsMargins(0, 0, 0, 0)
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: transparent;")
        rl.addWidget(self.stack)

        self.login_page = LoginPage(db, cfg, self)
        self.reg_page = RegisterPage(db, cfg, self)
        self.chat_page = ChatPage(db, cfg, self)
        self.settings_page = SettingsPage(cfg, self)
        self.pc_page = PCPanelPage(db, cfg, self)

        for p in [self.login_page, self.reg_page, self.chat_page,
                  self.settings_page, self.pc_page]:
            p.parent_window = self

        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.reg_page)
        self.stack.addWidget(self.chat_page)
        self.stack.addWidget(self.settings_page)
        self.stack.addWidget(self.pc_page)

        self.login_page.logged.connect(self.on_login)
        self.stack.setCurrentIndex(0)
        self.fade()
        QTimer.singleShot(150, self.try_auto_login)

    def apply_palette(self, key):
        self.palette_key = key
        for p in [self.login_page, self.reg_page, self.chat_page,
                  self.settings_page, self.pc_page]:
            if hasattr(p, "refresh_palette"):
                p.refresh_palette(key)

    def try_auto_login(self):
        if not self.cfg.get("remember_me", False): return
        lu = self.cfg.get("last_user", ""); lp = self.cfg.get("last_password", "")
        if not lu or not lp: return
        u, m = self.db.login(lu, lp)
        if u:
            self.chat_page.set_user(u); self.pc_page.set_user(u)
            self.switch(2)

    def fade(self):
        eff = QGraphicsOpacityEffect(self.stack)
        self.stack.setGraphicsEffect(eff)
        a = QPropertyAnimation(eff, b"opacity")
        a.setDuration(450); a.setStartValue(0); a.setEndValue(1)
        a.setEasingCurve(QEasingCurve.Type.OutCubic); a.start()
        self._anim = a

    def switch(self, i):
        self.stack.setCurrentIndex(i); self.fade()

    def on_login(self, u):
        self.chat_page.set_user(u); self.pc_page.set_user(u)
        self.switch(2)

# ============================================================
# MAIN
# ============================================================
def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP)
    cfg = Config(); db = DB()

    if VK_BOT_OK and cfg.get("vk_bot_enabled", True):
        def run_vk():
            try: vk_bot.start_vk_bot()
            except Exception as e: print(f"❌ VK-бот: {e}")
        threading.Thread(target=run_vk, daemon=True).start()
        print("🔥 VK-бот запущен в фоне")

    w = MainWindow(db, cfg)
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()