# 核心控件
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QMessageBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt  # 用于布局对齐等
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from utils.database import init_database, DB_PATH, get_today
from utils.helpers import apply_gradient_background, animate_open 
from ui.status_dialog import StatusDialog
from ui.history_dialog import HistoryDialog
from ui.ranking_dialog import RankingDialog
from utils.constants import ICON_DIR
import sqlite3  # 用于数据库操作
import os

# 定义主窗口类，继承自QMainWindow
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Daily Status Chart v0.0.1")
        self.setFixedSize(400, 500)
        self.setWindowOpacity(0)  # 初始透明度为0
        init_database()
        self.init_ui()
        animate_open(self)  # 启动窗口淡入动画

    # 初始化界面UI
    def init_ui(self): 
        widget = QWidget(self)
        self.setCentralWidget(widget)
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(25)

        buttons = [
            ("📅 Record My Day", self.input_status),
            ("🔄 Flip My Status", self.change_status),
            ("🏆 View Ranking", self.view_ranking),
            ("🗒️ Explore My Diary", self.view_history),
            ("❌ Exit, Bye-Bye!", self.close)
        ]

        for text, cmd in buttons:
            btn = QPushButton(text, self)
            btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, 
                                                stop:0 #FFDAB9, stop:1 #FFB6C1); /* 浅桃色到淡粉渐变 */
                    color: #5C4033;  /* 深棕色文字 */
                    font: bold 15px 'Segoe Script';  /* 手写风格字体 */
                    border-radius: 35px;  /* 圆角更明显 */
                    padding: 14px 30px;
                    min-width: 200px;
                    border: 2px solid #D8BFD8; /* 淡紫色边框 */
                }

                QPushButton:hover {
                    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, 
                                                stop:0 #FBC2EB, stop:1 #FF9999); /* 更粉嫩的渐变 */
                    border: 2px solid #DDA0DD; /* 加深边框，增加立体感 */
                }

                QPushButton:pressed {
                    background: #FFB6C1; /* 柔和的深粉色 */
                    border: 2px solid #D8BFD8;
                    color: #5C4033; /* 按下时保持深棕色 */
                }
            """)

            btn.setGraphicsEffect(QGraphicsDropShadowEffect(btn))  # 加阴影
            btn.clicked.connect(lambda checked, b=btn: animate_button(b))  # 动画
            btn.clicked.connect(cmd)
            layout.addWidget(btn)

        apply_gradient_background(self)  # 应用渐变背景（与 StatusDialog 一致）

    def input_status(self):
        dialog = StatusDialog(self)
        dialog.exec()

    def change_status(self):
        today = get_today()  # 获取当前日期

        # 连接数据库
        with sqlite3.connect(DB_PATH) as conn:
            # 创建游标（光标），执行SQL查询工作
            cursor = conn.cursor()
            # 查询今日是否有记录
            cursor.execute("SELECT score FROM daily_status WHERE date = ?", (today,))
            if not cursor.fetchone():
                QMessageBox.critical(self, "Error", f"No status recorded for {today}!")
            else:
                dialog = StatusDialog(self, is_change=True)
                dialog.exec()

    def view_ranking(self):
        dialog = RankingDialog(self)
        dialog.exec()

    def view_history(self):
        dialog = HistoryDialog(self)
        dialog.exec()

def animate_button(btn):
    animation = QPropertyAnimation(btn, b"geometry")
    animation.setDuration(150)  # 动画时间
    animation.setStartValue(btn.geometry())
    animation.setEndValue(btn.geometry().adjusted(0, -2, 0, -2))  # 轻微上浮
    animation.setEasingCurve(QEasingCurve.Type.OutQuad)  # 平滑动画
    animation.start()
    btn.clicked.connect(lambda: animate_button(btn))