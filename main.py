import sys  # 处理系统操作，here：exit
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QColor, QPalette
from ui.main_window import MainWindow

def main():
    # 处理 sys.argv 可能为空的问题，确保打包后稳定运行
    args = sys.argv if len(sys.argv) > 1 else [sys.executable]
    app = QApplication(args)  # 创建QApplication实例

    # 设置 Fusion 样式并应用 Diary 风格背景
    app.setStyle("Fusion")
    app.setStyleSheet("""
        QMainWindow {
            background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, 
                                        stop:0 #FFF3E4, stop:1 #FCE4EC);
        }
    """)

    # 自定义调色板（按钮颜色，Diary 风格）
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Button, QColor("#FFDAB9"))  # 浅桃色
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#5C4033"))  # 深棕色文字
    app.setPalette(palette)
    
    try:
        # 创建窗口实例
        window = MainWindow()
        window.show()

        sys.exit(app.exec())  # app.exec() 启动 Qt 的 事件循环（Event Loop）
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()