# -*- coding: utf-8 -*-
"""calls.py — Аудио и видеозвонки через socket (sounddevice)"""
import socket
import threading
import time
import struct
import pickle
import cv2
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton,
    QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap

try:
    import sounddevice as sd
    AUDIO_OK = True
except ImportError:
    AUDIO_OK = False
    print("sounddevice не установлен — аудио не будет работать")


# ============================================================
# АУДИОЗВОНОК
# ============================================================
class AudioCall(QDialog):
    def __init__(self, parent=None, is_server=False, target_ip="127.0.0.1", port=5555):
        super().__init__(parent)
        self.setWindowTitle("Аудиозвонок")
        self.setFixedSize(400, 320)
        self.is_server = is_server
        self.target_ip = target_ip
        self.port = port
        self.running = True
        self.sock = None
        self.conn = None
        self.sample_rate = 16000
        self.channels = 1
        self.blocksize = 1024

        L = QVBoxLayout(self)
        self.status = QLabel("Соединение...")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setStyleSheet("font-size: 14px;")
        L.addWidget(self.status)

        self.info = QLabel(f"{'Сервер' if is_server else 'Клиент'}\n{target_ip}:{port}")
        self.info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        L.addWidget(self.info)

        if not AUDIO_OK:
            warn = QLabel("sounddevice не установлен — звук не работает")
            warn.setAlignment(Qt.AlignmentFlag.AlignCenter)
            warn.setStyleSheet("color: #ff8800; font-size: 11px;")
            L.addWidget(warn)

        L.addStretch()

        end_btn = QPushButton("Завершить")
        end_btn.clicked.connect(self.end_call)
        L.addWidget(end_btn)

        threading.Thread(target=self.run, daemon=True).start()

    def run(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if self.is_server:
                self.sock.bind(("0.0.0.0", self.port))
                self.sock.listen(1)
                self.status.setText("Ожидание звонка...")
                self.conn, addr = self.sock.accept()
                self.status.setText(f"Звонок от {addr[0]}")
            else:
                self.sock.connect((self.target_ip, self.port))
                self.status.setText("Подключено")
                self.conn = self.sock

            if AUDIO_OK:
                threading.Thread(target=self.audio_send, daemon=True).start()
                threading.Thread(target=self.audio_recv, daemon=True).start()
                while self.running:
                    time.sleep(0.5)
            else:
                while self.running:
                    time.sleep(0.5)
        except Exception as e:
            self.status.setText(f"Ошибка: {e}")

    def audio_send(self):
        try:
            def callback(indata, frames, time_info, status):
                if self.running and self.conn:
                    try:
                        self.conn.sendall(indata.tobytes())
                    except:
                        self.running = False
            with sd.RawInputStream(
                samplerate=self.sample_rate,
                blocksize=self.blocksize,
                dtype="int16",
                channels=self.channels,
                callback=callback
            ):
                while self.running:
                    time.sleep(0.1)
        except Exception as e:
            print(f"Audio send error: {e}")

    def audio_recv(self):
        try:
            def callback(outdata, frames, time_info, status):
                try:
                    data = self.conn.recv(frames * 2 * self.channels)
                    if len(data) < len(outdata):
                        outdata[:len(data)] = data
                        outdata[len(data):] = b"\x00" * (len(outdata) - len(data))
                    else:
                        outdata[:] = data
                except:
                    outdata[:] = b"\x00" * len(outdata)
            with sd.RawOutputStream(
                samplerate=self.sample_rate,
                blocksize=self.blocksize,
                dtype="int16",
                channels=self.channels,
                callback=callback
            ):
                while self.running:
                    time.sleep(0.1)
        except Exception as e:
            print(f"Audio recv error: {e}")

    def end_call(self):
        self.running = False
        try:
            if self.conn: self.conn.close()
            if self.sock: self.sock.close()
        except: pass
        self.close()


# ============================================================
# ВИДЕОЗВОНОК
# ============================================================
class VideoCall(QDialog):
    def __init__(self, parent=None, is_server=False, target_ip="127.0.0.1", port=5556):
        super().__init__(parent)
        self.setWindowTitle("Видеозвонок")
        self.setMinimumSize(700, 560)
        self.is_server = is_server
        self.target_ip = target_ip
        self.port = port
        self.running = True
        self.sock = None
        self.conn = None
        self.frame = None

        L = QVBoxLayout(self)
        self.status = QLabel("Соединение...")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        L.addWidget(self.status)

        self.video = QLabel()
        self.video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video.setStyleSheet("background: #000; border-radius: 8px;")
        self.video.setMinimumSize(640, 480)
        L.addWidget(self.video, 1)

        end_btn = QPushButton("Завершить")
        end_btn.clicked.connect(self.end_call)
        L.addWidget(end_btn)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        threading.Thread(target=self.run, daemon=True).start()

    def run(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if self.is_server:
                self.sock.bind(("0.0.0.0", self.port))
                self.sock.listen(1)
                self.status.setText("Ожидание видеозвонка...")
                self.conn, addr = self.sock.accept()
                self.status.setText(f"Видео от {addr[0]}")
            else:
                self.sock.connect((self.target_ip, self.port))
                self.status.setText("Подключено")
                self.conn = self.sock

            threading.Thread(target=self.send_video, daemon=True).start()
            threading.Thread(target=self.recv_video, daemon=True).start()

            while self.running:
                time.sleep(0.5)
        except Exception as e:
            self.status.setText(f"Ошибка: {e}")

    def send_video(self):
        cap = cv2.VideoCapture(0)
        while self.running:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.05)
                continue
            frame = cv2.resize(frame, (320, 240))
            data = pickle.dumps(frame)
            try:
                self.conn.sendall(struct.pack("Q", len(data)) + data)
            except:
                break
        cap.release()

    def recv_video(self):
        data = b""
        payload_size = struct.calcsize("Q")
        while self.running:
            try:
                while len(data) < payload_size:
                    packet = self.conn.recv(4096)
                    if not packet:
                        return
                    data += packet
                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("Q", packed_msg_size)[0]
                while len(data) < msg_size:
                    data += self.conn.recv(4096)
                frame_data = data[:msg_size]
                data = data[msg_size:]
                self.frame = pickle.loads(frame_data)
            except Exception as e:
                print(f"recv_video: {e}")
                break

    def update_frame(self):
        if self.frame is None:
            return
        frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        img = QImage(frame.data, w, h, ch * w, QImage.Format.Format_RGB888)
        self.video.setPixmap(QPixmap.fromImage(img).scaled(
            self.video.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))

    def end_call(self):
        self.running = False
        try:
            if self.conn: self.conn.close()
            if self.sock: self.sock.close()
        except: pass
        self.close()


# ============================================================
# ДИАЛОГ ВЫБОРА (сервер/клиент)
# ============================================================
class CallDialog(QDialog):
    def __init__(self, parent=None, call_type="audio"):
        super().__init__(parent)
        self.call_type = call_type
        title_text = "Аудиозвонок" if call_type == "audio" else "Видеозвонок"
        self.setWindowTitle(title_text)
        self.setFixedSize(420, 300)

        L = QVBoxLayout(self)
        title = QLabel(title_text)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        L.addWidget(title)

        L.addWidget(QLabel("IP собеседника:"))
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("192.168.0.180")
        L.addWidget(self.ip_input)

        L.addWidget(QLabel("Порт:"))
        self.port_input = QLineEdit()
        self.port_input.setText("5555" if call_type == "audio" else "5556")
        L.addWidget(self.port_input)

        L.addSpacing(10)

        b_server = QPushButton("Создать звонок (я сервер)")
        b_server.clicked.connect(lambda: self.start(True))
        L.addWidget(b_server)

        b_client = QPushButton("Позвонить (я клиент)")
        b_client.clicked.connect(lambda: self.start(False))
        L.addWidget(b_client)

    def start(self, is_server):
        ip = self.ip_input.text().strip() or "127.0.0.1"
        try:
            port = int(self.port_input.text().strip())
        except:
            port = 5555 if self.call_type == "audio" else 5556

        if self.call_type == "audio":
            call = AudioCall(self.parent(), is_server, ip, port)
        else:
            call = VideoCall(self.parent(), is_server, ip, port)
        call.show()
        self.close()