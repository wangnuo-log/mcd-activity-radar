# -*- coding: utf-8 -*-
"""麦麦随机选餐彩蛋 · 确定性装卦（查表）引擎

定位（合规边界，务必遵守）
------------------------
本模块把中国传统易学「京房纳甲」体系的卦象当作一种**随机符号**，
为「今天吃什么」这类选择困难提供有仪式感的趣味玩法。
它是一个**娱乐性的随机选餐游戏**，不提供任何预测性结论，
输出结果不构成任何形式的建议。

技术说明
--------
抽样与装卦全部是查表型确定性计算（随机数之外无任何启发式），
不依赖大模型心算，保证同一输入（日期 + 种子）完全可复现。

规则依据：京房纳甲体系，属传统易学公开常数。
"""

import json
import os
import random
from datetime import datetime

# ---------------------------------------------------------------------------
# 一、基础常数表
# ---------------------------------------------------------------------------

# 八卦：卦名 -> (三爻, 从下到上，1=阳 0=阴)
BAGUA = {
    "乾": [1, 1, 1],
    "兑": [1, 1, 0],
    "离": [1, 0, 1],
    "震": [1, 0, 0],
    "巽": [0, 1, 1],
    "坎": [0, 1, 0],
    "艮": [0, 0, 1],
    "坤": [0, 0, 0],
}
GUA_BY_BITS = {tuple(v): k for k, v in BAGUA.items()}

# 八卦自然象 -> 卦名（用于从卦名反解上下卦）
XIANG2GUA = {"天": "乾", "泽": "兑", "火": "离", "雷": "震",
             "风": "巽", "水": "坎", "山": "艮", "地": "坤"}
GUA2XIANG = {v: k for k, v in XIANG2GUA.items()}

# 纳支：卦名 -> 六爻地支（初爻到上爻）
NAZHI = {
    "乾": ["子", "寅", "辰", "午", "申", "戌"],
    "兑": ["巳", "卯", "丑", "亥", "酉", "未"],
    "离": ["卯", "丑", "亥", "酉", "未", "巳"],
    "震": ["子", "寅", "辰", "午", "申", "戌"],
    "巽": ["丑", "亥", "酉", "未", "巳", "卯"],
    "坎": ["寅", "辰", "午", "申", "戌", "子"],
    "艮": ["辰", "午", "申", "戌", "子", "寅"],
    "坤": ["未", "巳", "卯", "丑", "亥", "酉"],
}

# 八宫六十四卦（本宫/一世/二世/三世/四世/五世/游魂/归魂）
GONG_GUA = {
    "乾": ["乾为天", "天风姤", "天山遁", "天地否", "风地观", "山地剥", "火地晋", "火天大有"],
    "坤": ["坤为地", "地雷复", "地泽临", "地天泰", "雷天大壮", "泽天夬", "水天需", "水地比"],
    "震": ["震为雷", "雷地豫", "雷水解", "雷风恒", "地风升", "水风井", "泽风大过", "泽雷随"],
    "巽": ["巽为风", "风天小畜", "风火家人", "风雷益", "天雷无妄", "火雷噬嗑", "山雷颐", "山风蛊"],
    "坎": ["坎为水", "水泽节", "水雷屯", "水火既济", "泽火革", "雷火丰", "地火明夷", "地水师"],
    "离": ["离为火", "火山旅", "火风鼎", "火水未济", "山水蒙", "风水涣", "天水讼", "天火同人"],
    "艮": ["艮为山", "山火贲", "山天大畜", "山泽损", "火泽睽", "天泽履", "风泽中孚", "风山渐"],
    "兑": ["兑为泽", "泽水困", "泽地萃", "泽山咸", "水山蹇", "地山谦", "雷山小过", "雷泽归妹"],
}
SHI_POS = [6, 1, 2, 3, 4, 5, 4, 3]  # 与上表 8 种世位一一对应
SHI_NAME = ["", "初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]

# 八宫五行（京房纳甲：六亲以「卦宫五行」为基准，非世爻五行）
GONG_WUXING = {"乾": "金", "兑": "金", "坤": "土", "艮": "土",
               "震": "木", "巽": "木", "坎": "水", "离": "火"}

DIZHI = "子丑寅卯辰巳午未申酉戌亥"
TIANGAN = "甲乙丙丁戊己庚辛壬癸"
ZHI_WUXING = {"子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火",
              "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水"}

# 六神（按日干起排，从初爻到上爻）
LIUSHEN = ["青龙", "朱雀", "勾陈", "螣蛇", "白虎", "玄武"]
LIUSHEN_START = [0, 0, 1, 1, 2, 3, 4, 4, 5, 5]  # 甲~癸

# 节气近似表（用于定月建；固定日期，误差 ±1 天，趣味玩法足够）
JIEQI = [(1, 6, "丑"), (2, 4, "寅"), (3, 6, "卯"), (4, 5, "辰"), (5, 6, "巳"),
         (6, 6, "午"), (7, 7, "未"), (8, 8, "申"), (9, 8, "酉"), (10, 8, "戌"),
         (11, 7, "亥"), (12, 7, "子")]

# 五行生克
SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

# 六亲推导顺序（展示用）
LIUQIN_ORDER = ["父母", "兄弟", "子孙", "妻财", "官鬼"]

# ---------------------------------------------------------------------------
# 二、卦表构造： (外卦, 内卦) -> 卦信息
# ---------------------------------------------------------------------------

def _parse_gua_name(name):
    """从卦名反解 (外卦, 内卦)。如 天风姤 -> (乾, 巽)；乾为天 -> (乾, 乾)。"""
    if "为" in name:
        g = name.split("为")[0]
        return g, g
    return XIANG2GUA[name[0]], XIANG2GUA[name[1]]


GUA_TABLE = {}
for _gong, _names in GONG_GUA.items():
    for _i, _nm in enumerate(_names):
        _wai, _nei = _parse_gua_name(_nm)
        GUA_TABLE[(_wai, _nei)] = {"name": _nm, "gong": _gong, "shi": SHI_POS[_i]}

assert len(GUA_TABLE) == 64, "六十四卦表构造异常：%d" % len(GUA_TABLE)

# ---------------------------------------------------------------------------
# 三、历法：日干支 / 月建（纯标准库）
# ---------------------------------------------------------------------------

def julian_day(y, m, d):
    """公历 -> 儒略日数（当日中午）。"""
    a = (14 - m) // 12
    y2 = y + 4800 - a
    m2 = m + 12 * a - 3
    return d + (153 * m2 + 2) // 5 + 365 * y2 + y2 // 4 - y2 // 100 + y2 // 400 - 32045


def day_ganzhi(dt):
    """返回 (天干, 地支, 干支串)。基准：2000-01-01 为戊午日。"""
    idx = (julian_day(dt.year, dt.month, dt.day) + 49) % 60
    gan, zhi = TIANGAN[idx % 10], DIZHI[idx % 12]
    return gan, zhi, gan + zhi


def month_zhi(dt):
    """按节气近似取月建地支。"""
    key = (dt.month, dt.day)
    zhi = "子"  # 小寒前属上年子月
    for m, d, z in JIEQI:
        if (m, d) <= key:
            zhi = z
    return zhi


# ---------------------------------------------------------------------------
# 四、抽样与装卦
# ---------------------------------------------------------------------------

def toss(seed=None):
    """确定性抽样：模拟三枚铜钱掷六次（初爻 -> 上爻）。seed 固定则结果可复现。"""
    rnd = random.Random(seed)
    lines = []
    for i in range(6):
        coins = [rnd.choice((2, 3)) for _ in range(3)]  # 3=正(阳) 2=反(阴)
        total = sum(coins)
        if total == 9:
            yang, moving, mark = 1, True, "老阳"
        elif total == 6:
            yang, moving, mark = 0, True, "老阴"
        elif total == 8:
            yang, moving, mark = 1, False, "少阳"
        else:
            yang, moving, mark = 0, False, "少阴"
        lines.append({"pos": i + 1, "yang": yang, "moving": moving,
                      "mark": mark, "coins": coins})
    return lines


def _gua_of(bits):
    return GUA_BY_BITS[tuple(bits)]


def _liuqin(wuxing, base):
    """以世爻五行为基准判定六亲。"""
    if wuxing == base:
        return "兄弟"          # 同我者
    if SHENG[wuxing] == base:
        return "父母"          # 生我者
    if SHENG[base] == wuxing:
        return "子孙"          # 我生者
    if KE[wuxing] == base:
        return "官鬼"          # 克我者
    return "妻财"              # 我克者


def build(dt=None, seed=None, lines=None):
    """抽样 + 装卦，返回完整卦盘（确定性）。lines 可显式传入以便测试。"""
    dt = dt or datetime.now()
    lines = lines if lines is not None else toss(seed)
    bits = [l["yang"] for l in lines]
    nei, wai = _gua_of(bits[0:3]), _gua_of(bits[3:6])
    base_meta = GUA_TABLE[(wai, nei)]

    moving = [i for i, l in enumerate(lines) if l["moving"]]
    bian_meta = None
    if moving:
        bbits = [1 - b if l["moving"] else b for b, l in zip(bits, lines)]
        bnei, bwai = _gua_of(bbits[0:3]), _gua_of(bbits[3:6])
        bian_meta = GUA_TABLE[(bwai, bnei)]

    # 纳支：内卦前三爻 + 外卦后三爻
    nazhi = NAZHI[nei][0:3] + NAZHI[wai][3:6]

    dgan, dzhi, dgz = day_ganzhi(dt)
    mzhi = month_zhi(dt)

    start = LIUSHEN_START[TIANGAN.index(dgan)]
    shen = [LIUSHEN[(start + i) % 6] for i in range(6)]

    shi = base_meta["shi"]
    ying = ((shi - 1 + 3) % 6) + 1
    base_wx = GONG_WUXING[base_meta["gong"]]  # 六亲基准 = 卦宫五行（京房纳甲传统）

    six = []
    for i in range(6):
        z = nazhi[i]
        six.append({
            "pos": i + 1,
            "pos_name": SHI_NAME[i + 1],
            "mark": lines[i]["mark"],
            "yang": lines[i]["yang"],
            "moving": lines[i]["moving"],
            "shen": shen[i],
            "zhi": z,
            "wuxing": ZHI_WUXING[z],
            "liuqin": _liuqin(ZHI_WUXING[z], base_wx),
            "role": "世" if i + 1 == shi else ("应" if i + 1 == ying else ""),
        })

    return {
        "date": dt.strftime("%Y-%m-%d"),
        "time": dt.strftime("%H:%M"),
        "weekday": "周" + "一二三四五六日"[dt.weekday()],
        "day_gz": dgz,
        "day_gan": dgan,
        "day_zhi": dzhi,
        "month_zhi": mzhi,
        "ben": {"name": base_meta["name"], "gong": base_meta["gong"],
                "shi": shi, "ying": ying, "wai": wai, "nei": nei},
        "bian": ({"name": bian_meta["name"], "gong": bian_meta["gong"]}
                 if bian_meta else None),
        "moving_count": len(moving),
        "moving_pos": [p + 1 for p in moving],
        "six": six,
        "base_wuxing": base_wx,
    }


# ---------------------------------------------------------------------------
# 五、卦象 -> 口味线索 -> 真实餐品映射
# ---------------------------------------------------------------------------

# 六神 -> 口味线索（关键词用于匹配真实菜单名称）
LIUSHEN_TASTE = {
    "青龙": {"tag": "尝鲜", "desc": "东方木气，主生发 —— 适合当季新品与清新之选",
             "kw": ["龙焰", "多笋", "鳕鱼", "蔬", "苹果", "玉米"]},
    "朱雀": {"tag": "热辣", "desc": "南方火气，主热烈 —— 适合辣味与热食",
             "kw": ["辣", "椒盐", "川", "韩式", "鸡排"]},
    "勾陈": {"tag": "厚实", "desc": "中央土气，主厚重 —— 适合牛肉与主食",
             "kw": ["牛", "巨无霸", "吉士", "安格斯"]},
    "螣蛇": {"tag": "甜蜜", "desc": "土气缠绵，主甜腻 —— 适合甜品与冰品",
             "kw": ["麦旋风", "新地", "圆筒", "派", "冰淇淋", "雪冰", "黑巧"]},
    "白虎": {"tag": "酥脆", "desc": "西方金气，主刚脆 —— 适合炸物与酥香",
             "kw": ["鸡", "薯", "脆", "V翅", "麦乐鸡"]},
    "玄武": {"tag": "清爽", "desc": "北方水气，主寒润 —— 适合冰饮与清口",
             "kw": ["可乐", "雪碧", "冰", "汁", "柠", "橙", "奶", "茶", "咖啡", "纯悦"]},
}

# 世爻五行 -> 辅助线索
WUXING_TASTE = {
    "木": {"tag": "清新", "kw": ["蔬", "笋", "苹果", "玉米", "鳕鱼"]},
    "火": {"tag": "辛香", "kw": ["辣", "椒盐", "川", "韩式"]},
    "土": {"tag": "扎实", "kw": ["牛", "巨无霸", "吉士", "堡"]},
    "金": {"tag": "酥香", "kw": ["鸡", "薯", "脆", "V翅"]},
    "水": {"tag": "清润", "kw": ["可乐", "冰", "汁", "茶", "咖啡"]},
}


def _filter(meals, kws):
    return [m for m in meals if any(k in m["name"] for k in kws)]


def _stable_pick(cands, hexa, salt=0):
    """由卦象派生的确定性索引（同卦同选）。"""
    h = sum(ord(c) for c in hexa["ben"]["name"])
    h += hexa["moving_count"] * 13 + salt * 7 + len(hexa["six"])
    return cands[h % len(cands)]


def pick_meal(hexa, meals):
    """按卦象（世爻六神为主线）从真实菜单选出「随机之选」。"""
    shi_line = hexa["six"][hexa["ben"]["shi"] - 1]
    shen, wuxing = shi_line["shen"], shi_line["wuxing"]
    taste = LIUSHEN_TASTE[shen]
    wuxing_taste = WUXING_TASTE[wuxing]

    pool = _filter(meals, taste["kw"]) or meals
    main = _stable_pick(pool, hexa, 0)

    others = [m for m in pool if m["code"] != main["code"]]
    if len(others) < 2:
        others = [m for m in meals if m["code"] != main["code"]]

    alts = []
    for k in range(2):
        alts.append(_stable_pick(others, hexa, salt=k + 1))

    return {
        "shen": shen,
        "wuxing": wuxing,
        "liuqin": shi_line["liuqin"],
        "taste": taste["tag"],
        "taste_desc": taste["desc"],
        "wuxing_taste": wuxing_taste["tag"],
        "main": main,
        "alts": alts,
        "pool_size": len(pool),
    }


def load_menu(path=None):
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "sample_data", "menu.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)["meals"]


# ---------------------------------------------------------------------------
# 六、文本渲染
# ---------------------------------------------------------------------------

def render_markdown(hexa, pick):
    b = hexa["ben"]
    lines = []
    lines.append("# 今日手气 · 随机选餐")
    lines.append("")
    lines.append("> %s（%s）| 月建：%s | 日辰：%s | 抽样：确定性随机" %
                 (hexa["date"], hexa["weekday"], hexa["month_zhi"], hexa["day_gz"]))
    lines.append("")

    # 卦象
    arrow = " → %s" % hexa["bian"]["name"] if hexa["bian"] else ""
    lines.append("## 卦象")
    lines.append("")
    lines.append("本卦：**%s**（%s宫，%s）%s" %
                 (b["name"], b["gong"], SHI_NAME[b["shi"]] + "世", arrow))
    lines.append("")
    lines.append("| 爻位 | 六神 | 六亲 | 纳支 | 爻象 | 动 |")
    lines.append("|---|---|---|---|---|---|")
    for l in sorted(hexa["six"], key=lambda x: -x["pos"]):
        mark = "▅▅▅▅▅" if l["yang"] else "▅▅ ▅▅"
        role = (" ·" + l["role"]) if l["role"] else ""
        lines.append("| %s%s | %s | %s | %s%s | %s | %s |" %
                     (l["pos_name"], role, l["shen"], l["liuqin"],
                      l["zhi"], l["wuxing"], mark, "○" if l["moving"] else ""))
    lines.append("")

    # 口味指引
    lines.append("## 口味指引")
    lines.append("")
    lines.append("- 世爻：%s（%s%s），六神 **%s**，五行 **%s**" %
                 (hexa["six"][b["shi"] - 1]["pos_name"],
                  hexa["six"][b["shi"] - 1]["zhi"],
                  hexa["six"][b["shi"] - 1]["wuxing"], pick["shen"], pick["wuxing"]))
    lines.append("- 今日手气：**%s** ｜ %s" % (pick["taste"], pick["taste_desc"]))
    lines.append("- 五行佐味：%s" % pick["wuxing_taste"])
    lines.append("")

    # 推荐
    lines.append("## 随机之选")
    lines.append("")
    m = pick["main"]
    lines.append("1. **%s** ¥%s  · %s" % (m["name"], m["price"], m["category"]))
    for i, a in enumerate(pick["alts"], 2):
        lines.append("%d. %s ¥%s  · %s" % (i, a["name"], a["price"], a["category"]))
    lines.append("")
    lines.append("> 本玩法以传统卦象作随机符号，属娱乐性选餐游戏，不构成任何建议；"
                 "餐品价格与供应以门店实时为准。")
    return "\n".join(lines)


def build_and_pick(dt=None, seed=None, meals=None):
    hexa = build(dt=dt, seed=seed)
    meals = meals if meals is not None else load_menu()
    return hexa, pick_meal(hexa, meals)


if __name__ == "__main__":
    h, p = build_and_pick()
    print(render_markdown(h, p))
