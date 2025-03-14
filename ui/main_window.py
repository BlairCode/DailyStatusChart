# 文件：main_window.py
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QMessageBox, QHBoxLayout, QLabel
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from utils.database import init_database, DB_PATH, get_today
from utils.helpers import apply_gradient_background, animate_open 
from ui.status_dialog import StatusDialog
from ui.history_dialog import HistoryDialog
from ui.ranking_dialog import RankingDialog
from utils.constants import ICON_DIR
import sqlite3
import os
from .base_window import BaseWindow, animate_button

# 定义主窗口类
class MainWindow(BaseWindow):
    def __init__(self):
        super().__init__(title="Daily Status Chart v0.0.2")  # 设置窗口标题
        init_database()
        self.setup_ui()  # 设置内容区域
        animate_open(self)  # 启动淡入动画

    def setup_ui(self):
        buttons = [
            ("📅 Record My Day", self.input_status),
            ("🔄 Flip My Status", self.change_status),
            ("🏆 View Ranking", self.view_ranking),
            ("🗒️ Explore My Diary", self.view_history),
            ("❌ Exit, Bye-Bye!", self.close)
        ]

        for text, cmd in buttons:
            btn = QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, 
                                                stop:0 #FFDAB9, stop:1 #FFB6C1);
                    color: #5C4033;
                    font: bold 15px 'Segoe Script';
                    border-radius: 35px;
                    padding: 14px 30px;
                    min-width: 200px;
                    border: 2px solid #D8BFD8;
                }
                QPushButton:hover {
                    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, 
                                                stop:0 #FBC2EB, stop:1 #FF9999);
                    border: 2px solid #DDA0DD;
                }
                QPushButton:pressed {
                    background: #FFB6C1;
                    border: 2px solid #D8BFD8;
                    color: #5C4033;
                }
            """)
            btn.setGraphicsEffect(QGraphicsDropShadowEffect(btn))
            btn.clicked.connect(lambda checked, b=btn: animate_button(b))
            btn.clicked.connect(cmd)
            self.content_layout.addWidget(btn)  # 添加到基类的 content_layout

    def input_status(self):
        # 修改：移除 self 作为 parent，使弹窗独立
        dialog = StatusDialog(parent=None)
        dialog.exec()

    def change_status(self):
        today = get_today()  # 获取当前日期
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT score FROM daily_status WHERE date = ?", (today,))
            if not cursor.fetchone():
                QMessageBox.critical(self, "Error", f"No status recorded for {today}!")
            else:
                dialog = StatusDialog(parent=None, is_change=True)
                dialog.exec()

    def view_ranking(self):
        dialog = RankingDialog(parent=None)
        dialog.exec()

    def view_history(self):
        dialog = HistoryDialog(parent=None)
        dialog.exec()

    # 全屏/最大化切换函数
    def toggle_max_full(self):
        if self.isFullScreen():
            self.setMinimumSize(400, 500)  # 恢复最小尺寸
            self.showNormal()  # 从全屏恢复正常状态
            self.is_fullscreen = False
        else:
            self.showFullScreen()  # 切换到全屏模式
            self.is_fullscreen = True
        self.update_button_sizes()  # 更新按钮大小

    # 动态调整标题栏按钮大小
    def update_button_sizes(self):
        if self.is_fullscreen:
            size = 40, 30  # 全屏时按钮更大
            font_size = 16  # 字体更大
        else:
            size = 30, 20  # 正常状态下按钮大小
            font_size = 12  # 正常字体大小
        for btn in (self.min_button, self.max_full_button, self.close_button):
            btn.setFixedSize(*size)  # 动态调整按钮大小
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: #FFDAB9;
                    color: #5C4033;
                    border: none;
                    padding: 2px 8px;
                    font-size: {font_size}px;
                }}
                QPushButton:hover {{
                    background: #FF9999;
                }}
            """)  # 动态调整按钮样式和字体大小
        # 调整标题栏高度和字体
        self.title_bar_widget.setFixedHeight(size[1] + 10)  # 标题栏高度随按钮调整
        self.title_label.setStyleSheet(f"""
            color: #5C4033;
            font: bold {font_size}px 'Segoe Script';
            padding: 2px 5px;
        """)  # 动态调整软件名字体大小

    # 添加鼠标事件以实现拖动窗口
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

def animate_button(btn):
    animation = QPropertyAnimation(btn, b"geometry")
    animation.setDuration(150)  # 动画时间
    animation.setStartValue(btn.geometry())
    animation.setEndValue(btn.geometry().adjusted(0, -2, 0, -2))  # 轻微上浮
    animation.setEasingCurve(QEasingCurve.Type.OutQuad)  # 平滑动画
    animation.start()
    btn.clicked.connect(lambda: animate_button(btn))