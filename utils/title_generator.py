# utils/title_generator.py
import sqlite3
from utils.database import DB_PATH
from utils.constants import ATTR_NAMES, ATTR_WEIGHTS
import statistics

def generate_title(attr_scores, today):
    """
    根据每日属性得分生成称号。
    
    参数：
    - attr_scores: 今日每个属性的得分列表（与 ATTR_NAMES 对应）
    - today: 今日日期（用于查询历史数据）
    
    返回：
    - title: 今日的称号（字符串）
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # 计算总分
        total_score = sum(s * w for s, w in zip(attr_scores, ATTR_WEIGHTS))

        # 获取历史均值
        historical_means = []
        for attr in ATTR_NAMES:
            cursor.execute("SELECT AVG(attr_score) FROM attributes WHERE attr_name = ? AND date < ?", (attr, today))
            mean_score = cursor.fetchone()[0] or 0  # 如果没有历史记录，均值为 0
            historical_means.append(mean_score)

        # 计算今日提升比例
        improvements = []
        for attr_score, mean_score in zip(attr_scores, historical_means):
            if mean_score == 0:  # 避免除以 0
                improvement = attr_score * 100 if attr_score > 0 else 0
            else:
                improvement = ((attr_score - mean_score) / mean_score) * 100  # 提升百分比
            improvements.append(improvement)

        # 1. 突出属性称号（优先级最高）
        title = None
        max_improvement = max(improvements) if improvements else 0
        if max_improvement > 30:  # 提升超过 30%，认为是突出属性
            max_idx = improvements.index(max_improvement)
            attr_name = ATTR_NAMES[max_idx]
            # 根据提升程度和属性给称号
            if max_improvement > 50:
                if attr_name == "智慧之光 (Wisdom Radiance)":
                    title = "智慧大师 (Master of Wisdom)"
                elif attr_name == "生命之泉 (Vitality Spring)":
                    title = "活力之王 (King of Vitality)"
                elif attr_name == "星光魅影 (Starlight Charm)":
                    title = "社交之星 (Star of Charm)"
                elif attr_name == "灵感火花 (Inspiration Flame)":
                    title = "创意天才 (Genius of Inspiration)"
                elif attr_name == "心弦之音 (Heartstring Melody)":
                    title = "心灵乐师 (Maestro of Heartstrings)"
                elif attr_name == "意志引擎 (Willpower Engine)":
                    title = "意志斗士 (Warrior of Willpower)"
            elif max_improvement > 30:
                if attr_name == "智慧之光 (Wisdom Radiance)":
                    title = "智慧新星 (Rising Star of Wisdom)"
                elif attr_name == "生命之泉 (Vitality Spring)":
                    title = "活力精灵 (Sprite of Vitality)"
                elif attr_name == "星光魅影 (Starlight Charm)":
                    title = "魅力新秀 (Rising Star of Charm)"
                elif attr_name == "灵感火花 (Inspiration Flame)":
                    title = "灵感小火苗 (Spark of Inspiration)"
                elif attr_name == "心弦之音 (Heartstring Melody)":
                    title = "心弦轻弹 (Gentle Heartstring Player)"
                elif attr_name == "意志引擎 (Willpower Engine)":
                    title = "意志新兵 (Rookie of Willpower)"

        # 2. 综合得分称号（次高优先级）
        if not title:
            if total_score > 24:
                title = "完美一天 (Perfect Day)"
            elif total_score > 18:
                title = "充实一天 (Fulfilling Day)"
            elif total_score > 12:
                title = "平稳一天 (Stable Day)"
            else:
                title = "悠闲一天 (Relaxed Day)"

        # 3. 均衡性称号（次优先级）
        if not title:
            std_dev = statistics.stdev(attr_scores) if len(attr_scores) > 1 else 0
            if std_dev < 1.0:  # 标准差小于 1，说明属性得分很均衡
                title = "均衡之星 (Star of Balance)"

        # 4. 波动性称号（次低优先级）
        if not title:
            min_improvement = min(improvements) if improvements else 0
            if min_improvement < -30:  # 下降超过 30%
                min_idx = improvements.index(min_improvement)
                attr_name = ATTR_NAMES[min_idx]
                if attr_name == "智慧之光 (Wisdom Radiance)":
                    title = "智慧需充电 (Wisdom Needs Recharge)"
                elif attr_name == "生命之泉 (Vitality Spring)":
                    title = "活力需补充 (Vitality Needs Boost)"
                elif attr_name == "星光魅影 (Starlight Charm)":
                    title = "魅力需点亮 (Charm Needs Spark)"
                elif attr_name == "灵感火花 (Inspiration Flame)":
                    title = "灵感需引燃 (Inspiration Needs Ignition)"
                elif attr_name == "心弦之音 (Heartstring Melody)":
                    title = "心弦需调整 (Heartstrings Need Tuning)"
                elif attr_name == "意志引擎 (Willpower Engine)":
                    title = "意志需加油 (Willpower Needs Fuel)"

        # 5. 默认称号（最低优先级）
        if not title:
            title = "普通一天 (Normal Day)"

        # 保存到数据库
        cursor.execute("INSERT OR REPLACE INTO daily_status (date, score, title) VALUES (?, ?, ?)", (today, total_score, title))
        conn.commit()

    return title