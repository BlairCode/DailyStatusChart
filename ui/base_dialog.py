# 文件：base_dialog.py
from PyQt6.QtWidgets import QDialog, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QPoint

class BaseDialog(QDialog):
    def __init__(self, parent=None, title="Dialog"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(400, 500)
        self.setWindowOpacity(0)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.drag_position = QPoint()
        self.is_fullscreen = False
        self.title = title
        self.init_ui()

    def init_ui(self):
        # 主布局
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 自定义标题栏
        self.title_bar_widget = QWidget()
        self.title_bar_widget.setFixedHeight(30)
        title_bar = QHBoxLayout(self.title_bar_widget)
        title_bar.setContentsMargins(5, 0, 5, 0)
        self.title_bar_widget.setStyleSheet("""
            background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                                        stop:0 #FFDAB9, stop:1 #FF9999);
            border-bottom: 1px solid #D8BFD8;
        """)

        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("""
            color: #5C4033;
            font: bold 14px 'Segoe Script';
            padding: 2px 5px;
        """)
        title_bar.addWidget(self.title_label)

        self.min_button = QPushButton("−")
        self.max_full_button = QPushButton("□")
        self.close_button = QPushButton("×")
        title_bar.addStretch()
        title_bar.addWidget(self.min_button)
        title_bar.addWidget(self.max_full_button)
        title_bar.addWidget(self.close_button)

        self.close_button.clicked.connect(self.close)
        self.min_button.clicked.connect(self.showMinimized)
        self.max_full_button.clicked.connect(self.toggle_max_full)

        # 内容区域（不预设 layout 类型，由子类定义）
        self.content_widget = QWidget()
        # 不在这里设置 content_layout，让子类自由定义
        # self.content_layout = QVBoxLayout(self.content_widget)

        self.main_layout.addWidget(self.title_bar_widget)
        self.main_layout.addWidget(self.content_widget)

        self.setLayout(self.main_layout)

        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #FFF8E1, stop:1 #FCE4EC);
                border: none;
            }
            QDialog QPushButton {
                background: #FFDAB9;
                color: #5C4033;
                border: none;
                padding: 2px 8px;
            }
            QDialog QPushButton:hover {
                background: #FF9999;
            }
        """)

        self.update_button_sizes()

    def toggle_max_full(self):
        if self.isFullScreen():
            self.setMinimumSize(400, 500)
            self.showNormal()
            self.is_fullscreen = False
        else:
            self.showFullScreen()
            self.is_fullscreen = True
        self.update_button_sizes()

    def update_button_sizes(self):
        if self.is_fullscreen:
            size = 40, 30
            font_size = 16
        else:
            size = 30, 20
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
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()