from PyQt6.QtGui import QPalette, QColor, QLinearGradient, QBrush
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve

def apply_gradient_background(widget):
    palette = widget.palette()
    gradient = QLinearGradient(0, 0, 0, widget.height())
    gradient.setColorAt(0, QColor("#d4a1ff"))  # 浅紫色渐变开始色
    gradient.setColorAt(1, QColor("#f4b3d1"))  # 浅粉色渐变结束色
    palette.setBrush(QPalette.ColorRole.Window, QBrush(gradient))
    widget.setPalette(palette)

def animate_open(widget):
    anim = QPropertyAnimation(widget, b"windowOpacity", widget)
    anim.setDuration(400)
    anim.setStartValue(0)
    anim.setEndValue(1)
    anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
    anim.start()