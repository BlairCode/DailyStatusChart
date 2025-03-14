from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, 
    QGridLayout, QLabel, QLineEdit, QTextEdit,
    QHBoxLayout, QMessageBox, QScrollArea, QWidget
)
from PyQt6.QtGui import QTextOption, QGuiApplication
from PyQt6.QtCore import Qt
from utils.database import DB_PATH, get_today
from utils.constants import (
    ATTR_NAMES, ATTR_WEIGHTS, FACTOR_NAMES, RECORD_EVENT, 
    FACTOR_WEIGHTS, ATTR_DESCS, SCORES_TIP, TIP
)
from utils.title_generator import generate_title
from utils.helpers import animate_open
import sqlite3
from .base_dialog import BaseDialog
from PyQt6.QtWidgets import QApplication  # 新增：导入 QApplication

class StatusDialog(BaseDialog):
    def __init__(self, parent=None, is_change=False):
        self.is_change = is_change
        super().__init__(parent, title="Flip My Status" if is_change else "Record My Day")
        self.setMinimumSize(600, 600)
        self.current_page = 0
        self.entries = [[] for _ in ATTR_NAMES]
        self.event_entries = [None] * len(ATTR_NAMES)
        self.attr_scores = [0.0] * len(ATTR_NAMES)
        self.setup_ui()
        self.center_on_screen()  # 居中显示
        animate_open(self)

    def setup_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.content_widget_inner = QWidget()
        self.content_layout = QGridLayout(self.content_widget_inner)
        self.content_layout.setSpacing(12)

        self.content_layout.setColumnStretch(0, 2)
        self.content_layout.setColumnStretch(1, 1)
        self.content_layout.setColumnStretch(2, 2)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        scroll.setWidget(self.content_widget_inner)
        self.main_layout.addWidget(scroll)

        btn_layout = QHBoxLayout()
        self.prev_btn = QPushButton("Previous", self)
        self.prev_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, 
                                            stop:0 #FFDAB9, stop:1 #FFB6C1);
                color: #5C4033;
                font: bold 14px 'Segoe Script';
                border-radius: 20px;
                padding: 8px 16px;
                min-width: 100px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, 
                                            stop:0 #FFC107, stop:1 #FF9999);
            }
            QPushButton:pressed {
                background: #FFB6C1;
            }
            QPushButton:disabled {
                background: #E0E0E0;
                color: #A9A9A9;
            }
        """)
        self.prev_btn.clicked.connect(self.prev_page)
        btn_layout.addWidget(self.prev_btn)

        self.next_btn = QPushButton("Next", self)
        self.next_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, 
                                            stop:0 #FFDAB9, stop:1 #FFB6C1);
                color: #5C4033;
                font: bold 14px 'Segoe Script';
                border-radius: 20px;
                padding: 8px 16px;
                min-width: 100px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, 
                                            stop:0 #FFC107, stop:1 #FF9999);
            }
            QPushButton:pressed {
                background: #FFB6C1;
            }
            QPushButton:disabled {
                background: #E0E0E0;
                color: #A9A9A9;
            }
        """)
        self.next_btn.clicked.connect(self.next_page)
        btn_layout.addWidget(self.next_btn)

        self.main_layout.addLayout(btn_layout)
        self.content_widget.setLayout(self.main_layout)
        self.content_widget.setStyleSheet("background: transparent;")
        self.update_page()

    def center_on_screen(self):
        # 使用 QApplication.primaryScreen() 替代 QDesktopWidget
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        # 计算居中位置
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)

    def update_page(self):
        for i in reversed(range(self.content_layout.count())):
            item = self.content_layout.itemAt(i)
            if item and item.widget():
                item.widget().setParent(None)

        today = get_today()
        attr_idx = self.current_page
        attr = ATTR_NAMES[attr_idx]

        title_label = QLabel(attr, self)
        title_label.setStyleSheet("""
            color: #FFFFFF;
            font: bold 18px 'Segoe Script';
            background-color: #D8BFD8;
            border-radius: 10px;
            padding: 8px 16px;
            text-align: center;
        """)
        self.content_layout.addWidget(title_label, 0, 0, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)

        desc_label = QLabel(ATTR_DESCS[attr_idx], self)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("""
            color: #5C4033;
            font: 14px 'Segoe Script';
            padding: 4px;
        """)
        self.content_layout.addWidget(desc_label, 1, 0, 1, 3)

        self.entries[attr_idx].clear()
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            for j, factor in enumerate(FACTOR_NAMES[attr_idx]):
                factor_label = QLabel(factor, self)
                factor_label.setWordWrap(True)
                factor_label.setStyleSheet("""
                    color: #5C4033;
                    font: bold 14px 'Segoe Script';
                    padding: 6px 10px;
                """)
                self.content_layout.addWidget(factor_label, j + 2, 0)

                entry = QLineEdit(self)
                entry.setMinimumWidth(40)
                entry.setStyleSheet("""
                    background: #FFFFFF; 
                    color: #5C4033; 
                    border: 2px solid #D8BFD8;
                    border-radius: 8px; 
                    padding: 6px;
                    font: 12px 'Segoe Script';
                """)
                entry.setText("3")
                entry.setAlignment(Qt.AlignmentFlag.AlignCenter)
                entry.mousePressEvent = lambda event, ent=entry: self.clear_default(ent)

                if self.is_change:
                    cursor.execute("SELECT factor_score FROM factors WHERE date = ? AND attr_name = ? AND factor_name = ?", (today, attr, factor))
                    score = cursor.fetchone()
                    entry.setText(str(score[0]) if score else "3")
                
                self.content_layout.addWidget(entry, j + 2, 1)
                self.entries[attr_idx].append(entry)

            hint_widget = QWidget()
            hint_layout = QVBoxLayout(hint_widget)
            hint_layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignRight)
            hint_layout.setSpacing(5)

            hint_title = QLabel(TIP, self)
            hint_title.setStyleSheet("""
                color: #5C4033;
                font: bold 16px 'Segoe Script';
                padding: 2px;
            """)
            hint_layout.addWidget(hint_title)

            for score_text in SCORES_TIP:
                score_label = QLabel(score_text, self)
                score_label.setStyleSheet("""
                    color: #5C4033;
                    font: 10px 'Segoe Script';
                    padding: 2px;
                """)
                hint_layout.addWidget(score_label)

            self.content_layout.addWidget(hint_widget, 2, 2, 4, 1)

            event_label = QLabel(RECORD_EVENT, self)
            event_label.setStyleSheet("""
                color: #5C4033; 
                font: bold 14px 'Segoe Script';
                padding: 6px 10px;
            """)
            self.content_layout.addWidget(event_label, 6, 0)

            event_entry = QTextEdit(self)
            event_entry.setStyleSheet("""
                background: #FFFFFF; 
                color: #5C4033; 
                border: 1px solid #D8BFD8; 
                border-radius: 5px; 
                padding: 5px;
                font: 12px 'Segoe Script';
            """)
            event_entry.setFixedHeight(100)
            event_entry.setWordWrapMode(QTextOption.WrapMode.WordWrap)
            if self.is_change:
                cursor.execute("SELECT event FROM events WHERE date = ? AND attr_name = ?", (today, attr))
                event = cursor.fetchone()
                event_entry.setText(event[0] if event else "")
            
            self.content_layout.addWidget(event_entry, 6, 1, 1, 2)
            self.event_entries[attr_idx] = event_entry

        self.prev_btn.setEnabled(self.current_page > 0)
        self.next_btn.setText("Save" if self.current_page == len(ATTR_NAMES) - 1 else "Next")
        self.next_btn.clicked.disconnect()
        self.next_btn.clicked.connect(self.save_status if self.current_page == len(ATTR_NAMES) - 1 else self.next_page)

    def clear_default(self, entry):
        if entry.text() == "3":
            entry.clear()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_page()

    def next_page(self):
        self.save_current_page()
        if self.current_page < len(ATTR_NAMES) - 1:
            self.current_page += 1
            self.update_page()

    def save_current_page(self):
        today = get_today()
        attr_idx = self.current_page
        attr = ATTR_NAMES[attr_idx]
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                f_scores = [float(entry.text()) for entry in self.entries[attr_idx]]
                if not all(1 <= s <= 5 for s in f_scores):
                    raise ValueError(f"Factor scores for {attr} must be between 1 and 5!")
                attr_score = sum(f * w for f, w in zip(f_scores, FACTOR_WEIGHTS))
                self.attr_scores[attr_idx] = attr_score

                cursor.execute("INSERT OR REPLACE INTO attributes (date, attr_name, attr_score, total_score) VALUES (?, ?, ?, ?)", (today, attr, attr_score, attr_score))
                for j, factor in enumerate(FACTOR_NAMES[attr_idx]):
                    cursor.execute("INSERT OR REPLACE INTO factors (date, attr_name, factor_name, factor_score, factor_weight) VALUES (?, ?, ?, ?, ?)", (today, attr, factor, f_scores[j], FACTOR_WEIGHTS[j]))
                event_text = self.event_entries[attr_idx].toPlainText().strip()
                if event_text:
                    cursor.execute("INSERT OR REPLACE INTO events (date, attr_name, event) VALUES (?, ?, ?)", (today, attr, event_text))
                conn.commit()
        except ValueError as e:
            QMessageBox.critical(self, "Error", str(e))

    def save_status(self):
        self.save_current_page()
        today = get_today()
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                total_score = sum(s * w for s, w in zip(self.attr_scores, ATTR_WEIGHTS))
                title = generate_title(self.attr_scores, today)
                cursor.execute("INSERT OR REPLACE INTO daily_status (date, score, title) VALUES (?, ?, ?)", (today, total_score, title))
                conn.commit()
            self.accept()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to save: {e}")