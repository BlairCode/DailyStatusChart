from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor
from utils.database import DB_PATH
from utils.constants import ICON_DIR
from utils.helpers import apply_gradient_background, animate_open
import sqlite3
import os

class RankingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ranking")
        self.setFixedSize(700, 500)
        self.setWindowOpacity(0)
        self.init_ui()
        animate_open(self)

    def init_ui(self):
        layout = QVBoxLayout()
        table = QTableWidget(self)
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Rank", "Date", "Score", "Title"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setStyleSheet("""
            QTableWidget {
                background: transparent;
                color: #5C4033;  /* 深棕色 */
                border: none;
                font: 12px 'Segoe UI';
            }
            QHeaderView::section {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #FFDAB9, stop:1 #FF9999);  /* 浅桃色到樱花粉 */
                color: #5C4033;
                font: bold 14px 'Segoe Script';
                padding: 5px;
                border: none;
                border-bottom: 1px solid #FF9999;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid rgba(255, 218, 185, 0.3);  /* 浅桃色透明边框 */
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #FFF5F5, stop:1 #FFE4E1);  /* 柔和粉色渐变 */
            }
            QTableWidget::item:hover {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #FF9999, stop:1 #FFDAB9);  /* 樱花粉到浅桃色 */
            }
            /* 为前三名行添加动画效果 */
            QTableWidget#rankingTable tr:nth-child(1) { animation: glow 2s infinite ease-in-out; }
            QTableWidget#rankingTable tr:nth-child(2) { animation: glow 2s infinite ease-in-out; }
            QTableWidget#rankingTable tr:nth-child(3) { animation: glow 2s infinite ease-in-out; }
            @keyframes glow {
                0% { background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #FFF5F5, stop:1 #FFE4E1); }
                50% { background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #FF9999, stop:1 #FFDAB9); }
                100% { background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #FFF5F5, stop:1 #FFE4E1); }
            }
        """)
        table.setObjectName("rankingTable")  # 为表格设置唯一标识符以应用动画
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # 背景样式（与 HistoryDialog 一致）
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #FFF8E1, stop:1 #FCE4EC);
            }
        """)

        # 从数据库加载排行榜数据
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT date, score, title FROM daily_status ORDER BY score DESC")
            rows = cursor.fetchall()
            table.setRowCount(len(rows))
            for i, (date, score, title) in enumerate(rows):
                # 排名列
                rank_text = f"{i + 1}"
                if i == 0:
                    rank_text = f"🥇 {i + 1}"  # 第一名：金牌
                elif i == 1:
                    rank_text = f"🥈 {i + 1}"  # 第二名：银牌
                elif i == 2:
                    rank_text = f"🥉 {i + 1}"  # 第三名：铜牌
                else:
                    rank_text = f"🌟 {i + 1}"  # 其他排名：发光星星

                rank_item = QTableWidgetItem(rank_text)
                rank_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(i, 0, rank_item)

                # 日期列
                date_item = QTableWidgetItem(f"🌸 {date}")
                date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(i, 1, date_item)

                # 分数列
                score_item = QTableWidgetItem(f"{score:.2f}")
                score_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if score >= 25:
                    score_item.setText(f"🔥 {score:.2f}")  # 高分加火焰图标
                table.setItem(i, 2, score_item)

                # 称号列
                title_item = QTableWidgetItem(f"✨ {title}")
                title_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(i, 3, title_item)

        layout.addWidget(table)
        self.setLayout(layout)
        apply_gradient_background(self)