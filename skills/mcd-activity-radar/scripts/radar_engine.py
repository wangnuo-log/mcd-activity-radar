"""麦麦活动雷达 · 确定性引擎（纯标准库）。

职责边界（和「取数给 MCP、算术给代码、表达给 Agent」一致）：
  - 解析：把 MCP 返回的活动文案切成结构化活动对象      ← 本模块
  - 去重：同名不同文案（如联名第一弹/第二弹）视为不同活动  ← 本模块
  - 抽取：从营销文案里正则捞出「开售/开抢时间」并算倒计时  ← 本模块
  - 分类：按关键词把活动归到 5 个情报类别               ← 本模块
  - 表达：交给 WorkBuddy Agent 讲解                     ← 不在本模块

为什么必须用代码而不是大模型：
  1) 营销文案写的是「10月15日10:45开售」，让 LLM 心算「还有几天几小时」不可靠；
  2) 活动日历里同一活动会跨多天重复出现，靠 LLM 去重会漏；
  3) 正则 + datetime 的结果可复现、可测试。
"""
import re
from datetime import datetime

# ---------------------------------------------------------------- 类别定义
CATEGORIES = [
    ("门店活动", ["派对", "体验营", "品鉴会", "读书会", "过家家", "亲子", "遛娃", "职业体验"]),
    ("联名限定", ["联名", "限定", "周边", "徽章", "丝巾", "棒球帽", "珍藏", "限量", "联名款"]),
    ("抽奖福利", ["抽奖", "霸王餐", "麦金喜", "中奖"]),
    ("新品上市", ["上新", "新品", "登场", "回归", "来啦", "首发", "全新", "开吃", "新口味"]),
    ("优惠福利", ["券", "优惠", "折", "只要", "免配", "学生", "会员", "免费", "元起", "特惠",
                  "麦金卡", "早餐卡", "学期卡", "套餐"]),
]
CATEGORY_ORDER = [c[0] for c in CATEGORIES] + ["其他"]

# 时间关键词 → 事件类型
LAUNCH_WORDS = ["开售", "开抢", "开卖", "开始", "抢先购", "上市", "上线"]

_SECTION_RE = re.compile(r"^####\s*(\d{4})年(\d{1,2})月(\d{1,2})日\s*(.*)$")
_TITLE_RE = re.compile(r"^-\s*\*\*活动标题\*\*[：:]\s*(.+)$")
_BODY_RE = re.compile(r"^\s*\*\*活动内容介绍\*\*[：:]\s*(.*)$")
_IMG_RE = re.compile(r'<img\s+src="([^"]+)"')
_DT_RE = re.compile(r"(\d{1,2})月(\d{1,2})日\s*(\d{1,2})[:：](\d{2})")
_TIME_ONLY_RE = re.compile(r"(?<![:\d])(\d{1,2})[:：](\d{2})")


def classify(title, body):
    text = (title or "") + (body or "")
    for name, kws in CATEGORIES:
        for kw in kws:
            if kw in text:
                return name
    return "其他"


def parse_activities(md):
    """把活动日历 markdown 切成 (日期 × 活动) 条目。"""
    out = []
    cur_date = None
    cur_tag = ""
    cur = None

    def flush():
        if cur and cur.get("title"):
            out.append(dict(cur, body="\n".join(cur["body"]).strip()))

    for raw in md.splitlines():
        line = raw.rstrip()
        m = _SECTION_RE.match(line)
        if m:
            flush()
            cur = None
            y, mo, d, rest = m.groups()
            cur_date = datetime(int(y), int(mo), int(d)).date()
            cur_tag = (rest or "").strip()
            continue
        mt = _TITLE_RE.match(line)
        if mt:
            flush()
            cur = {"date": cur_date, "title": mt.group(1).strip(),
                   "body": [], "image": None, "tag": cur_tag}
            continue
        if cur is None:
            continue
        mb = _BODY_RE.match(line)
        if mb:
            if mb.group(1).strip():
                cur["body"].append(mb.group(1).strip())
            continue
        mi = _IMG_RE.search(line)
        if mi:
            cur["image"] = mi.group(1)
            continue
        if line.strip() and "**活动图片介绍**" not in line:
            cur["body"].append(line.strip())
    flush()
    return out


def group_activities(acts):
    """按 (标题, 文案) 去重：同一活动跨多天出现会被合并成一条，记录全部日期。

    注意：联名第一弹（棒球帽）与第二弹（徽章）标题相同但文案不同，必须算两条。
    """
    groups = {}
    for a in acts:
        key = (a["title"], a["body"])
        g = groups.get(key)
        if g is None:
            g = {"title": a["title"], "body": a["body"], "image": a["image"],
                 "dates": [], "tags": set()}
            groups[key] = g
        g["dates"].append(a["date"])
        g["tags"].add(a["tag"])
        if not g["image"]:
            g["image"] = a["image"]
    return list(groups.values())


def extract_launch(body, activity_date):
    """从文案里抽「开售/开抢时间」。返回 (datetime|None, 命中短语)。"""
    if not body:
        return None, None
    for m in _DT_RE.finditer(body):
        mo, d, hh, mm = (int(x) for x in m.groups())
        try:
            dt = datetime(activity_date.year, mo, d, hh, mm)
        except ValueError:
            continue
        if _near_word(body, m.start(), m.end(), LAUNCH_WORDS):
            return dt, m.group(0)
    # 只有时间的情形：积分抢先购10:40开抢 → 归到活动当天
    for m in _TIME_ONLY_RE.finditer(body):
        seg = body[max(0, m.start() - 14):m.end() + 10]
        before = body[max(0, m.start() - 14):m.start()]
        if re.search(r"\d{1,2}月|\d{1,2}日", before):
            continue  # 已带日期，交给上面的分支
        if not any(w in seg for w in LAUNCH_WORDS):
            continue
        hh, mm = int(m.group(1)), int(m.group(2))
        if hh > 23:
            continue
        return datetime(activity_date.year, activity_date.month,
                        activity_date.day, hh, mm), m.group(0)
    return None, None


def _near_word(text, start, end, words, window=20):
    seg = text[max(0, start - window):min(len(text), end + window)]
    return any(w in seg for w in words)


def countdown(target, now):
    delta = target - now
    secs = int(delta.total_seconds())
    if secs < 0:
        return "已开始"
    d, rem = divmod(secs, 86400)
    h, rem = divmod(rem, 3600)
    m = rem // 60
    parts = []
    if d:
        parts.append("%d 天" % d)
    if h or d:
        parts.append("%d 小时" % h)
    if m and not d:
        parts.append("%d 分钟" % m)
    return "还有 " + " ".join(parts) if parts else "即将开始"


def build_radar(calendar_md, party_json=None, goods_json=None,
                account_json=None, now=None):
    """把各路数据合成一份雷达报告（dict）。"""
    now = now or datetime.now()
    today = now.date()

    groups = group_activities(parse_activities(calendar_md))
    active, upcoming, past = [], [], []
    launch_board = []

    for g in groups:
        g["category"] = classify(g["title"], g["body"])
        g["dates"] = sorted(g["dates"])
        g["first_date"] = g["dates"][0]
        g["last_date"] = g["dates"][-1]
        future = [d for d in g["dates"] if d > today]
        g["next_date"] = future[0] if future else None
        g["is_active"] = (today in g["dates"]) or ("今日" in g["tags"])
        g["launch"], g["launch_phrase"] = extract_launch(g["body"], g["first_date"])
        if g["launch"] and g["launch"] > now and g["next_date"]:
            g["countdown"] = countdown(g["launch"], now)
        else:
            g["countdown"] = None

        if g["is_active"]:
            active.append(g)
        elif g["next_date"]:
            upcoming.append(g)
        else:
            past.append(g)

        if g["launch"] and g["launch"] > now:
            launch_board.append(g)

    active.sort(key=lambda x: (CATEGORY_ORDER.index(x["category"]), x["title"]))
    upcoming.sort(key=lambda x: (x["next_date"], CATEGORY_ORDER.index(x["category"])))
    past.sort(key=lambda x: x["last_date"], reverse=True)
    launch_board.sort(key=lambda x: x["launch"])

    goods = (goods_json or {}).get("data", [])
    parties = (party_json or {}).get("data", [])
    account = (account_json or {}).get("data", {}) or {}

    return {
        "generated_at": now, "today": today,
        "active": active, "upcoming": upcoming, "past": past,
        "launch_board": launch_board,
        "goods": goods, "parties": parties, "account": account,
    }


def _fmt_date(d):
    return "%d月%d日" % (d.month, d.day)


def _brief(body, max_lines=3):
    """取文案前几行做简报，避免 markdown 过长。"""
    lines = [x for x in (body or "").split("\n") if x.strip()]
    txt = "  \n  ".join(lines[:max_lines])
    if len(lines) > max_lines:
        txt += " …"
    return txt


def render_markdown(radar, brief=True):
    L = ["# 📡 麦麦活动雷达", "",
         "> 数据时间：%s ｜ 非麦当劳官方产品，活动与价格以麦当劳官方渠道为准。"
         % radar["generated_at"].strftime("%Y-%m-%d %H:%M"), ""]

    lb = radar["launch_board"]
    if lb:
        L += ["## ⏰ 开抢倒计时", "",
              "| 倒计时 | 开抢时间 | 活动 | 类别 |", "|---|---|---|---|"]
        for a in lb:
            L.append("| **%s** | %s | %s | %s |" % (
                a["countdown"], a["launch"].strftime("%m-%d %H:%M"), a["title"], a["category"]))
        L.append("")

    if radar["active"]:
        L += ["## 🔥 正在进行（%d）" % len(radar["active"]), ""]
        for a in radar["active"]:
            L.append("- **[%s] %s**" % (a["category"], a["title"]))
            if a["body"]:
                L.append("  " + _brief(a["body"]))
        L.append("")

    if radar["upcoming"]:
        L += ["## 📅 即将到来（%d）" % len(radar["upcoming"]), ""]
        cur = None
        for a in radar["upcoming"]:
            if a["next_date"] != cur:
                cur = a["next_date"]
                L.append("**%s**" % _fmt_date(cur))
            tail = ""
            if a["launch"] and a["launch"] == datetime(cur.year, cur.month, cur.day,
                                                      a["launch"].hour, a["launch"].minute):
                tail = "（%s 开抢，%s）" % (a["launch"].strftime("%H:%M"), a["countdown"] or "")
            L.append("- [%s] %s%s" % (a["category"], a["title"], tail))
        L.append("")

    if radar["goods"]:
        L += ["## 🎁 限定周边（积分兑换 · 限量）", "",
              "| 商品 | 积分 | 卖点 | 窗口 |", "|---|---:|---|---|"]
        for g in radar["goods"]:
            L.append("| %s | %s | %s | %s ~ %s |" % (
                g.get("spuName"), g.get("point"), g.get("selling"),
                (g.get("upTime") or "")[:10], (g.get("downTime") or "")[:10]))
        L.append("")

    if radar["parties"]:
        L += ["## 🎉 门店活动（可预约）", "",
              "| 活动 | 类目 | 价格 | spuId |", "|---|---|---:|---:|"]
        for p in radar["parties"]:
            L.append("| %s | %s | ¥%s | %s |" % (
                p.get("spuName"), p.get("catName"), p.get("price"), p.get("spuId")))
        L.append("")

    acc = radar["account"]
    if acc:
        L += ["## 👤 你的账户", "",
              "- 可用积分：**%s**" % acc.get("availablePoint", "-"),
              "- 累计积分：%s" % acc.get("accumulativePoint", "-")]
        if acc.get("currentMouthExpirePoint") not in (None, "0", "0.0"):
            L.append("- ⚠️ 本月将过期积分：**%s**" % acc["currentMouthExpirePoint"])
        if acc.get("expiredPoint") not in (None, "0", "0.0"):
            L.append("- 已过期积分：%s" % acc["expiredPoint"])
        L.append("")

    if radar["past"]:
        L += ["## 🕘 往期（最近）", ""]
        for a in radar["past"][:8]:
            L.append("- %s [%s] %s" % (_fmt_date(a["last_date"]), a["category"], a["title"]))
        L.append("")

    L += ["---",
          "*本作品为麦当劳程序员节创意开发大赛参赛作品，由参赛者独立开发，非麦当劳官方产品。"
          "餐品信息、价格及供应状态以麦当劳官方渠道的实时结果为准。*"]
    return "\n".join(L)


def summarize(radar):
    hot = radar["launch_board"][0] if radar["launch_board"] else None
    s = "正在进行 %d 条、即将到来 %d 条、开抢倒计时 %d 个" % (
        len(radar["active"]), len(radar["upcoming"]), len(radar["launch_board"]))
    if hot:
        s += "；最近的是「%s」，%s" % (hot["title"], hot["countdown"])
    return s
