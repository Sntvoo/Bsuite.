# C:\Buddy_filing\Suit\python_core.py

import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QGraphicsOpacityEffect, QPushButton, QStackedWidget, QListWidget, QListWidgetItem,
    QSizePolicy, QTextEdit, QLineEdit, QMessageBox, QProgressDialog, QComboBox, QFileDialog,
    QCheckBox, QSpinBox, QRadioButton, QButtonGroup
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QRect, QSize, Signal, QDateTime, QEvent
from PySide6.QtGui import QFont, QColor, QPalette, QScreen, QPainter, QBrush, QPen, QClipboard

# For TinyDB (local database)
from tinydb import TinyDB, Query
import os 
import math 
import socket 
import threading 
import hashlib # For file integrity monitoring and hashing
import random # For password generation
import string # For password generation

# For Encryption/Decryption
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidTag
import base64 # For encoding/decoding encrypted text

# External libraries for OSINT (Optional, but recommended)
try:
    import requests
except ImportError:
    requests = None
try:
    import whois
except ImportError:
    whois = None
try:
    import dns.resolver
except ImportError:
    dns = None


# --- Global Style Constants ---
MAIN_BG_GREY = QColor(40, 40, 40)
SIDEBAR_BG_GREY = QColor(55, 55, 55)
TEXT_COLOR_GREY = QColor(224, 224, 224)
HIGHLIGHT_PURPLE = QColor(128, 0, 128)
LIGHTER_GREY = QColor(70, 70, 70) 

# --- Database Path ---
DATABASE_PATH = os.path.join("C:\\Buddy_filing\\Suit", "buddy_db.json")

# --- Helper Functions ---
def get_sleek_font(size, weight=QFont.DemiBold):
    font = QFont("Segoe UI", size) 
    font.setWeight(weight)
    return font

class LoadingSpinnerWidget(QWidget):
    def __init__(self, parent=None, color=HIGHLIGHT_PURPLE):
        super().__init__(parent)
        self.setFixedSize(60, 60)
        self.color = color
        self.angle = 0 
        self.num_segments = 8 
        self.segment_length = 15 
        self.segment_width = 7 
        self.inner_radius = 15 

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate_spinner)
        self.timer.start(80) 

    def rotate_spinner(self):
        self.angle = (self.angle + 360 // self.num_segments) % 360 
        self.update() 

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        center_x = self.width() / 2
        center_y = self.height() / 2
        painter.translate(center_x, center_y)

        painter.setBrush(QBrush(self.color))
        painter.setPen(Qt.NoPen) 

        for i in range(self.num_segments):
            opacity = 1.0 - (i / self.num_segments) * 0.7 
            painter.setOpacity(opacity)

            painter.save()
            painter.rotate(self.angle + i * (360 / self.num_segments)) 
            
            painter.drawRoundedRect(
                int(self.inner_radius), 
                int(-self.segment_width / 2), 
                self.segment_length, 
                self.segment_width, 
                self.segment_width / 2, 
                self.segment_width / 2  
            )
            painter.restore()

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("B.U.D.D.Ysuite")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint) 
        
        screen_geo = QApplication.primaryScreen().geometry()
        self.setGeometry(screen_geo) 
        
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255)) 
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        
        self.show()
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setAlignment(Qt.AlignCenter) 

        self.title_label = QLabel("BUDDYsuite")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(get_sleek_font(80)) 
        self.title_label.setStyleSheet(f"color: {HIGHLIGHT_PURPLE.name()};") 
        main_layout.addWidget(self.title_label)

        self.spinner = LoadingSpinnerWidget(self, color=HIGHLIGHT_PURPLE)
        main_layout.addWidget(self.spinner, alignment=Qt.AlignCenter)
        
        main_layout.addStretch() 

        self.fine_print_label = QLabel("proudly presented by the ExG series")
        self.fine_print_label.setAlignment(Qt.AlignBottom | Qt.AlignRight)
        self.fine_print_label.setFont(get_sleek_font(12)) 
        self.fine_print_label.setStyleSheet(f"color: {HIGHLIGHT_PURPLE.name()};") 
        
        fine_print_layout = QHBoxLayout()
        fine_print_layout.addStretch() 
        fine_print_layout.addWidget(self.fine_print_label)
        fine_print_layout.setContentsMargins(0, 0, 20, 20) 
        
        main_layout.addLayout(fine_print_layout)
        
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        self.fade_in_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in_animation.setDuration(1500) 
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)
        self.fade_in_animation.setEasingCurve(QEasingCurve.InQuad)
        self.fade_in_animation.finished.connect(self.start_fade_out_timer)

        self.fade_out_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out_animation.setDuration(1500)
        self.fade_out_animation.setStartValue(1.0)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.setEasingCurve(QEasingCurve.OutQuad)
        self.fade_out_animation.finished.connect(self.start_main_app)
        
        self.fade_in_animation.start()

    def start_fade_out_timer(self):
        self.spinner.timer.stop() 
        QTimer.singleShot(1000, self.fade_out_animation.start) 

    def start_main_app(self):
        self.hide() 
        self.main_window = MainWindow() 
        self.main_window.show()

class DataManagementPage(QWidget):
    note_saved = Signal() 

    def __init__(self):
        super().__init__()
        self.db = TinyDB(DATABASE_PATH)
        self.Note = Query()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        main_layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)

        title_label = QLabel("Structured Note-Taking & Tagging")
        title_label.setFont(get_sleek_font(30))
        title_label.setStyleSheet(f"color: {HIGHLIGHT_PURPLE.name()};")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        note_area_label = QLabel("Note Content:")
        note_area_label.setFont(get_sleek_font(14, QFont.Normal))
        note_area_label.setStyleSheet(f"color: {TEXT_COLOR_GREY.name()};")
        main_layout.addWidget(note_area_label)

        self.note_text_edit = QTextEdit()
        self.note_text_edit.setFont(get_sleek_font(12, QFont.Normal))
        self.note_text_edit.setStyleSheet(f"""
            QTextEdit {{
                background-color: {LIGHTER_GREY.name()};
                color: {TEXT_COLOR_GREY.name()};
                border: 1px solid {QColor(90, 90, 90).name()};
                padding: 10px;
            }}
        """)
        self.note_text_edit.setPlaceholderText("Enter your note here...")
        main_layout.addWidget(self.note_text_edit)

        tags_layout = QHBoxLayout()
        tags_layout.setSpacing(10)
        tags_layout.setAlignment(Qt.AlignLeft)

        tags_label = QLabel("Tags (comma-separated):")
        tags_label.setFont(get_sleek_font(14, QFont.Normal))
        tags_label.setStyleSheet(f"color: {TEXT_COLOR_GREY.name()};")
        tags_layout.addWidget(tags_label)

        self.tags_input = QLineEdit()
        self.tags_input.setFont(get_sleek_font(12, QFont.Normal))
        self.tags_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {LIGHTER_GREY.name()};
                color: {TEXT_COLOR_GREY.name()};
                border: 1px solid {QColor(90, 90, 90).name()};
                padding: 5px;
            }}
        """)
        self.tags_input.setPlaceholderText("e.g., OSINT, HUMINT, network, target_alpha")
        tags_layout.addWidget(self.tags_input)
        
        main_layout.addLayout(tags_layout)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setAlignment(Qt.AlignCenter)

        self.save_button = QPushButton("Save Note")
        self.save_button.clicked.connect(self.save_note)
        self.new_note_button = QPushButton("New Note")
        self.new_note_button.clicked.connect(self.clear_note_fields)
        self.load_note_button = QPushButton("Load Note") 
        self.load_note_button.clicked.connect(self.open_load_dialog) 
        self.delete_note_button = QPushButton("Delete Current") 
        self.delete_note_button.clicked.connect(self.delete_current_note)


        button_style = f"""
            QPushButton {{
                background-color: {HIGHLIGHT_PURPLE.name()};
                color: {QColor(255, 255, 255).name()};
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {QColor(150, 0, 150).name()}; 
            }}
        """
        self.save_button.setStyleSheet(button_style)
        self.new_note_button.setStyleSheet(button_style)
        self.load_note_button.setStyleSheet(button_style)
        self.delete_note_button.setStyleSheet(button_style)

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.new_note_button)
        button_layout.addWidget(self.load_note_button)
        button_layout.addWidget(self.delete_note_button)

        main_layout.addLayout(button_layout)
        main_layout.addStretch() 

        notes_list_label = QLabel("Saved Notes:")
        notes_list_label.setFont(get_sleek_font(14, QFont.Normal))
        notes_list_label.setStyleSheet(f"color: {TEXT_COLOR_GREY.name()};")
        main_layout.addWidget(notes_list_label)

        self.saved_notes_display = QListWidget()
        self.saved_notes_display.setFont(get_sleek_font(12, QFont.Normal))
        self.saved_notes_display.setStyleSheet(f"""
            QListWidget {{
                background-color: {LIGHTER_GREY.name()};
                color: {TEXT_COLOR_GREY.name()};
                border: 1px solid {QColor(90, 90, 90).name()};
                outline: none;
                padding: 5px;
            }}
            QListWidget::item {{
                padding: 5px;
            }}
            QListWidget::item:selected {{
                background-color: {HIGHLIGHT_PURPLE.name()};
                color: {QColor(255, 255, 255).name()};
            }}
            QListWidget::item:hover:!selected {{
                background-color: {QColor(80, 80, 80).name()};
            }}
        """)
        self.saved_notes_display.itemClicked.connect(self.display_selected_note)
        main_layout.addWidget(self.saved_notes_display)
        
        self.current_note_doc_id = None 

        self.load_all_notes_list() 

    def save_note(self):
        content = self.note_text_edit.toPlainText().strip()
        tags_str = self.tags_input.text().strip()
        tags = [tag.strip().lower() for tag in tags_str.split(',') if tag.strip()]

        if not content:
            QMessageBox.warning(self, "Empty Note", "Note content cannot be empty! Please enter some text.")
            return

        note_data = {
            "content": content,
            "tags": tags,
            "timestamp": QDateTime.currentDateTime().toString(Qt.ISODate) 
        }

        if self.current_note_doc_id:
            self.db.update(note_data, self.Note.doc_id == self.current_note_doc_id)
            QMessageBox.information(self, "Note Saved", f"Note updated: {self.current_note_doc_id}")
        else:
            doc_id = self.db.insert(note_data)
            self.current_note_doc_id = doc_id
            QMessageBox.information(self, "Note Saved", f"New note saved: {doc_id}")
            
        self.load_all_notes_list() 
        self.note_saved.emit() 

    def load_all_notes_list(self):
        self.saved_notes_display.clear()
        all_notes = self.db.all()
        all_notes.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        for note in all_notes:
            preview_content = note['content'].split('\n')[0] 
            preview_text = f"[{note['timestamp'].split('T')[0]}] {preview_content[:40]}... [{', '.join(note['tags'])}]" if note['content'] else f"[{note['timestamp'].split('T')[0]}] (No Content) [{', '.join(note['tags'])}]"
            item = QListWidgetItem(preview_text)
            item.setData(Qt.UserRole, note.doc_id) 
            self.saved_notes_display.addItem(item)

    def display_selected_note(self, item):
        doc_id = item.data(Qt.UserRole)
        note = self.db.get(doc_id=doc_id)
        if note:
            self.current_note_doc_id = doc_id
            self.note_text_edit.setPlainText(note.get("content", ""))
            self.tags_input.setText(", ".join(note.get("tags", [])))

    def clear_note_fields(self):
        self.note_text_edit.clear()
        self.tags_input.clear()
        self.current_note_doc_id = None 
        self.saved_notes_display.clearSelection() 
        QMessageBox.information(self, "New Note", "Fields cleared. Ready for a new note.")

    def delete_current_note(self):
        if self.current_note_doc_id:
            reply = QMessageBox.question(self, 'Confirm Delete', 
                                         "Are you sure you want to delete this note?", 
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.db.remove(doc_ids=[self.current_note_doc_id])
                QMessageBox.information(self, "Note Deleted", f"Note deleted: {self.current_note_doc_id}")
                self.clear_note_fields()
                self.load_all_notes_list()
                self.note_saved.emit() 
        else:
            QMessageBox.information(self, "No Note Selected", "Please select a note to delete from the list below.")

    def open_load_dialog(self):
        QMessageBox.information(self, "Load Note", 
                                "To load a note, please select one from the 'Saved Notes' list below.")

class NetworkScannersPage(QWidget):
    scan_finished = Signal(str) 
    scan_progress_update = Signal(int, str) 
    scan_output_append = Signal(str) 

    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        main_layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)

        title_label = QLabel("Network Scanners")
        title_label.setFont(get_sleek_font(30))
        title_label.setStyleSheet(f"color: {HIGHLIGHT_PURPLE.name()};")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        target_layout = QHBoxLayout()
        target_layout.setSpacing(10)
        target_layout.setAlignment(Qt.AlignLeft)

        target_label = QLabel("Target (IP/Hostname):")
        target_label.setFont(get_sleek_font(14, QFont.Normal))
        target_label.setStyleSheet(f"color: {TEXT_COLOR_GREY.name()};")
        target_layout.addWidget(target_label)

        self.target_input = QLineEdit("127.0.0.1") 
        self.target_input.setFont(get_sleek_font(12, QFont.Normal))
        self.target_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {LIGHTER_GREY.name()};
                color: {TEXT_COLOR_GREY.name()};
                border: 1px solid {QColor(90, 90, 90).name()};
                padding: 5px;
            }}
        """)
        target_layout.addWidget(self.target_input)
        main_layout.addLayout(target_layout)

        ports_layout = QHBoxLayout()
        ports_layout.setSpacing(10)
        ports_layout.setAlignment(Qt.AlignLeft)

        ports_label = QLabel("Ports (comma-separated or range):")
        ports_label.setFont(get_sleek_font(14, QFont.Normal))
        ports_label.setStyleSheet(f"color: {TEXT_COLOR_GREY.name()};")
        ports_layout.addWidget(ports_label)

        self.ports_input = QLineEdit("21,22,23,80,443,3389") 
        self.ports_input.setFont(get_sleek_font(12, QFont.Normal))
        self.ports_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {LIGHTER_GREY.name()};
                color: {TEXT_COLOR_GREY.name()};
                border: 1px solid {QColor(90, 90, 90).name()};
                padding: 5px;
            }}
        """)
        ports_layout.addWidget(self.ports_input)
        main_layout.addLayout(ports_layout)

        self.scan_button = QPushButton("Start Scan")
        self.scan_button.setFont(get_sleek_font(14))
        self.scan_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {HIGHLIGHT_PURPLE.name()};
                color: {QColor(255, 255, 255).name()};
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {QColor(150, 0, 150).name()};
            }}
        """)
        self.scan_button.clicked.connect(self.start_scan_thread)
        main_layout.addWidget(self.scan_button, alignment=Qt.AlignCenter)

        results_label = QLabel("Scan Results:")
        results_label.setFont(get_sleek_font(14, QFont.Normal))
        results_label.setStyleSheet(f"color: {TEXT_COLOR_GREY.name()};")
        main_layout.addWidget(results_label)

        self.results_text_edit = QTextEdit()
        self.results_text_edit.setFont(get_sleek_font(10, QFont.Normal))
        self.results_text_edit.setReadOnly(True)
        self.results_text_edit.setStyleSheet(f"""
            QTextEdit {{
                background-color: {LIGHTER_GREY.name()};
                color: {TEXT_COLOR_GREY.name()};
                border: 1px solid {QColor(90, 90, 90).name()};
                padding: 10px;
            }}
        """)
        main_layout.addWidget(self.results_text_edit)
        main_layout.addStretch()

        self.scan_finished.connect(self.handle_scan_finished)
        self.scan_progress_update.connect(self.update_progress_dialog)
        self.scan_output_append.connect(self.append_scan_output)

    def parse_ports(self, ports_str):
        ports = []
        parts = ports_str.split(',')
        for part in parts:
            part = part.strip()
            if '-' in part:
                try:
                    start, end = map(int, part.split('-'))
                    ports.extend(range(start, end + 1))
                except ValueError:
                    continue
            else:
                try:
                    ports.append(int(part))
                except ValueError:
                    continue
        return sorted(list(set(p for p in ports if 1 <= p <= 65535)))

    def _run_scan_in_thread(self, target, ports_to_scan):
        all_results = []
        try:
            target_ip = socket.gethostbyname(target)
            self.scan_output_append.emit(f"Scanning target: {target} ({target_ip})\n")
        except socket.gaierror:
            self.scan_output_append.emit(f"Error: Could not resolve hostname '{target}'. Please check the target.\n")
            self.scan_finished.emit("Scan completed with errors.")
            return

        open_ports = []
        for i, port in enumerate(ports_to_scan):
            if self.progress_dialog.wasCanceled(): 
                self.scan_output_append.emit("\nScan cancelled by user.")
                break 

            self.scan_progress_update.emit(i + 1, f"Scanning port {port}...") 
            
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5) 
                result = s.connect_ex((target_ip, port))
                if result == 0:
                    open_ports.append(port)
                    self.scan_output_append.emit(f"Port {port}: OPEN\n")
                else:
                    self.scan_output_append.emit(f"Port {port}: CLOSED\n") 
                s.close()
            except Exception as e:
                self.scan_output_append.emit(f"Error scanning port {port}: {e}\n")
            
        if open_ports:
            final_message = f"\nScan completed. Open ports: {', '.join(map(str, open_ports))}"
        else:
            final_message = "\nScan completed. No open ports found in the specified range."
        
        self.scan_finished.emit(final_message)


    def start_scan_thread(self):
        target = self.target_input.text().strip()
        ports_str = self.ports_input.text().strip()
        ports = self.parse_ports(ports_str)

        if not target:
            QMessageBox.warning(self, "Input Error", "Please enter a target IP address or hostname.")
            return
        if not ports:
            QMessageBox.warning(self, "Input Error", "Please enter valid ports to scan (e.g., 80,443 or 1-100).")
            return

        self.results_text_edit.clear()
        self.results_text_edit.append("Starting scan...\n")
        self.scan_button.setEnabled(False) 

        self.progress_dialog = QProgressDialog("Scanning ports...", "Cancel", 0, len(ports), self)
        self.progress_dialog.setWindowTitle("Network Scan Progress")
        self.progress_dialog.setWindowModality(Qt.WindowModal) 
        self.progress_dialog.setAutoClose(False) 
        self.progress_dialog.setCancelButtonText("Cancel Scan") 
        self.progress_dialog.canceled.connect(self.cancel_scan) 
        self.progress_dialog.show()

        self.scan_thread = threading.Thread(target=self._run_scan_in_thread, args=(target, ports))
        self.scan_thread.daemon = True 
        self.scan_thread.start()

    def update_progress_dialog(self, value, message):
        """Slot to update the QProgressDialog from the scan thread."""
        if hasattr(self, 'progress_dialog') and self.progress_dialog.isVisible():
            self.progress_dialog.setValue(value)
            self.progress_dialog.setLabelText(message)
            if value >= self.progress_dialog.maximum():
                self.progress_dialog.close()

    def append_scan_output(self, text):
        """Slot to append text to the results_text_edit from the scan thread."""
        self.results_text_edit.append(text)
        self.results_text_edit.verticalScrollBar().setValue(self.results_text_edit.verticalScrollBar().maximum())


    def handle_scan_finished(self, final_message):
        """Slot to handle scan completion or error."""
        self.scan_output_append.emit(final_message) 
        self.scan_button.setEnabled(True) 
        if hasattr(self, 'progress_dialog') and self.progress_dialog.isVisible():
            self.progress_dialog.close()

    def cancel_scan(self):
        """Handles the user clicking 'Cancel' on the progress dialog."""
        self.scan_button.setEnabled(True)
        if hasattr(self, 'progress_dialog') and self.progress_dialog.isVisible():
            self.progress_dialog.close()
        self.scan_output_append.emit("\nScan manually cancelled.")


class OsintDataFetchersPage(QWidget):
    fetch_finished = Signal(str)
    fetch_output_append = Signal(str)

    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        main_layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)

        title_label = QLabel("OSINT Data Fetchers")
        title_label.setFont(get_sleek_font(30))
        title_label.setStyleSheet(f"color: {HIGHLIGHT_PURPLE.name()};")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Target Input
        target_layout = QHBoxLayout()
        target_label = QLabel("Target (Domain/IP/URL):")
        target_label.setFont(get_sleek_font(14, QFont.Normal))
        target_label.setStyleSheet(f"color: {TEXT_COLOR_GREY.name()};")
        target_layout.addWidget(target_label)
        self.target_input = QLineEdit("example.com")
        self.target_input.setFont(get_sleek_font(12, QFont.Normal))
        self.target_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {LIGHTER_GREY.name()};
                color: {TEXT_COLOR_GREY.name()};
                border: 1px solid {QColor(90, 90, 90).name()};
                padding: 5px;
            }}
        """)
        target_layout.addWidget(self.target_input)
        main_layout.addLayout(target_layout)

        # Fetch Type Selector
        type_layout = QHBoxLayout()
        type_label = QLabel("Fetch Type:")
        type_label.setFont(get_sleek_font(14, QFont.Normal))
        type_label.setStyleSheet(f"color: {TEXT_COLOR_GREY.name()};")
        type_layout.addWidget(type_label)
        self.fetch_type_combo = QComboBox()
        self.fetch_type_combo.addItems(["HTTP Headers", "DNS Lookup (A/AAAA)", "WHOIS Lookup (Domain)"])
        self.fetch_type_combo.setFont(get_sleek_font(12, QFont.Normal))
        self.fetch_type_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {LIGHTER_GREY.name()};
                color: {TEXT_COLOR_GREY.name()};
                border: 1px solid {QColor(90, 90, 90).name()};
                padding: 5px;
                selection-background-color: {HIGHLIGHT_PURPLE.name()};
            }}
            QComboBox::drop-down {{
                border: 0px;
            }}
            QComboBox::down-arrow {{
                image: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {LIGHTER_GREY.name()};
                color: {TEXT_COLOR_GREY.name()};
                selection-background-color: {HIGHLIGHT_PURPLE.name()};
            }}
        """)
        type_layout.addWidget(self.fetch_type_combo)
        main_layout.addLayout(type_layout)

        # Fetch Button
        self.fetch_button = QPushButton("Fetch Data")
        self.fetch_button.setFont(get_sleek_font(14))
        self.fetch_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {HIGHLIGHT_PURPLE.name()};
                color: {QColor(255, 255, 255).name()};
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {QColor(150, 0, 150).name()};
            }}
        """)
        self.fetch_button.clicked.connect(self.start_fetch_thread)
        main_layout.addWidget(self.fetch_button, alignment=Qt.AlignCenter)

        # Results Display
        results_label = QLabel("Fetch Results:")
        results_label.setFont(get_sleek_font(14, QFont.Normal))
        results_label.setStyleSheet(f"color: {TEXT_COLOR_GREY.name()};")
        main_layout.addWidget(results_label)

        self.results_text_edit = QTextEdit()
        self.results_text_edit.setFont(get_sleek_font(10, QFont.Normal))
        self.results_text_edit.setReadOnly(True)
        self.results_text_edit.setStyleSheet(f"""
            QTextEdit {{
                background-color: {LIGHTER_GREY.name()};
                color: {TEXT_COLOR_GREY.name()};
                border: 1px solid {QColor(90, 90, 90).name()};
                padding: 10px;
            }}
        """)
        main_layout.addWidget(self.results_text_edit)
        main_layout.addStretch()

        self.fetch_finished.connect(self.handle_fetch_finished)
        self.fetch_output_append.connect(self.append_fetch_output)

    def _run_fetch_in_thread(self, target, fetch_type):
        self.fetch_output_append.emit(f"Starting {fetch_type} for: {target}\n")
        result_text = ""

        try:
            if fetch_type == "HTTP Headers":
                if requests is None:
                    result_text = "Error: 'requests' library not found. Please install it: pip install requests"
                else:
                    if not target.startswith("http://") and not target.startswith("https://"):
                        target = "http://" + target # Default to http if no scheme
                    try:
                        response = requests.head(target, allow_redirects=True, timeout=10)
                        result_text += f"Status Code: {response.status_code}\n"
                        result_text += "HTTP Headers:\n"
                        for header, value in response.headers.items():
                            result_text += f"  {header}: {value}\n"
                    except requests.exceptions.RequestException as e:
                        result_text = f"Error fetching HTTP Headers: {e}"

            elif fetch_type == "DNS Lookup (A/AAAA)":
                try:
                    ip_addresses = socket.getaddrinfo(target, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
                    seen_ips = set()
                    for ip_info in ip_addresses:
                        ip_address = ip_info[4][0]
                        if ip_address not in seen_ips:
                            result_text += f"Resolved IP: {ip_address}\n"
                            seen_ips.add(ip_address)
                    if not seen_ips:
                         result_text = f"No IP addresses found for {target}.\n"
                except socket.gaierror:
                    result_text = f"Error: Could not resolve DNS for '{target}'. Invalid hostname or network issue."

            elif fetch_type == "WHOIS Lookup (Domain)":
                if whois is None:
                    result_text = "Error: 'python-whois' library not found. Please install it: pip install python-whois"
                else:
                    try:
                        # Attempt to make sure it's just a domain name
                        domain_only = target.replace("http://", "").replace("https://", "").split("/")[0]
                        if not "." in domain_only:
                            result_text = "Error: Invalid domain for WHOIS lookup. Please provide a domain name (e.g., example.com)."
                        else:
                            obj = whois.whois(domain_only)
                            if isinstance(obj.text, str): # Raw text from whois
                                result_text = obj.text
                            else: # whois object (newer versions)
                                result_text += f"Domain: {obj.domain}\n"
                                result_text += f"Registrar: {obj.registrar}\n"
                                result_text += f"Creation Date: {obj.creation_date}\n"
                                result_text += f"Expiration Date: {obj.expiration_date}\n"
                                result_text += f"Updated Date: {obj.updated_date}\n"
                                result_text += f"Name Servers: {', '.join(obj.name_servers) if obj.name_servers else 'N/A'}\n"
                                if obj.emails:
                                    result_text += f"Emails: {', '.join(obj.emails)}\n"
                                if obj.org:
                                    result_text += f"Organization: {obj.org}\n"
                                if obj.address:
                                    result_text += f"Address: {obj.address}\n"
                                if obj.city:
                                    result_text += f"City: {obj.city}\n"
                                if obj.state:
                                    result_text += f"State: {obj.state}\n"
                                if obj.zipcode:
                                    result_text += f"Zipcode: {obj.zipcode}\n"
                                if obj.country:
                                    result_text += f"Country: {obj.country}\n"
                                result_text += "\n(Raw WHOIS output may be available in the console or by inspecting the object details)"
                    except whois.parser.PywhoisError as e:
                        result_text = f"WHOIS Error: {e}. Domain might not exist or WHOIS server is unavailable."
                    except Exception as e:
                        result_text = f"An unexpected error occurred during WHOIS lookup: {e}"

            else:
                result_text = "Error: Unknown fetch type selected."

        except Exception as e:
            result_text = f"An unexpected error occurred: {e}"
        
        self.fetch_finished.emit(result_text)

    def start_fetch_thread(self):
        target = self.target_input.text().strip()
        fetch_type = self.fetch_type_combo.currentText()

        if not target:
            QMessageBox.warning(self, "Input Error", "Please enter a target (Domain, IP, or URL).")
            return

        self.results_text_edit.clear()
        self.results_text_edit.append(f"Fetching {fetch_type} for {target}...\n")
        self.fetch_button.setEnabled(False)

        self.fetch_thread = threading.Thread(target=self._run_fetch_in_thread, args=(target, fetch_type))
        self.fetch_thread.daemon = True
        self.fetch_thread.start()

    def handle_fetch_finished(self, result_text):
        self.append_fetch_output(result_text)
        self.fetch_button.setEnabled(True)

    def append_fetch_output(self, text):
        self.results_text_edit.append(text)
        self.results_text_edit.verticalScrollBar().setValue(self.results_text_edit.verticalScrollBar().maximum())


class PassiveMonitoringToolsPage(QWidget):
    monitor_output_append = Signal(str)
    monitor_finished = Signal(str)

    def __init__(self):
        super().__init__()
        self.db = TinyDB(DATABASE_PATH)
        self.FimQuery = Query()
        self.monitored_path_id = None # To track which path is currently being monitored

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        main_layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)

        title_label = QLabel("Passive Monitoring Tools (File Integrity Monitoring)")
        title_label.setFont(get_sleek_font(30))
        title_label.setStyleSheet(f"color: {HIGHLIGHT_PURPLE.name()};")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Path Input
        path_layout = QHBoxLayout()
        path_label = QLabel("Path to Monitor (File or Folder):")
        path_label.setFont(get_sleek_font(14, QFont.Normal))
        path_label.setStyleSheet(f"color: {TEXT_COLOR_GREY.name()};")
        path_layout.addWidget(path_label)
        self.path_input = QLineEdit()
        self.path_input.setFont(get_sleek_font(12, QFont.Normal))
        self.path_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {LIGHTER_GREY.name()};
                color: {TEXT_COLOR_GREY.name()};
                border: 1px solid {QColor(90, 90, 90).name()};
                padding: 5px;
            }}
        """)
        path_layout.addWidget(self.path_input)

        self.browse_button = QPushButton("Browse")
        self.browse_button.setFont(get_sleek_font(12))
        self.browse_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {QColor(90, 90, 90).name()};
                color: {QColor(255, 255, 255).name()};
                border: none;
                padding: 5px 10px;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {QColor(110, 110, 110).name()};
            }}
        """)
        self.browse_button.clicked.connect(self.browse_path)
        path_layout.addWidget(self.browse_button)
        main_layout.addLayout(path_layout)

        # Action Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setAlignment(Qt.AlignCenter)

        self.initialize_button = QPushButton("Initialize Monitoring")
        self.initialize_button.setFont(get_sleek_font(14))
        self.initialize_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {HIGHLIGHT_PURPLE.name()};
                color: {QColor(255, 255, 255).name()};
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {QColor(150, 0, 150).name()};
            }}
        """)
        self.initialize_button.clicked.connect(self.start_initialize_thread)
        button_layout.addWidget(self.initialize_button)

        self.check_button = QPushButton("Check for Changes")
        self.check_button.setFont(get_sleek_font(14))
        self.check_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {HIGHLIGHT_PURPLE.name()};
                color: {QColor(255, 255, 255).name()};
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {QColor(150, 0, 150).name()};
            }}
        """)
        self.check_button.clicked.connect(self.start_check_thread)
        self.check_button.setEnabled(False) # Disable until initialized
        button_layout.addWidget(self.check_button)
        
        self.stop_button = QPushButton("Stop Monitoring")
        self.stop_button.setFont(get_sleek_font(14))
        self.stop_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {HIGHLIGHT_PURPLE.name()};
                color: {QColor(255, 255, 255).name()};
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {QColor(150, 0, 150).name()};
            }}
        """)
        self.stop_button.clicked.connect(self.stop_monitoring)
        self.stop_button.setEnabled(False) # Disable until initialized
        button_layout.addWidget(self.stop_button)

        main_layout.addLayout(button_layout)

        # Results Display
        results_label = QLabel("Monitoring Status/Results:")
        results_label.setFont(get_sleek_font(14, QFont.Normal))
        results_label.setStyleSheet(f"color: {TEXT_COLOR_GREY.name()};")
        main_layout.addWidget(results_label)

        self.results_text_edit = QTextEdit()
        self.results_text_edit.setFont(get_sleek_font(10, QFont.Normal))
        self.results_text_edit.setReadOnly(True)
        self.results_text_edit.setStyleSheet(f"""
            QTextEdit {{
                background-color: {LIGHTER_GREY.name()};
                color: {TEXT_COLOR_GREY.name()};
                border: 1px solid {QColor(90, 90, 90).name()};
                padding: 10px;
            }}
        """)
        main_layout.addWidget(self.results_text_edit)
        main_layout.addStretch()

        self.monitor_output_append.connect(self.append_monitor_output)
        self.monitor_finished.connect(self.handle_monitor_finished)
        
        # Check if a path is already being monitored from previous session
        self._load_monitored_path_status()

    def _hash_file(self, filepath, block_size=65536):
        """Calculates the SHA256 hash of a file."""
        sha256 = hashlib.sha256()
        try:
            with open(filepath, 'rb') as f:
                for block in iter(lambda: f.read(block_size), b''):
                    sha256.update(block)
            return sha256.hexdigest()
        except IOError:
            return None # File not found or inaccessible

    def _get_file_hashes_in_path(self, path):
        """Recursively gets SHA256 hashes for all files in a given path."""
        hashes = {}
        if os.path.isfile(path):
            file_hash = self._hash_file(path)
            if file_hash:
                hashes[path] = file_hash
        elif os.path.isdir(path):
            for root, _, files in os.walk(path):
                for file in files:
                    filepath = os.path.join(root, file)
                    if os.path.islink(filepath): # Skip symbolic links
                        continue
                    file_hash = self._hash_file(filepath)
                    if file_hash:
                        hashes[filepath] = file_hash
        return hashes

    def browse_path(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.Directory) # Default to directory
        dialog.setOption(QFileDialog.Option.ShowDirsOnly, False) # Allow selecting files too
        dialog.setWindowTitle("Select File or Folder to Monitor")

        # Customize for file selection if needed
        # dialog.setNameFilter("All Files (*.*)") 
        # dialog.setFileMode(QFileDialog.FileMode.ExistingFile) # For single file

        if dialog.exec():
            selected_path = dialog.selectedFiles()[0]
            self.path_input.setText(selected_path)
            self._load_monitored_path_status(selected_path)


    def _load_monitored_path_status(self, current_path=None):
        """Checks if the current path (or specified path) is already monitored and updates UI buttons."""
        path_to_check = current_path if current_path else self.path_input.text().strip()
        
        monitored_entry = self.db.get(self.FimQuery.path == path_to_check)
        if monitored_entry:
            self.monitored_path_id = monitored_entry.doc_id
            self.initialize_button.setEnabled(False)
            self.check_button.setEnabled(True)
            self.stop_button.setEnabled(True)
            self.monitor_output_append.emit(f"Monitoring is active for: {path_to_check}\n")
        else:
            self.monitored_path_id = None
            self.initialize_button.setEnabled(True)
            self.check_button.setEnabled(False)
            self.stop_button.setEnabled(False)
            self.monitor_output_append.emit(f"No active monitoring for: {path_to_check}\n")

    def _run_initialize_in_thread(self, path):
        self.monitor_output_append.emit(f"Initializing monitoring for: {path}...\n")
        try:
            current_hashes = self._get_file_hashes_in_path(path)
            if not current_hashes:
                self.monitor_finished.emit(f"Error: No files found or accessible at '{path}' to monitor. Make sure the path is correct and accessible.\n")
                return

            # Remove any existing monitoring for this path before adding new
            self.db.remove(self.FimQuery.path == path)
            doc_id = self.db.insert({"path": path, "hashes": current_hashes, "timestamp": QDateTime.currentDateTime().toString(Qt.ISODate)})
            self.monitored_path_id = doc_id
            self.monitor_finished.emit(f"Monitoring initialized successfully for '{path}'. Baseline set. ({len(current_hashes)} files hashed)\n")
        except Exception as e:
            self.monitor_finished.emit(f"Error initializing monitoring: {e}\n")

    def _run_check_in_thread(self, path):
        self.monitor_output_append.emit(f"Checking for changes in: {path}...\n")
        try:
            monitored_entry = self.db.get(doc_id=self.monitored_path_id)
            if not monitored_entry:
                self.monitor_finished.emit("Error: No baseline found for this path. Please initialize monitoring first.\n")
                return

            baseline_hashes = monitored_entry['hashes']
            current_hashes = self._get_file_hashes_in_path(path)

            changes_found = False
            report = []

            # Check for modified or deleted files
            for filepath, baseline_hash in baseline_hashes.items():
                if filepath not in current_hashes:
                    report.append(f"  - DELETED: {filepath}")
                    changes_found = True
                elif current_hashes[filepath] != baseline_hash:
                    report.append(f"  - MODIFIED: {filepath} (Old Hash: {baseline_hash[:8]}..., New Hash: {current_hashes[filepath][:8]}...)")
                    changes_found = True

            # Check for new files
            for filepath in current_hashes:
                if filepath not in baseline_hashes:
                    report.append(f"  - NEW: {filepath} (Hash: {current_hashes[filepath][:8]}...)")
                    changes_found = True
            
            if changes_found:
                report.insert(0, f"Changes detected in '{path}':")
                self.monitor_finished.emit("\n".join(report) + "\n")
            else:
                self.monitor_finished.emit(f"No changes detected in '{path}' since last baseline.\n")

        except Exception as e:
            self.monitor_finished.emit(f"Error checking for changes: {e}\n")


    def start_initialize_thread(self):
        path = self.path_input.text().strip()
        if not path:
            QMessageBox.warning(self, "Input Error", "Please select a file or folder to monitor.")
            return
        if not os.path.exists(path):
            QMessageBox.warning(self, "Path Error", "The specified path does not exist. Please check it.")
            return

        self.results_text_edit.clear()
        self.initialize_button.setEnabled(False)
        self.check_button.setEnabled(False)
        self.stop_button.setEnabled(False)

        self.monitor_thread = threading.Thread(target=self._run_initialize_in_thread, args=(path,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def start_check_thread(self):
        path = self.path_input.text().strip()
        if not self.monitored_path_id:
            QMessageBox.warning(self, "Monitoring Not Initialized", "Please initialize monitoring for this path first.")
            return
        if not os.path.exists(path):
            QMessageBox.warning(self, "Path Error", "The monitored path no longer exists. Please re-initialize monitoring.")
            self.stop_monitoring() # Automatically stop if path is gone
            return

        self.results_text_edit.clear()
        self.initialize_button.setEnabled(False)
        self.check_button.setEnabled(False)
        self.stop_button.setEnabled(False)

        self.monitor_thread = threading.Thread(target=self._run_check_in_thread, args=(path,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def stop_monitoring(self):
        path = self.path_input.text().strip()
        if self.monitored_path_id:
            reply = QMessageBox.question(self, 'Confirm Stop', 
                                         f"Are you sure you want to stop monitoring '{path}' and clear its baseline?", 
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.db.remove(doc_ids=[self.monitored_path_id])
                self.monitored_path_id = None
                self.monitor_output_append.emit(f"Monitoring stopped and baseline cleared for '{path}'.\n")
                self.path_input.clear() # Clear path after stopping
                self.initialize_button.setEnabled(True)
                self.check_button.setEnabled(False)
                self.stop_button.setEnabled(False)
        else:
            QMessageBox.information(self, "No Active Monitoring", "No path is currently being monitored.")


    def handle_monitor_finished(self, result_text):
        self.append_monitor_output(result_text)
        self.initialize_button.setEnabled(True)
        self.check_button.setEnabled(self.monitored_path_id is not None)
        self.stop_button.setEnabled(self.monitored_path_id is not None)
        # Reload status to ensure button states are correct based on current path
        self._load_monitored_path_status(self.path_input.text().strip())


    def append_monitor_output(self, text):
        self.results_text_edit.append(text)
        self.results_text_edit.verticalScrollBar().setValue(self.results_text_edit.verticalScrollBar().maximum())

class PasswordManagersPage(QWidget):
    def __init__(self):
        super().__init__()
        self.db = TinyDB(DATABASE_PATH)
        self.Password = Query()
        self.current_password_doc_id = None

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        main_layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)

        title_label = QLabel("Password Generator & Manager (DEMO)")
        title_label.setFont(get_sleek_font(30))
        title_label.setStyleSheet(f"color: {HIGHLIGHT_PURPLE.name()};")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # --- IMPORTANT SECURITY DISCLAIMER ---
        self.security_warning_label = QLabel(
            "<p style='color: red; font-weight: bold;'>WARNING: This is a DEMO password manager. Passwords are NOT SECURELY ENCRYPTED for this demonstration and should NEVER be used for real, sensitive credentials. For production use, a robust encryption method (e.g., using a master password and strong cryptographic libraries) is essential.</p>"
        )
        self.security_warning_label.setFont(get_sleek_font(10, QFont.Bold))
        self.security_warning_label.setAlignment(Qt.AlignCenter)
        self.security_warning_label.setWordWrap(True)
        main_layout.addWidget(self.security_warning_label)
        # --- END DISCLAIMER ---

        # Password Generation Section
        generator_group_layout = QVBoxLayout()
        generator_group_layout.setSpacing(10)
        generator_group_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        gen_title_label = QLabel("Password Generator:")
        gen_title_label.setFont(get_sleek_font(16, QFont.Bold))
        gen_title_label.setStyleSheet(f"color: {TEXT_COLOR_GREY.name()};")
        generator_group_layout.addWidget(gen_title_label)

        length_layout = QHBoxLayout()
        length_layout.addWidget(QLabel(f"<span style='color: {TEXT_COLOR_GREY.name()};'>Length:</span>"))
        self.length_spinbox = QSpinBox()
        self.length_spinbox.setMinimum(8)
        self.length_spinbox.setMaximum(64)
        self.length_spinbox.setValue(16)
        self.length_spinbox.setStyleSheet(f"""
            QSpinBox {{
                background-color: {LIGHTER_GREY.name()};
                color: {TEXT_COLOR_GREY.name()};
                border: 1px solid {QColor(90, 90, 90).name()};
                padding: 2px;
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                width: 16px;
                border: 1px solid {QColor(90, 90, 90).name()};
                background-color: {QColor(80, 80, 80).name()};
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background-color: {QColor(100, 100, 100).name()};
            }}
        """)
        length_layout.addWidget(self.length_spinbox)
        generator_group_layout.addLayout(length_layout)

        chars_layout = QHBoxLayout()
        chars_layout.addWidget(QLabel(f"<span style='color: {TEXT_COLOR_GREY.name()};'>Include:</span>"))
        self.lower_checkbox = QCheckBox("Lowercase (a-z)")
        self.upper_checkbox = QCheckBox("Uppercase (A-Z)")
        self.digits_checkbox = QCheckBox("Digits (0-9)")
        self.symbols_checkbox = QCheckBox("Symbols (!@#$)")

        checkbox_style = f"color: {TEXT_COLOR_GREY.name()};"
        self.lower_checkbox.setStyleSheet(checkbox_style)
        self.upper_checkbox.setStyleSheet(checkbox_style)
        self.digits_checkbox.setStyleSheet(checkbox_style)
        self.symbols_checkbox.setStyleSheet(checkbox_style)

        self.lower_checkbox.setChecked(True)
        self.upper_checkbox.setChecked(True)
        self.digits_checkbox.setChecked(True)
        self.symbols_checkbox.setChecked(True)

        chars_layout.addWidget(self.lower_checkbox)
        chars_layout.addWidget(self.upper_checkbox)
        chars_layout.addWidget(self.digits_checkbox)
        chars_layout.addWidget(self.symbols_checkbox)
        chars_layout.addStretch()
        generator_group_layout.addLayout(chars_layout)

        self.generate_button = QPushButton("Generate Password")
        self.generate_button.clicked.connect(self.generate_password)
        self.generate_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {HIGHLIGHT_PURPLE.name()};
                color: {QColor(255, 255, 255).name()};
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {QColor(150, 0, 150).name()}; 
            }}
        """)
        generator_group_layout.addWidget(self.generate_button, alignment=Qt.AlignLeft)

        generated_password_layout = QHBoxLayout()
        generated_password_layout.addWidget(QLabel(f"<span style='color: {TEXT_COLOR_GREY.name()};'>Generated:</span>"))
        self.generated_password_display = QLineEdit()
        self.generated_password_display.setReadOnly(True)
        self.generated_password_display.setFont(get_sleek_font(12))
        self.generated_password_display.setStyleSheet(f"""
            QLineEdit {{
                background-color: {LIGHTER_GREY.name()};
                color: {TEXT_COLOR_GREY.name()};
                border: 1px solid {QColor(90, 90, 90).name()};
                padding: 5px;
            }}
        """)
        generated_password_layout.addWidget(self.generated_password_display)

        self.copy_button = QPushButton("Copy")
        self.copy_button.clicked.connect(self.copy_password_to_clipboard)
        self.copy_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {QColor(90, 90, 90).name()};
                color: {QColor(255, 255, 255).name()};
                border: none;
                padding: 5px 10px;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {QColor(110, 110, 110).name()};
            }}
        """)
        generated_password_layout.addWidget(self.copy_button)
        generator_group_layout.addLayout(generated_password_layout)

        main_layout.addLayout(generator_group_layout)
        main_layout.addSpacing(25)

        # Password Storage Section
        storage_group_layout = QVBoxLayout()
        storage_group_layout.setSpacing(10)
        storage_group_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        store_title_label = QLabel("Saved Passwords (DEMO Storage):")
        store_title_label.setFont(get_sleek_font(16, QFont.Bold))
        store_title_label.setStyleSheet(f"color: {TEXT_COLOR_GREY.name()};")
        storage_group_layout.addWidget(store_title_label)

        form_layout = QVBoxLayout()
        form_layout.setSpacing(8)

        service_layout = QHBoxLayout()
        service_layout.addWidget(QLabel(f"<span style='color: {TEXT_COLOR_GREY.name()};'>Service:</span>"))
        self.service_input = QLineEdit()
        self.service_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {LIGHTER_GREY.name()};
                color: {TEXT_COLOR_GREY.name()};
                border: 1px solid {QColor(90, 90, 90).name()};
                padding: 5px;
            }}
        """)
        service_layout.addWidget(self.service_input)
        form_layout.addLayout(service_layout)

        username_layout = QHBoxLayout()
        username_layout.addWidget(QLabel(f"<span style='color: {TEXT_COLOR_GREY.name()};'>Username:</span>"))
        self.username_input = QLineEdit()
        self.username_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {LIGHTER_GREY.name()};
                color: {TEXT_COLOR_GREY.name()};
                border: 1px solid {QColor(90, 90, 90).name()};
                padding: 5px;
            }}
        """)
        username_layout.addWidget(self.username_input)
        form_layout.addLayout(username_layout)

        password_store_layout = QHBoxLayout()
        password_store_layout.addWidget(QLabel(f"<span style='color: {TEXT_COLOR_GREY.name()};'>Password:</span>"))
        self.stored_password_input = QLineEdit()
        self.stored_password_input.setEchoMode(QLineEdit.Password)
        self.stored_password_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {LIGHTER_GREY.name()};
                color: {TEXT_COLOR_GREY.name()};
                border: 1px solid {QColor(90, 90, 90).name()};
                padding: 5px;
            }}
        """)
        password_store_layout.addWidget(self.stored_password_input)
        self.show_hide_password_button = QPushButton("Show")
        self.show_hide_password_button.setCheckable(True)
        self.show_hide_password_button.clicked.connect(self.toggle_password_visibility)
        self.show_hide_password_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {QColor(90, 90, 90).name()};
                color: {QColor(255, 255, 255).name()};
                border: none;
                padding: 5px 10px;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {QColor(110, 110, 110).name()};
            }}
            QPushButton:checked {{
                background-color: {HIGHLIGHT_PURPLE.name()};
            }}
        """)
        password_store_layout.addWidget(self.show_hide_password_button)
        form_layout.addLayout(password_store_layout)
        storage_group_layout.addLayout(form_layout)

        storage_buttons_layout = QHBoxLayout()
        self.save_password_button = QPushButton("Save Password")
        self.save_password_button.clicked.connect(self.save_password_entry)
        self.new_entry_button = QPushButton("New Entry")
        self.new_entry_button.clicked.connect(self.clear_password_fields)
        self.delete_entry_button = QPushButton("Delete Entry")
        self.delete_entry_button.clicked.connect(self.delete_password_entry)

        storage_button_style = f"""
            QPushButton {{
                background-color: {HIGHLIGHT_PURPLE.name()};
                color: {QColor(255, 255, 255).name()};
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {QColor(150, 0, 150).name()}; 
            }}
        """
        self.save_password_button.setStyleSheet(storage_button_style)
        self.new_entry_button.setStyleSheet(storage_button_style)
        self.delete_entry_button.setStyleSheet(storage_button_style)

        storage_buttons_layout.addWidget(self.save_password_button)
        storage_buttons_layout.addWidget(self.new_entry_button)
        storage_buttons_layout.addWidget(self.delete_entry_button)
        storage_buttons_layout.addStretch()
        storage_group_layout.addLayout(storage_buttons_layout)
        
        main_layout.addLayout(storage_group_layout)

        self.saved_passwords_list = QListWidget()
        self.saved_passwords_list.setFont(get_sleek_font(12, QFont.Normal))
        self.saved_passwords_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {LIGHTER_GREY.name()};
                color: {TEXT_COLOR_GREY.name()};
                border: 1px solid {QColor(90, 90, 90).name()};
                outline: none;
                padding: 5px;
            }}
            QListWidget::item {{
                padding: 5px;
            }}
            QListWidget::item:selected {{
                background-color: {HIGHLIGHT_PURPLE.name()};
                color: {QColor(255, 255, 255).name()};
            }}
            QListWidget::item:hover:!selected {{
                background-color: {QColor(80, 80, 80).name()};
            }}
        """)
        self.saved_passwords_list.itemClicked.connect(self.display_selected_password)
        main_layout.addWidget(self.saved_passwords_list)
        main_layout.addStretch()

        self.load_all_password_entries()

    def generate_password(self):
        length = self.length_spinbox.value()
        chars = ''
        if self.lower_checkbox.isChecked():
            chars += string.ascii_lowercase
        if self.upper_checkbox.isChecked():
            chars += string.ascii_uppercase
        if self.digits_checkbox.isChecked():
            chars += string.digits
        if self.symbols_checkbox.isChecked():
            chars += string.punctuation

        if not chars:
            QMessageBox.warning(self, "Selection Error", "Please select at least one character type.")
            return

        # Ensure at least one character from each selected category is included (if possible)
        password_list = []
        if self.lower_checkbox.isChecked():
            password_list.append(random.choice(string.ascii_lowercase))
        if self.upper_checkbox.isChecked():
            password_list.append(random.choice(string.ascii_uppercase))
        if self.digits_checkbox.isChecked():
            password_list.append(random.choice(string.digits))
        if self.symbols_checkbox.isChecked():
            password_list.append(random.choice(string.punctuation))
        
        # Fill the rest of the password length
        if len(password_list) < length:
            password_list.extend(random.choice(chars) for _ in range(length - len(password_list)))
        
        random.shuffle(password_list)
        generated_password = "".join(password_list)
        
        self.generated_password_display.setText(generated_password)
        self.stored_password_input.setText(generated_password) # Pre-fill for saving

    def copy_password_to_clipboard(self):
        clipboard = QApplication.clipboard()
        password = self.generated_password_display.text()
        if password:
            clipboard.setText(password)
            QMessageBox.information(self, "Copied!", "Generated password copied to clipboard.")
        else:
            QMessageBox.warning(self, "No Password", "No password to copy.")

    def toggle_password_visibility(self):
        if self.show_hide_password_button.isChecked():
            self.stored_password_input.setEchoMode(QLineEdit.Normal)
            self.show_hide_password_button.setText("Hide")
        else:
            self.stored_password_input.setEchoMode(QLineEdit.Password)
            self.show_hide_password_button.setText("Show")

    def save_password_entry(self):
        service = self.service_input.text().strip()
        username = self.username_input.text().strip()
        password = self.stored_password_input.text() # Get text directly, not echo mode

        if not service or not username or not password:
            QMessageBox.warning(self, "Missing Information", "Service, Username, and Password fields cannot be empty.")
            return

        password_data = {
            "service": service,
            "username": username,
            "password": password, # WARNING: Stored as plain text for DEMO purposes ONLY
            "timestamp": QDateTime.currentDateTime().toString(Qt.ISODate)
        }

        if self.current_password_doc_id:
            self.db.update(password_data, self.Password.doc_id == self.current_password_doc_id)
            QMessageBox.information(self, "Password Saved", f"Entry updated for: {service}")
        else:
            # Check for existing service/username pair to prevent duplicates
            existing_entry = self.db.get((self.Password.service == service) & (self.Password.username == username))
            if existing_entry:
                reply = QMessageBox.question(self, "Entry Exists", 
                                             f"An entry for '{service}' with username '{username}' already exists. Do you want to update it?",
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.db.update(password_data, self.Password.doc_id == existing_entry.doc_id)
                    self.current_password_doc_id = existing_entry.doc_id # Set current doc_id for update
                    QMessageBox.information(self, "Password Saved", f"Entry updated for: {service}")
                else:
                    return # User chose not to update, so do nothing
            else:
                doc_id = self.db.insert(password_data)
                self.current_password_doc_id = doc_id
                QMessageBox.information(self, "Password Saved", f"New entry saved for: {service}")

        self.load_all_password_entries()
        # Optionally, clear fields after save
        # self.clear_password_fields()

    def load_all_password_entries(self):
        self.saved_passwords_list.clear()
        all_entries = self.db.all()
        all_entries.sort(key=lambda x: x.get("service", "").lower()) # Sort by service name
        for entry in all_entries:
            item_text = f"Service: {entry.get('service', 'N/A')} | User: {entry.get('username', 'N/A')}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, entry.doc_id)
            self.saved_passwords_list.addItem(item)

    def display_selected_password(self, item):
        doc_id = item.data(Qt.UserRole)
        entry = self.db.get(doc_id=doc_id)
        if entry:
            self.current_password_doc_id = doc_id
            self.service_input.setText(entry.get("service", ""))
            self.username_input.setText(entry.get("username", ""))
            self.stored_password_input.setText(entry.get("password", ""))
            self.show_hide_password_button.setChecked(False) # Reset show/hide
            self.stored_password_input.setEchoMode(QLineEdit.Password) # Ensure masked

    def clear_password_fields(self):
        self.service_input.clear()
        self.username_input.clear()
        self.stored_password_input.clear()
        self.generated_password_display.clear()
        self.current_password_doc_id = None
        self.saved_passwords_list.clearSelection()
        self.show_hide_password_button.setChecked(False) # Reset show/hide
        self.stored_password_input.setEchoMode(QLineEdit.Password) # Ensure masked
        QMessageBox.information(self, "New Entry", "Fields cleared. Ready for a new password entry.")

    def delete_password_entry(self):
        if self.current_password_doc_id:
            reply = QMessageBox.question(self, 'Confirm Delete',
                                         "Are you sure you want to delete this password entry?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.db.remove(doc_ids=[self.current_password_doc_id])
                QMessageBox.information(self, "Entry Deleted", "Password entry deleted.")
                self.clear_password_fields()
                self.load_all_password_entries()
        else:
            QMessageBox.information(self, "No Entry Selected", "Please select an entry to delete from the list.")


class FileHashingPage(QWidget):
    hash_calculated = Signal(str, str) # Emits (algorithm, hash_value)
    error_occurred = Signal(str) # Emits (error_message)

    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        main_layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)

        title_label = QLabel("File Hashing & Integrity Verification")
        title_label.setFont(get_sleek_font(30))
        title_label.setStyleSheet(f"color: {HIGHLIGHT_PURPLE.name()};")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # File Selection
        file_layout = QHBoxLayout()
        file_label = QLabel("Select File:")
        file_label.setFont(get_sleek_font(14, QFont.Normal))
        file_label.setStyleSheet(f"color: {TEXT_COLOR_GREY.name()};")
        file_layout.addWidget(file_label)
        
        self.file_path_input = QLineEdit()
        self.file_path_input.setFont(get_sleek_font(12, QFont.Normal))
        self.file_path_input.setPlaceholderText("No file selected...")
        self.file_path_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {LIGHTER_GREY.name()};
                color: {TEXT_COLOR_GREY.name()};
                border: 1px solid {QColor(90, 90, 90).name()};
                padding: 5px;
            }}
        """)
        file_layout.addWidget(self.file_path_input)

        self.browse_file_button = QPushButton("Browse")
        self.browse_file_button.setFont(get_sleek_font(12))
        self.browse_file_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {QColor(90, 90, 90).name()};
                color: {QColor(255, 255, 255).name()};
                border: none;
                padding: 5px 10px;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {QColor(110, 110, 110).name()};
            }}
        """)
        self.browse_file_button.clicked.connect(self.browse_file)
        file_layout.addWidget(self.browse_file_button)
        main_layout.addLayout(file_layout)

        # Hashing Algorithm Selection
        algo_layout = QHBoxLayout()
        algo_label = QLabel("Hashing Algorithm:")
        algo_label.setFont(get_sleek_font(14, QFont.Normal))
        algo_label.setStyleSheet(f"color: {TEXT_COLOR_GREY.name()};")
        algo_layout.addWidget(algo_label)
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems(["MD5", "SHA1", "SHA256", "SHA512"])
        self.algorithm_combo.setFont(get_sleek_font(12, QFont.Normal))
        self.algorithm_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {LIGHTER_GREY.name()};
                color: {TEXT_COLOR_GREY.name()};
                border: 1px solid {QColor(90, 90, 90).name()};
                padding: 5px;
                selection-background-color: {HIGHLIGHT_PURPLE.name()};
            }}
            QComboBox::drop-down {{
                border: 0px;
            }}
            QComboBox::down-arrow {{
                image: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {LIGHTER_GREY.name()};
                color: {TEXT_COLOR_GREY.name()};
                selection-background-color: {HIGHLIGHT_PURPLE.name()};
            }}
        """)
        algo_layout.addWidget(self.algorithm_combo)
        main_layout.addLayout(algo_layout)

        # Calculate Button
        self.calculate_button = QPushButton("Calculate Hash")
        self.calculate_button.setFont(get_sleek_font(14))
        self.calculate_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {HIGHLIGHT_PURPLE.name()};
                color: {QColor(255, 255, 255).name()};
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {QColor(150, 0, 150).name()};
            }}
        """)
        self.calculate_button.clicked.connect(self.start_hash_calculation)
        main_layout.addWidget(self.calculate_button, alignment=Qt.AlignCenter)

        # Results Display
        results_label = QLabel("Calculated Hash:")
        results_label.setFont(get_sleek_font(14, QFont.Normal))
        results_label.setStyleSheet(f"color: {TEXT_COLOR_GREY.name()};")
        main_layout.addWidget(results_label)

        self.hash_results_text = QTextEdit()
        self.hash_results_text.setFont(get_sleek_font(10, QFont.Normal))
        self.hash_results_text.setReadOnly(True)
        self.hash_results_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {LIGHTER_GREY.name()};
                color: {TEXT_COLOR_GREY.name()};
                border: 1px solid {QColor(90, 90, 90).name()};
                padding: 10px;
            }}
        """)
        main_layout.addWidget(self.hash_results_text)
        
        # Hash Comparison Section
        comparison_group_layout = QVBoxLayout()
        comparison_group_layout.setSpacing(10)
        comparison_group_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        compare_title_label = QLabel("Hash Comparison:")
        compare_title_label.setFont(get_sleek_font(16, QFont.Bold))
        compare_title_label.setStyleSheet(f"color: {TEXT_COLOR_GREY.name()};")
        comparison_group_layout.addWidget(compare_title_label)

        expected_hash_layout = QHBoxLayout()
        expected_hash_layout.addWidget(QLabel(f"<span style='color: {TEXT_COLOR_GREY.name()};'>Expected Hash:</span>"))
        self.expected_hash_input = QLineEdit()
        self.expected_hash_input.setFont(get_sleek_font(10, QFont.Normal))
        self.expected_hash_input.setPlaceholderText("Paste hash here for comparison...")
        self.expected_hash_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {LIGHTER_GREY.name()};
                color: {TEXT_COLOR_GREY.name()};
                border: 1px solid {QColor(90, 90, 90).name()};
                padding: 5px;
            }}
        """)
        expected_hash_layout.addWidget(self.expected_hash_input)
        comparison_group_layout.addLayout(expected_hash_layout)

        self.compare_button = QPushButton("Compare Hashes")
        self.compare_button.setFont(get_sleek_font(14))
        self.compare_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {HIGHLIGHT_PURPLE.name()};
                color: {QColor(255, 255, 255).name()};
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {QColor(150, 0, 150).name()};
            }}
        """)
        self.compare_button.clicked.connect(self.compare_hashes)
        comparison_group_layout.addWidget(self.compare_button, alignment=Qt.AlignLeft)

        self.comparison_result_label = QLabel("")
        self.comparison_result_label.setFont(get_sleek_font(14, QFont.Bold))
        self.comparison_result_label.setStyleSheet(f"color: {TEXT_COLOR_GREY.name()};")
        comparison_group_layout.addWidget(self.comparison_result_label, alignment=Qt.AlignLeft)

        main_layout.addLayout(comparison_group_layout)
        main_layout.addStretch()

        self.hash_calculated.connect(self.handle_hash_calculated)
        self.error_occurred.connect(self.handle_error)

    def browse_file(self):
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, "Select File to Hash")
        if file_path:
            self.file_path_input.setText(file_path)
            self.hash_results_text.clear() # Clear previous results
            self.comparison_result_label.clear() # Clear previous comparison result

    def _calculate_hash_in_thread(self, file_path, algorithm):
        hasher = None
        if algorithm == "MD5":
            hasher = hashlib.md5()
        elif algorithm == "SHA1":
            hasher = hashlib.sha1()
        elif algorithm == "SHA256":
            hasher = hashlib.sha256()
        elif algorithm == "SHA512":
            hasher = hashlib.sha512()
        else:
            self.error_occurred.emit("Invalid hashing algorithm selected.")
            return

        try:
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(8192) # Read in 8KB chunks
                    if not chunk:
                        break
                    hasher.update(chunk)
            self.hash_calculated.emit(algorithm, hasher.hexdigest())
        except FileNotFoundError:
            self.error_occurred.emit(f"Error: File not found at '{file_path}'")
        except Exception as e:
            self.error_occurred.emit(f"An error occurred during hashing: {e}")

    def start_hash_calculation(self):
        file_path = self.file_path_input.text().strip()
        algorithm = self.algorithm_combo.currentText()

        if not file_path:
            QMessageBox.warning(self, "Input Error", "Please select a file first.")
            return
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "File Not Found", "The specified file does not exist. Please check the path.")
            return

        self.hash_results_text.clear()
        self.comparison_result_label.clear()
        self.calculate_button.setEnabled(False)
        self.hash_results_text.append(f"Calculating {algorithm} hash for '{os.path.basename(file_path)}'...")

        self.hash_thread = threading.Thread(target=self._calculate_hash_in_thread, args=(file_path, algorithm))
        self.hash_thread.daemon = True
        self.hash_thread.start()

    def handle_hash_calculated(self, algorithm, hash_value):
        self.hash_results_text.setText(f"{algorithm} Hash:\n{hash_value}")
        self.calculate_button.setEnabled(True)

    def handle_error(self, error_message):
        QMessageBox.critical(self, "Hashing Error", error_message)
        self.hash_results_text.setText(f"Error: {error_message}")
        self.calculate_button.setEnabled(True)

    def compare_hashes(self):
        calculated_hash_text = self.hash_results_text.toPlainText()
        if not calculated_hash_text:
            QMessageBox.warning(self, "No Calculated Hash", "Please calculate a file hash first.")
            return
        
        # Extract only the hash value part
        calculated_hash = calculated_hash_text.split('\n')
        if len(calculated_hash) < 2:
            QMessageBox.warning(self, "Invalid Calculated Hash Format", "Could not extract calculated hash.")
            self.comparison_result_label.setText("<span style='color: red;'>Error in format!</span>")
            return
        calculated_hash_value = calculated_hash[1].strip()

        expected_hash = self.expected_hash_input.text().strip()

        if not expected_hash:
            QMessageBox.warning(self, "Missing Expected Hash", "Please enter an expected hash to compare against.")
            return

        if calculated_hash_value.lower() == expected_hash.lower(): # Case-insensitive comparison
            self.comparison_result_label.setText("<span style='color: green; font-weight: bold;'>HASH MATCH!</span>")
        else:
            self.comparison_result_label.setText("<span style='color: red; font-weight: bold;'>HASH MISMATCH!</span>")


class EncryptionDecryptionPage(QWidget):
    operation_finished = Signal(str, str) # (status: "success"/"error", message)
    
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        main_layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)

        title_label = QLabel("Encryption & Decryption (AES-256 GCM)")
        title_label.setFont(get_sleek_font(30))
        title_label.setStyleSheet(f"color: {HIGHLIGHT_PURPLE.name()};")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # --- IMPORTANT SECURITY DISCLAIMER ---
        self.security_warning_label = QLabel(
            "<p style='color: red; font-weight: bold;'>WARNING: This is a DEMO of encryption principles. For production use, always consult professional cryptographic advice and libraries. The security of this implementation relies entirely on the strength of your passphrase and the secure handling of files. Loss of passphrase means irreversible data loss. This app does NOT store passphrases.</p>"
        )
        self.security_warning_label.setFont(get_sleek_font(10, QFont.Bold))
        self.security_warning_label.setAlignment(Qt.AlignCenter)
        self.security_warning_label.setWordWrap(True)
        main_layout.addWidget(self.security_warning_label)
        # --- END DISCLAIMER ---

        # Passphrase Input
        passphrase_layout = QHBoxLayout()
        passphrase_label = QLabel("Passphrase:")
        passphrase_label.setFont(get_sleek_font(14, QFont.Normal))
        passphrase_label.setStyleSheet(f"color: {TEXT_COLOR_GREY.name()};")
        passphrase_layout.addWidget(passphrase_label)
        self.passphrase_input = QLineEdit()
        self.passphrase_input.setEchoMode(QLineEdit.Password)
        self.passphrase_input.setFont(get_sleek_font(12, QFont.Normal))
        self.passphrase_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {LIGHTER_GREY.name()};
                color: {TEXT_COLOR_GREY.name()};
                border: 1px solid {QColor(90, 90, 90).name()};
                padding: 5px;
            }}
        """)
        passphrase_layout.addWidget(self.passphrase_input)
        self.toggle_passphrase_visibility_button = QPushButton("Show")
        self.toggle_passphrase_visibility_button.setCheckable(True)
        self.toggle_passphrase_visibility_button.clicked.connect(self.toggle_passphrase_visibility)
        self.toggle_passphrase_visibility_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {QColor(90, 90, 90).name()};
                color: {QColor(255, 255, 255).name()};
                border: none;
                padding: 5px 10px;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {QColor(110, 110, 110).name()};
            }}
            QPushButton:checked {{
                background-color: {HIGHLIGHT_PURPLE.name()};
            }}
        """)
        passphrase_layout.addWidget(self.toggle_passphrase_visibility_button)
        main_layout.addLayout(passphrase_layout)

        # Mode Selection (Text/File)
        mode_group_layout = QHBoxLayout()
        mode_group_label = QLabel("Operation Mode:")
        mode_group_label.setFont(get_sleek_font(14, QFont.Normal))
        mode_group_label.setStyleSheet(f"color: {TEXT_COLOR_GREY.name()};")
        mode_group_layout.addWidget(mode_group_label)

        self.mode_group = QButtonGroup(self)
        self.radio_text = QRadioButton("Text")
        self.radio_file = QRadioButton("File")
        self.radio_text.setChecked(True) # Default to text mode

        radio_style = f"color: {TEXT_COLOR_GREY.name()};"
        self.radio_text.setStyleSheet(radio_style)
        self.radio_file.setStyleSheet(radio_style)

        self.mode_group.addButton(self.radio_text)
        self.mode_group.addButton(self.radio_file)
        
        mode_group_layout.addWidget(self.radio_text)
        mode_group_layout.addWidget(self.radio_file)
        mode_group_layout.addStretch() # Push radios to left
        main_layout.addLayout(mode_group_layout)

        self.radio_text.toggled.connect(self.toggle_mode_sections)
        self.radio_file.toggled.connect(self.toggle_mode_sections)

        # --- Text Operations Section ---
        self.text_section_widget = QWidget()
        text_section_layout = QVBoxLayout(self.text_section_widget)
        text_section_layout.setContentsMargins(0, 0, 0, 0)
        text_section_layout.setSpacing(10)

        text_label = QLabel("Input / Output Text:")
        text_label.setFont(get_sleek_font(14, QFont.Normal))
        text_label.setStyleSheet(f"color: {TEXT_COLOR_GREY.name()};")
        text_section_layout.addWidget(text_label)

        self.text_input_output = QTextEdit()
        self.text_input_output.setFont(get_sleek_font(10, QFont.Normal))
        self.text_input_output.setPlaceholderText("Enter text to encrypt/decrypt here or paste encrypted text...")
        self.text_input_output.setStyleSheet(f"""
            QTextEdit {{
                background-color: {LIGHTER_GREY.name()};
                color: {TEXT_COLOR_GREY.name()};
                border: 1px solid {QColor(90, 90, 90).name()};
                padding: 10px;
            }}
        """)
        text_section_layout.addWidget(self.text_input_output)

        text_buttons_layout = QHBoxLayout()
        self.encrypt_text_button = QPushButton("Encrypt Text")
        self.decrypt_text_button = QPushButton("Decrypt Text")
        
        button_style = f"""
            QPushButton {{
                background-color: {HIGHLIGHT_PURPLE.name()};
                color: {QColor(255, 255, 255).name()};
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {QColor(150, 0, 150).name()};
            }}
        """
        self.encrypt_text_button.setStyleSheet(button_style)
        self.decrypt_text_button.setStyleSheet(button_style)
        
        self.encrypt_text_button.clicked.connect(self.start_text_encryption)
        self.decrypt_text_button.clicked.connect(self.start_text_decryption)

        text_buttons_layout.addWidget(self.encrypt_text_button)
        text_buttons_layout.addWidget(self.decrypt_text_button)
        text_buttons_layout.addStretch()
        text_section_layout.addLayout(text_buttons_layout)
        main_layout.addWidget(self.text_section_widget)

        # --- File Operations Section ---
        self.file_section_widget = QWidget()
        file_section_layout = QVBoxLayout(self.file_section_widget)
        file_section_layout.setContentsMargins(0, 0, 0, 0)
        file_section_layout.setSpacing(10)
        self.file_section_widget.hide() # Hidden by default

        # Input File
        input_file_layout = QHBoxLayout()
        input_file_label = QLabel("Input File:")
        input_file_label.setFont(get_sleek_font(14, QFont.Normal))
        input_file_label.setStyleSheet(f"color: {TEXT_COLOR_GREY.name()};")
        input_file_layout.addWidget(input_file_label)
        self.input_file_path = QLineEdit()
        self.input_file_path.setFont(get_sleek_font(12, QFont.Normal))
        self.input_file_path.setPlaceholderText("Select file to encrypt/decrypt...")
        self.input_file_path.setStyleSheet(f"""
            QLineEdit {{
                background-color: {LIGHTER_GREY.name()};
                color: {TEXT_COLOR_GREY.name()};
                border: 1px solid {QColor(90, 90, 90).name()};
                padding: 5px;
            }}
        """)
        input_file_layout.addWidget(self.input_file_path)
        self.browse_input_file_button = QPushButton("Browse")
        self.browse_input_file_button.clicked.connect(self.browse_input_file)
        self.browse_input_file_button.setFont(get_sleek_font(12))
        self.browse_input_file_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {QColor(90, 90, 90).name()};
                color: {QColor(255, 255, 255).name()};
                border: none;
                padding: 5px 10px;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {QColor(110, 110, 110).name()};
            }}
        """)
        input_file_layout.addWidget(self.browse_input_file_button)
        file_section_layout.addLayout(input_file_layout)

        # Output File
        output_file_layout = QHBoxLayout()
        output_file_label = QLabel("Output File:")
        output_file_label.setFont(get_sleek_font(14, QFont.Normal))
        output_file_label.setStyleSheet(f"color: {TEXT_COLOR_GREY.name()};")
        output_file_layout.addWidget(output_file_label)
        self.output_file_path = QLineEdit()
        self.output_file_path.setFont(get_sleek_font(12, QFont.Normal))
        self.output_file_path.setPlaceholderText("Select where to save encrypted/decrypted file...")
        self.output_file_path.setStyleSheet(f"""
            QLineEdit {{
                background-color: {LIGHTER_GREY.name()};
                color: {TEXT_COLOR_GREY.name()};
                border: 1px solid {QColor(90, 90, 90).name()};
                padding: 5px;
            }}
        """)
        output_file_layout.addWidget(self.output_file_path)
        self.browse_output_file_button = QPushButton("Save As")
        self.browse_output_file_button.clicked.connect(self.browse_output_file)
        self.browse_output_file_button.setFont(get_sleek_font(12))
        self.browse_output_file_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {QColor(90, 90, 90).name()};
                color: {QColor(255, 255, 255).name()};
                border: none;
                padding: 5px 10px;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {QColor(110, 110, 110).name()};
            }}
        """)
        output_file_layout.addWidget(self.browse_output_file_button)
        file_section_layout.addLayout(output_file_layout)

        file_buttons_layout = QHBoxLayout()
        self.encrypt_file_button = QPushButton("Encrypt File")
        self.decrypt_file_button = QPushButton("Decrypt File")
        
        self.encrypt_file_button.setStyleSheet(button_style)
        self.decrypt_file_button.setStyleSheet(button_style)
        
        self.encrypt_file_button.clicked.connect(self.start_file_encryption)
        self.decrypt_file_button.clicked.connect(self.start_file_decryption)

        file_buttons_layout.addWidget(self.encrypt_file_button)
        file_buttons_layout.addWidget(self.decrypt_file_button)
        file_buttons_layout.addStretch()
        file_section_layout.addLayout(file_buttons_layout)
        main_layout.addWidget(self.file_section_widget)

        # Status/Log Display
        status_label = QLabel("Status / Logs:")
        status_label.setFont(get_sleek_font(14, QFont.Normal))
        status_label.setStyleSheet(f"color: {TEXT_COLOR_GREY.name()};")
        main_layout.addWidget(status_label)

        self.status_text_edit = QTextEdit()
        self.status_text_edit.setFont(get_sleek_font(10, QFont.Normal))
        self.status_text_edit.setReadOnly(True)
        self.status_text_edit.setStyleSheet(f"""
            QTextEdit {{
                background-color: {LIGHTER_GREY.name()};
                color: {TEXT_COLOR_GREY.name()};
                border: 1px solid {QColor(90, 90, 90).name()};
                padding: 10px;
            }}
        """)
        main_layout.addWidget(self.status_text_edit)
        main_layout.addStretch()

        self.operation_finished.connect(self.handle_operation_finished)

    def toggle_passphrase_visibility(self):
        if self.toggle_passphrase_visibility_button.isChecked():
            self.passphrase_input.setEchoMode(QLineEdit.Normal)
            self.toggle_passphrase_visibility_button.setText("Hide")
        else:
            self.passphrase_input.setEchoMode(QLineEdit.Password)
            self.toggle_passphrase_visibility_button.setText("Show")

    def toggle_mode_sections(self):
        is_text_mode = self.radio_text.isChecked()
        self.text_section_widget.setVisible(is_text_mode)
        self.file_section_widget.setVisible(not is_text_mode)
        self.status_text_edit.clear() # Clear status when mode changes

    def _derive_key(self, passphrase: str, salt: bytes) -> bytes:
        """Derives a 256-bit (32-byte) AES key from a passphrase and salt using PBKDF2."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32, # 256-bit key
            salt=salt,
            iterations=100000, # Recommended iteration count for PBKDF2
            backend=default_backend()
        )
        return kdf.derive(passphrase.encode())

    def _encrypt_bytes(self, data: bytes, passphrase: str) -> bytes:
        """Encrypts bytes using AES-256 GCM."""
        if not passphrase:
            raise ValueError("Passphrase cannot be empty.")

        salt = os.urandom(16) # 128-bit salt
        key = self._derive_key(passphrase, salt)
        
        # GCM recommends a 96-bit (12-byte) nonce
        nonce = os.urandom(12) 

        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce), backend=default_backend())
        encryptor = cipher.encryptor()
        
        ciphertext = encryptor.update(data) + encryptor.finalize()
        tag = encryptor.tag

        # Prepend salt, nonce, and tag to the ciphertext for storage/transmission
        return salt + nonce + tag + ciphertext

    def _decrypt_bytes(self, encrypted_data: bytes, passphrase: str) -> bytes:
        """Decrypts bytes using AES-256 GCM."""
        if not passphrase:
            raise ValueError("Passphrase cannot be empty.")
        if len(encrypted_data) < 16 + 12 + 16: # Salt (16) + Nonce (12) + Tag (16)
            raise ValueError("Encrypted data is too short or malformed.")

        salt = encrypted_data[:16]
        nonce = encrypted_data[16:16+12]
        tag = encrypted_data[16+12:16+12+16]
        ciphertext = encrypted_data[16+12+16:]

        key = self._derive_key(passphrase, salt)

        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag), backend=default_backend())
        decryptor = cipher.decryptor()

        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        return plaintext

    def _run_text_encryption(self, text_to_encrypt, passphrase):
        self.status_text_edit.append("Attempting text encryption...")
        try:
            encrypted_data = self._encrypt_bytes(text_to_encrypt.encode('utf-8'), passphrase)
            # Encode to base64 for safe display/storage as text
            encoded_encrypted_data = base64.b64encode(encrypted_data).decode('utf-8')
            self.operation_finished.emit("success", encoded_encrypted_data)
        except ValueError as e:
            self.operation_finished.emit("error", f"Encryption failed: {e}")
        except Exception as e:
            self.operation_finished.emit("error", f"An unexpected error occurred during encryption: {e}")

    def _run_text_decryption(self, text_to_decrypt_b64, passphrase):
        self.status_text_edit.append("Attempting text decryption...")
        try:
            # Decode from base64 first
            encrypted_data = base64.b64decode(text_to_decrypt_b64)
            decrypted_bytes = self._decrypt_bytes(encrypted_data, passphrase)
            decrypted_text = decrypted_bytes.decode('utf-8')
            self.operation_finished.emit("success", decrypted_text)
        except InvalidTag:
            self.operation_finished.emit("error", "Decryption failed: Invalid passphrase or corrupted data. (InvalidTag)")
        except ValueError as e:
            self.operation_finished.emit("error", f"Decryption failed: {e}. Data may be malformed.")
        except Exception as e:
            self.operation_finished.emit("error", f"An unexpected error occurred during decryption: {e}")

    def start_text_encryption(self):
        text = self.text_input_output.toPlainText()
        passphrase = self.passphrase_input.text()

        if not text:
            QMessageBox.warning(self, "Input Error", "Please enter text to encrypt.")
            return
        if not passphrase:
            QMessageBox.warning(self, "Input Error", "Please enter a passphrase.")
            return
        
        self.set_buttons_enabled(False)
        self.status_text_edit.clear()
        
        threading.Thread(target=self._run_text_encryption, args=(text, passphrase)).start()

    def start_text_decryption(self):
        text_b64 = self.text_input_output.toPlainText()
        passphrase = self.passphrase_input.text()

        if not text_b64:
            QMessageBox.warning(self, "Input Error", "Please enter encrypted text to decrypt.")
            return
        if not passphrase:
            QMessageBox.warning(self, "Input Error", "Please enter a passphrase.")
            return

        self.set_buttons_enabled(False)
        self.status_text_edit.clear()

        threading.Thread(target=self._run_text_decryption, args=(text_b64, passphrase)).start()

    def browse_input_file(self):
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, "Select Input File")
        if file_path:
            self.input_file_path.setText(file_path)

    def browse_output_file(self):
        file_dialog = QFileDialog(self)
        # Suggest a default name, e.g., adding .enc or .dec
        input_file = self.input_file_path.text()
        default_name = ""
        if input_file:
            base, ext = os.path.splitext(input_file)
            if ext.lower() == ".enc":
                default_name = base + ".dec" # Suggest .dec for encrypted files
            else:
                default_name = input_file + ".enc" # Suggest .enc for unencrypted files
        
        save_path, _ = file_dialog.getSaveFileName(self, "Save Output File As", default_name)
        if save_path:
            self.output_file_path.setText(save_path)

    def _run_file_encryption(self, input_file, output_file, passphrase):
        self.status_text_edit.append(f"Attempting file encryption: '{os.path.basename(input_file)}' to '{os.path.basename(output_file)}'...")
        try:
            if not passphrase:
                self.operation_finished.emit("error", "Passphrase cannot be empty.")
                return

            salt = os.urandom(16)
            key = self._derive_key(passphrase, salt)
            nonce = os.urandom(12)

            cipher = Cipher(algorithms.AES(key), modes.GCM(nonce), backend=default_backend())
            encryptor = cipher.encryptor()

            with open(input_file, 'rb') as infile, open(output_file, 'wb') as outfile:
                outfile.write(salt)
                outfile.write(nonce)
                # Placeholder for tag, will write later
                outfile.write(b'\0' * 16) # Reserve 16 bytes for the tag

                while True:
                    chunk = infile.read(8192) # Read in 8KB chunks
                    if not chunk:
                        break
                    encrypted_chunk = encryptor.update(chunk)
                    outfile.write(encrypted_chunk)
                
                final_encrypted_data = encryptor.finalize()
                tag = encryptor.tag
                outfile.write(final_encrypted_data) # Write any remaining encrypted data

                # Go back and write the tag
                outfile.seek(16 + 12) # Position after salt and nonce
                outfile.write(tag)

            self.operation_finished.emit("success", f"File '{os.path.basename(input_file)}' encrypted successfully to '{os.path.basename(output_file)}'.")
        except FileNotFoundError:
            self.operation_finished.emit("error", f"Error: File not found. Input: '{input_file}', Output: '{output_file}'")
        except Exception as e:
            self.operation_finished.emit("error", f"An unexpected error occurred during file encryption: {e}")

    def _run_file_decryption(self, input_file, output_file, passphrase):
        self.status_text_edit.append(f"Attempting file decryption: '{os.path.basename(input_file)}' to '{os.path.basename(output_file)}'...")
        try:
            if not passphrase:
                self.operation_finished.emit("error", "Passphrase cannot be empty.")
                return

            with open(input_file, 'rb') as infile, open(output_file, 'wb') as outfile:
                header = infile.read(16 + 12 + 16) # Salt (16) + Nonce (12) + Tag (16)
                if len(header) < 16 + 12 + 16:
                    raise ValueError("Input file is too short or malformed. Not a valid encrypted file.")

                salt = header[:16]
                nonce = header[16:16+12]
                tag = header[16+12:16+12+16]

                key = self._derive_key(passphrase, salt)
                cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag), backend=default_backend())
                decryptor = cipher.decryptor()

                while True:
                    chunk = infile.read(8192)
                    if not chunk:
                        break
                    decrypted_chunk = decryptor.update(chunk)
                    outfile.write(decrypted_chunk)
                
                decryptor.finalize() # This will raise InvalidTag if decryption fails

            self.operation_finished.emit("success", f"File '{os.path.basename(input_file)}' decrypted successfully to '{os.path.basename(output_file)}'.")

        except InvalidTag:
            self.operation_finished.emit("error", "Decryption failed: Invalid passphrase or corrupted file. (Authentication Tag Mismatch)")
        except FileNotFoundError:
            self.operation_finished.emit("error", f"Error: File not found. Input: '{input_file}', Output: '{output_file}'")
        except ValueError as e:
            self.operation_finished.emit("error", f"Decryption failed: {e}")
        except Exception as e:
            self.operation_finished.emit("error", f"An unexpected error occurred during file decryption: {e}")

    def start_file_encryption(self):
        input_path = self.input_file_path.text().strip()
        output_path = self.output_file_path.text().strip()
        passphrase = self.passphrase_input.text()

        if not input_path or not output_path:
            QMessageBox.warning(self, "Input Error", "Please select both input and output files.")
            return
        if not os.path.exists(input_path):
            QMessageBox.warning(self, "File Not Found", "Input file does not exist. Please check the path.")
            return
        if not passphrase:
            QMessageBox.warning(self, "Input Error", "Please enter a passphrase.")
            return

        self.set_buttons_enabled(False)
        self.status_text_edit.clear()

        threading.Thread(target=self._run_file_encryption, args=(input_path, output_path, passphrase)).start()

    def start_file_decryption(self):
        input_path = self.input_file_path.text().strip()
        output_path = self.output_file_path.text().strip()
        passphrase = self.passphrase_input.text()

        if not input_path or not output_path:
            QMessageBox.warning(self, "Input Error", "Please select both input and output files.")
            return
        if not os.path.exists(input_path):
            QMessageBox.warning(self, "File Not Found", "Input file does not exist. Please check the path.")
            return
        if not passphrase:
            QMessageBox.warning(self, "Input Error", "Please enter a passphrase.")
            return

        self.set_buttons_enabled(False)
        self.status_text_edit.clear()

        threading.Thread(target=self._run_file_decryption, args=(input_path, output_path, passphrase)).start()


    def set_buttons_enabled(self, enabled: bool):
        self.encrypt_text_button.setEnabled(enabled)
        self.decrypt_text_button.setEnabled(enabled)
        self.encrypt_file_button.setEnabled(enabled)
        self.decrypt_file_button.setEnabled(enabled)
        self.browse_input_file_button.setEnabled(enabled)
        self.browse_output_file_button.setEnabled(enabled)
        self.passphrase_input.setEnabled(enabled)
        self.radio_text.setEnabled(enabled)
        self.radio_file.setEnabled(enabled)


    def handle_operation_finished(self, status: str, message: str):
        if status == "success":
            self.status_text_edit.append(f"<span style='color: green;'>SUCCESS: {message}</span>")
            # If text encryption was successful, display the encrypted text
            if self.radio_text.isChecked() and self.text_input_output.toPlainText() == message:
                pass # Already set by the signal, no need to overwrite if it's the encrypted output
            elif self.radio_text.isChecked() and status == "success" and self.text_input_output.toPlainText() != message:
                self.text_input_output.setText(message) # For decryption, show decrypted text
        else: # status == "error"
            self.status_text_edit.append(f"<span style='color: red;'>ERROR: {message}</span>")
        
        self.set_buttons_enabled(True)
        self.status_text_edit.verticalScrollBar().setValue(self.status_text_edit.verticalScrollBar().maximum())



class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("B.U.D.D.Ysuite - Main Application")
        
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint) 
        self.showMaximized() 

        palette = self.palette()
        palette.setColor(QPalette.Window, MAIN_BG_GREY) 
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        self.main_app_layout = QHBoxLayout(self) 
        self.main_app_layout.setContentsMargins(0, 0, 0, 0)
        self.main_app_layout.setSpacing(0) 

        self.hamburger_button = QPushButton("☰")
        self.hamburger_button.setFixedSize(40, 40) 
        self.hamburger_button.setFont(get_sleek_font(20))
        self.hamburger_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {MAIN_BG_GREY.name()}; 
                color: {HIGHLIGHT_PURPLE.name()};
                border: none;
                padding: 5px;
            }}
            QPushButton:hover {{
                background-color: {QColor(60, 60, 60).name()}; 
            }}
        """)
        self.hamburger_button.clicked.connect(self.toggle_sidebar)

        hamburger_container = QWidget()
        hamburger_container_layout = QVBoxLayout(hamburger_container)
        hamburger_container_layout.setContentsMargins(0, 0, 0, 0)
        hamburger_container_layout.setSpacing(0)
        hamburger_container_layout.addWidget(self.hamburger_button, alignment=Qt.AlignTop | Qt.AlignLeft)
        hamburger_container_layout.addStretch() 
        
        self.main_app_layout.addWidget(hamburger_container) 

        self.sidebar_widget = QWidget()
        sidebar_palette = self.sidebar_widget.palette()
        sidebar_palette.setColor(QPalette.Window, SIDEBAR_BG_GREY) 
        self.sidebar_widget.setPalette(sidebar_palette)
        self.sidebar_widget.setAutoFillBackground(True)
        self.sidebar_widget.setMinimumWidth(0) 
        self.sidebar_widget.setMaximumWidth(0) 
        self.sidebar_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding) 
        
        self.sidebar_layout = QVBoxLayout(self.sidebar_widget)
        self.sidebar_layout.setContentsMargins(10, 50, 10, 10) 
        self.sidebar_layout.setSpacing(5)

        self.feature_list = QListWidget()
        self.feature_list.setFont(get_sleek_font(14))
        self.feature_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {SIDEBAR_BG_GREY.name()};
                border: none;
                outline: none; 
                color: {TEXT_COLOR_GREY.name()};
            }}
            QListWidget::item {{
                padding: 10px 15px;
            }}
            QListWidget::item:selected {{
                background-color: {HIGHLIGHT_PURPLE.name()};
                color: {QColor(255, 255, 255).name()}; 
            }}
            QListWidget::item:hover:!selected {{
                background-color: {QColor(70, 70, 70).name()}; 
            }}
        """)
        
        features = [
            "Data Management", 
            "Passive & Active Recon Tools",
            "  - Network Scanners", 
            "  - OSINT Data Fetchers",
            "  - Passive Monitoring Tools", 
            "Security Utilities",
            "  - Password Managers", 
            "  - File Hashing", 
            "  - Encryption/Decryption", # New item for Encryption/Decryption
            "  - Alerts/Notifications",
            "Automation",
            "  - Scanning Automation",
            "  - API Integration"
        ]
        
        for feature in features:
            item = QListWidgetItem(feature)
            if not feature.startswith("  -"):
                item.setFont(get_sleek_font(15)) 
                item.setForeground(QColor(255, 255, 255)) 
            self.feature_list.addItem(item)
            
        self.feature_list.itemClicked.connect(self.switch_feature_page)
        
        self.sidebar_layout.addWidget(self.feature_list)

        self.main_app_layout.addWidget(self.sidebar_widget) 

        self.sidebar_width_animation = QPropertyAnimation(self.sidebar_widget, b"maximumWidth")
        self.sidebar_width_animation.setDuration(300) 
        self.sidebar_width_animation.setEasingCurve(QEasingCurve.InOutQuad)

        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet(f"background-color: {MAIN_BG_GREY.name()};")
        
        self.pages = {}
        self.pages["Data Management"] = DataManagementPage()

        self.pages["  - Network Scanners"] = NetworkScannersPage()
        self.pages["  - OSINT Data Fetchers"] = OsintDataFetchersPage()
        self.pages["  - Passive Monitoring Tools"] = PassiveMonitoringToolsPage()
        self.pages["  - Password Managers"] = PasswordManagersPage()
        self.pages["  - File Hashing"] = FileHashingPage()
        
        # --- New: Encryption/Decryption Page ---
        self.pages["  - Encryption/Decryption"] = EncryptionDecryptionPage()


        self.pages["Passive & Active Recon Tools"] = self.create_generic_feature_page("Passive & Active Recon Tools", "Explore network scanners, OSINT data fetchers, and passive monitoring.")
        self.pages["Security Utilities"] = self.create_generic_feature_page("Security Utilities", "Manage passwords, verify files, and encrypt data.")

        for name, page_widget in self.pages.items():
            self.content_stack.addWidget(page_widget)
            
        self.content_stack.setCurrentWidget(self.pages["Data Management"]) 

        self.main_app_layout.addWidget(self.content_stack) 

    def create_generic_feature_page(self, title, description):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        
        title_label = QLabel(title)
        title_label.setFont(get_sleek_font(30))
        title_label.setStyleSheet(f"color: {HIGHLIGHT_PURPLE.name()};") 
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        desc_label = QLabel(description)
        desc_label.setFont(get_sleek_font(16, QFont.Normal)) 
        desc_label.setStyleSheet(f"color: {TEXT_COLOR_GREY.name()};") 
        desc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc_label)
        
        layout.addStretch() 
        return page

    def toggle_sidebar(self):
        try:
            self.sidebar_width_animation.finished.disconnect()
        except TypeError:
            pass 
            
        current_width = self.sidebar_widget.width()
        target_width = 250 if current_width == 0 else 0

        self.sidebar_width_animation.setStartValue(current_width)
        self.sidebar_width_animation.setEndValue(target_width)
        
        if target_width > 0: 
            self.sidebar_widget.show()
            self.sidebar_width_animation.start()
        else: 
            self.sidebar_width_animation.finished.connect(self.sidebar_widget.hide)
            self.sidebar_width_animation.start()


    def switch_feature_page(self, item):
        feature_name = item.text()
        if feature_name in self.pages:
            self.content_stack.setCurrentWidget(self.pages[feature_name])
            if self.sidebar_widget.width() > 0: 
                 self.toggle_sidebar() 

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    default_font = QFont("Segoe UI", 9) 
    default_font.setWeight(QFont.DemiBold)
    app.setFont(default_font)

    splash = SplashScreen()
    sys.exit(app.exec())