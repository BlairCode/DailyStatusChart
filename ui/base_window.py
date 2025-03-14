# 文件：base_window.py
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve

class BaseWindow(QMainWindow):
    def __init__(self, title="App"):
        super().__init__()
        self.setWindowTitle(title)
        self.setMinimumSize(400, 500)  # 默认最小尺寸
        self.setWindowOpacity(0)  # 初始透明度为0
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)  # 移除默认标题栏和边框
        self.drag_position = QPoint()  # 用于窗口拖动
        self.is_fullscreen = False  # 跟踪全屏状态
        self.title = title  # 存储标题以便显示
        self.init_ui()

    def init_ui(self):
        # 主布局
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)  # 移除外边距
        self.main_layout.setSpacing(0)  # 移除间距

        # 自定义标题栏
        self.title_bar_widget = QWidget()
        self.title_bar_widget.setFixedHeight(30)  # 固定标题栏高度
        title_bar = QHBoxLayout(self.title_bar_widget)
        title_bar.setContentsMargins(5, 0, 5, 0)  # 微调内边距
        self.title_bar_widget.setStyleSheet("""
            background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                                        stop:0 #FFDAB9, stop:1 #FF9999); /* 标题栏渐变 */
            border-bottom: 1px solid #D8BFD8; /* 细边框区分 */
        """)  # 设置标题栏样式，Diary 风格

        # 添加软件名
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("""
            color: #5C4033;
            font: bold 14px 'Segoe Script';
            padding: 2px 5px;
        """)  # 设置软件名样式
        title_bar.addWidget(self.title_label)

        # 标题栏按钮
        self.min_button = QPushButton("−")
        self.max_full_button = QPushButton("□")
        self.close_button = QPushButton("×")
        title_bar.addStretch()  # 按钮靠右
        title_bar.addWidget(self.min_button)
        title_bar.addWidget(self.max_full_button)
        title_bar.addWidget(self.close_button)

        # 连接按钮信号
        self.close_button.clicked.connect(self.close)
        self.min_button.clicked.connect(self.showMinimized)
        self.max_full_button.clicked.connect(self.toggle_max_full)

        # 内容区域（子类会填充）
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.setSpacing(25)

        # 添加到主布局
        self.main_layout.addWidget(self.title_bar_widget)
        self.main_layout.addWidget(self.content_widget)

        # 设置中心部件
        central_widget = QWidget(self)
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)

        # 自定义窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #FFF8E1, stop:1 #FCE4EC);
                border: none;
            }
            QMainWindow QPushButton {
                background: #FFDAB9;
                color: #5C4033;
                border: none;
                padding: 2px 8px;
            }
            QMainWindow QPushButton:hover {
                background: #FF9999;
            }
        """)  # 设置窗口和标题栏按钮样式

        # 初始设置按钮大小
        self.update_button_sizes()

    def toggle_max_full(self):
        if self.isFullScreen():
            self.setMinimumSize(400, 500)
            self.showNormal()
            self.is_fullscreen = False
        else:
            self.showFullScreen()
            self.is_fullscreen = True
        self.update_button_sizes()  # 更新按钮大小

    def update_button_sizes(self):
        if self.is_fullscreen:
            size = 40, 30  # 全屏时按钮更大
            font_size = 16
        else:
            size = 30, 20  # 正常状态
            font_size = 12
        for btn in (self.min_button, self.max_full_button, self.close_button):
            btn.setFixedSize(*size)
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
            """)
        self.title_bar_widget.setFixedHeight(size[1] + 10)
        self.title_label.setStyleSheet(f"""
            color: #5C4033;
            font: bold {font_size}px 'Segoe Script';
            padding: 2px 5px;
        """)  # 动态调整标题栏和按钮样式

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
    animation.setDuration(150)
    animation.setStartValue(btn.geometry())
    animation.setEndValue(btn.geometry().adjusted(0, -2, 0, -2))
    animation.setEasingCurve(QEasingCurve.Type.OutQuad)
    animation.start()
    btn.clicked.connect(lambda: animate_button(btn))