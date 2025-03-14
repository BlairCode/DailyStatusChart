# 文件：E:\Coding\DailyStatusChart\src\python\ui\history_dialog.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QScrollArea, QWidget, QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor, QGuiApplication
from utils.database import DB_PATH
from utils.helpers import apply_gradient_background, animate_open
import sqlite3
from .base_dialog import BaseDialog  # 继承 BaseDialog

class HistoryDialog(BaseDialog):
    def __init__(self, parent=None):
        # 调用 BaseDialog 的构造函数，传递标题
        super().__init__(parent, title="My Diary History")
        self.setMinimumSize(700, 500)  # 替换 setFixedSize，支持全屏
        self.setWindowOpacity(0)
        self.init_ui()
        self.center_on_screen()  # 居中显示
        animate_open(self)

    def init_ui(self):
        # 首先调用基类的 init_ui，确保 content_widget 和 main_layout 初始化
        super().init_ui()
        
        # 显式初始化 content_layout
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(10, 10, 10, 10)  # 调整边距以适配标题栏

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: rgba(255, 255, 255, 0.1);
                width: 8px;
                margin: 0 0 0 0;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #FFDAB9, stop:1 #FF9999);  /* 浅桃色到樱花粉 */
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
            }
        """)
        print("ScrollArea stylesheet applied")  # 调试信息
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(10)
        content_layout.setContentsMargins(20, 20, 20, 20)

        # 背景样式（日记风格，柔和粉色调）
        # BaseDialog 已设置背景样式，这里注释掉以避免冲突
        # self.setStyleSheet("""
        #     QDialog {
        #         background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
        #                                     stop:0 #FFF8E1, stop:1 #FCE4EC);
        #     }
        # """)
        content.setStyleSheet("""
            QWidget {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                border: 1px solid #FFDAB9;  /* 浅桃色 */
            }
        """)
        print("Content stylesheet applied")  # 调试信息

        # 从数据库加载历史记录
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT date, score, title FROM daily_status ORDER BY date ASC")
            rows = cursor.fetchall()
            if not rows:
                empty_label = QLabel("No history records found.", self)
                empty_label.setFont(QFont("Segoe UI", 12))
                empty_label.setStyleSheet("color: #5C4033; padding: 20px; text-align: center;")
                content_layout.addWidget(empty_label)
            else:
                for date, score, title in rows:
                    day_widget = QWidget()
                    day_layout = QVBoxLayout(day_widget)
                    day_layout.setSpacing(5)
                    day_layout.setContentsMargins(10, 10, 10, 10)
                    day_widget.setStyleSheet("""
                        QWidget {
                            background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                                                        stop:0 #FFF5F5, stop:1 #FFE4E1);  /* 更柔和的粉色渐变 */
                            border-radius: 10px;
                            border: 1px solid #FFDAB9;  /* 浅桃色 */
                        }
                    """)
                    print("Day widget stylesheet applied")  # 调试信息

                    day_header = QLabel(f"{date} - Score: {score:.2f}", self)
                    day_header.setFont(QFont("Segoe Script", 14, QFont.Weight.Bold))
                    day_header.setStyleSheet("color: #5C4033; padding: 5px;")
                    day_layout.addWidget(day_header)

                    # 称号（带有炫酷动画效果）
                    title_label = QLabel(f"🌸 {title} 🌸", self)
                    title_label.setFont(QFont("Segoe Script", 16, QFont.Weight.Bold))
                    title_label.setObjectName("titleLabel")
                    title_label.setStyleSheet("""
                        QLabel#titleLabel {
                            color: #D81B60;  /* 深玫红色 */
                            background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                                                        stop:0 #FFDAB9, stop:1 #FF9999);  /* 浅桃色到樱花粉 */
                            padding: 8px;
                            border-radius: 8px;
                            border: 1px solid #FF9999;  /* 樱花粉 */
                            text-align: center;
                        }
                    """)
                    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

                    # 添加透明度动画
                    self.add_glow_animation(title_label)
                    day_layout.addWidget(title_label)

                    # 属性和因素
                    cursor.execute("SELECT attr_name, attr_score FROM attributes WHERE date = ?", (date,))
                    attrs = cursor.fetchall()
                    for attr, attr_score in attrs:
                        attr_label = QLabel(f"{attr}: {attr_score:.2f}", self)
                        attr_label.setFont(QFont("Segoe UI", 12))
                        attr_label.setStyleSheet("color: #5C4033; padding-left: 20px; padding-top: 2px;")
                        day_layout.addWidget(attr_label)

                        cursor.execute("SELECT factor_name, factor_score FROM factors WHERE date = ? AND attr_name = ?", (date, attr))
                        factors = cursor.fetchall()
                        for factor, f_score in factors:
                            factor_label = QLabel(f"• {factor}: {f_score}", self)
                            factor_label.setFont(QFont("Segoe UI", 11))
                            factor_label.setStyleSheet("color: #5C4033; padding-left: 40px;")
                            day_layout.addWidget(factor_label)

                        cursor.execute("SELECT event FROM events WHERE date = ? AND attr_name = ?", (date, attr))
                        event = cursor.fetchone()
                        if event and event[0]:
                            event_label = QLabel(f"📝 {event[0]}", self)
                            event_label.setFont(QFont("Segoe UI", 11, italic=True))
                            event_label.setStyleSheet("color: #5C4033; padding-left: 40px; padding-top: 2px; padding-bottom: 2px;")
                            day_layout.addWidget(event_label)

                    content_layout.addWidget(day_widget)

        scroll.setWidget(content)
        self.content_layout.addWidget(scroll)

    def add_glow_animation(self, label):
        """为称号标签添加透明度动画效果"""
        print(f"Starting animation for title: {label.text()}")  # 调试信息

        # 使用 QGraphicsOpacityEffect 实现透明度动画
        try:
            opacity_effect = QGraphicsOpacityEffect(label)
            label.setGraphicsEffect(opacity_effect)

            animation = QPropertyAnimation(opacity_effect, b"opacity", self)
            animation.setDuration(2000)  # 动画持续 2 秒
            animation.setLoopCount(-1)   # 无限循环
            animation.setEasingCurve(QEasingCurve.Type.InOutSine)

            # 透明度从 0.5 到 1.0 变化
            animation.setKeyValueAt(0, 0.5)
            animation.setKeyValueAt(0.5, 1.0)
            animation.setKeyValueAt(1, 0.5)

            # 启动动画
            animation.start()
        except Exception as e:
            print(f"Animation failed: {e}")
            # 备用方案：使用 styleSheet 动画颜色
            color_animation = QPropertyAnimation(label, b"styleSheet", self)
            color_animation.setDuration(2000)
            color_animation.setLoopCount(-1)
            color_animation.setEasingCurve(QEasingCurve.Type.InOutSine)

            base_style = """
                QLabel#titleLabel {
                    color: #D81B60;
                    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                                                stop:0 #FFDAB9, stop:1 #FF9999);
                    padding: 8px;
                    border-radius: 8px;
                    border: 1px solid #FF9999;
                    text-align: center;
                }
            """
            glow_style = """
                QLabel#titleLabel {
                    color: #D81B60;
                    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                                                stop:0 #FF9999, stop:1 #FFDAB9);
                    padding: 8px;
                    border-radius: 8px;
                    border: 1px solid #FF9999;
                    text-align: center;
                }
            """

            color_animation.setKeyValueAt(0, base_style)
            color_animation.setKeyValueAt(0.5, glow_style)
            color_animation.setKeyValueAt(1, base_style)
            color_animation.start()

    def center_on_screen(self):
        # 使用 PyQt6 的 QGuiApplication.primaryScreen() 居中显示
        screen = QGuiApplication.primaryScreen().geometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)