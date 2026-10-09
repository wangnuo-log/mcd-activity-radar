"""麦麦活动雷达 · 命令行入口。

用法：
  python radar_cli.py --demo                     # 离线跑通（内置样本，无需 Token）
  python radar_cli.py --demo --html              # 输出麦当劳风格单文件 HTML
  python radar_cli.py --demo --html --out demo.html
  python radar_cli.py --demo --json              # 输出结构化 JSON
  python radar_cli.py --live                     # 接入真实麦当劳 MCP（需 MCD_MCP_TOKEN）
  python radar_cli.py --live --only 联名限定      # 只看某一类情报
  python radar_cli.py --demo --today 2026-10-20
  python radar_cli.py --fortune                  # 只出「今日手气·麦门签」（娱乐彩蛋）
  python radar_cli.py --fortune --seed 20261009  # 固定种子，起卦可复现
  python radar_cli.py --demo --no-fortune        # 雷达输出中不带手气签
"""
import argparse
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import radar_engine as E  # noqa: E402
import qian_engine as Q  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLE = os.path.join(HERE, "sample_data")

# 主题活动类目（mall-points-products 的 catRuleIds）
PARTY_CATS = "1>6>20,1>6>21,1>6>22,1>6>25,1>6>34,1>6>40"
GOODS_CATS = "2>8"


def load_sample():
    with open(os.path.join(SAMPLE, "campaign_calendar.md"), encoding="utf-8") as f:
        cal = f.read()
    with open(os.path.join(SAMPLE, "mall_points_party.json"), encoding="utf-8") as f:
        party = json.load(f)
    with open(os.path.join(SAMPLE, "mall_points_goods.json"), encoding="utf-8") as f:
        goods = json.load(f)
    with open(os.path.join(SAMPLE, "my_account.json"), encoding="utf-8") as f:
        acc = json.load(f)
    return cal, party, goods, acc


def load_live():
    from mcd_client import MCDClient, extract_json
    c = MCDClient()
    c.initialize()
    cal, _ = c.call("campaign-calendar", {})
    _, sc = c.call("mall-points-products", {"catRuleIds": PARTY_CATS})
    party = sc or extract_json(_) or {"data": []}
    _, sc2 = c.call("mall-points-products", {"catRuleIds": GOODS_CATS})
    goods = sc2 or extract_json(_) or {"data": []}
    _, sc3 = c.call("query-my-account", {})
    acc = sc3 or {"data": {}}
    return cal, party, goods, acc


def apply_filter(radar, only):
    if not only:
        return radar
    for k in ("active", "upcoming", "past"):
        radar[k] = [a for a in radar[k] if a["category"] == only]
    radar["launch_board"] = [a for a in radar["launch_board"] if a["category"] == only]
    return radar


def main():
    ap = argparse.ArgumentParser(description="麦麦活动雷达")
    ap.add_argument("--demo", action="store_true", help="离线样本模式（无需 Token）")
    ap.add_argument("--live", action="store_true", help="接入真实 MCP")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--today", help="覆盖基准日期，格式 YYYY-MM-DD")
    ap.add_argument("--only", help="只看某一类（如 联名限定）")
    ap.add_argument("--html", action="store_true", help="输出麦当劳风格单文件 HTML")
    ap.add_argument("--out", help="输出写入指定文件（UTF-8），不填则打印到终端")
    ap.add_argument("--categories", action="store_true", help="列出全部情报类别后退出")
    ap.add_argument("--fortune", action="store_true", help="只出「今日手气·麦门签」（娱乐向选餐彩蛋）")
    ap.add_argument("--no-fortune", action="store_true", help="雷达输出中不附带手气签")
    ap.add_argument("--seed", type=int, help="起卦种子（同 seed 可复现同一签）")
    args = ap.parse_args()

    if args.categories:
        print("情报类别：", "、".join(E.CATEGORY_ORDER))
        return

    if not (args.demo or args.live):
        args.demo = True  # 默认离线，保证任何人 clone 后即可跑通

    now = datetime.now()
    if args.today:
        d = datetime.strptime(args.today, "%Y-%m-%d")
        now = d.replace(hour=now.hour, minute=now.minute)

    # 今日手气（娱乐彩蛋）：默认随雷达一起输出
    fortune = None
    if args.fortune or not args.no_fortune:
        fortune = Q.build_and_pick(dt=now, seed=args.seed)

    if args.fortune:
        hexa, pick = fortune
        if args.html:
            from radar_html import render_fortune_only
            text = render_fortune_only(hexa, pick)
        elif args.json:
            text = json.dumps(_jsonable({"hexagram": hexa, "pick": pick}),
                              ensure_ascii=False, indent=2)
        else:
            text = Q.render_markdown(hexa, pick)
        _emit(text, args.out)
        return

    cal, party, goods, acc = load_live() if args.live else load_sample()
    radar = E.build_radar(cal, party, goods, acc, now=now)
    radar = apply_filter(radar, args.only)

    if args.html:
        from radar_html import render_html
        text = render_html(radar, fortune=fortune)
    elif args.json:
        out = _jsonable(radar)
        if fortune:
            out["fortune"] = _jsonable({"hexagram": fortune[0], "pick": fortune[1]})
        text = json.dumps(out, ensure_ascii=False, indent=2)
    else:
        text = E.render_markdown(radar) + "\n\n> 摘要：" + E.summarize(radar)
        if fortune:
            text += "\n\n---\n\n" + Q.render_markdown(fortune[0], fortune[1])

    _emit(text, args.out)


def _emit(text, out):
    if out:
        with open(out, "w", encoding="utf-8") as f:
            f.write(text)
        print("已写入 %s" % out)
    else:
        print(text)


def _jsonable(radar):
    def conv(o):
        if isinstance(o, dict):
            return {k: conv(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [conv(v) for v in o]
        if isinstance(o, (set, frozenset)):
            return sorted(conv(v) for v in o)
        if isinstance(o, datetime):
            return o.strftime("%Y-%m-%d %H:%M")
        if hasattr(o, "isoformat"):
            return o.isoformat()
        return o
    return conv(radar)


if __name__ == "__main__":
    main()
