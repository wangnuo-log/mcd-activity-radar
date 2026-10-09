"""麦麦活动雷达 · 自测（纯标准库，unittest）。

运行： python selftest.py
所有断言基于真实 MCP 返回的脱敏样本，改逻辑后必跑。
"""
import os
import sys
import unittest
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import radar_engine as E  # noqa: E402
import qian_engine as Q  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLE = os.path.join(HERE, "sample_data")
NOW = datetime(2026, 10, 9, 15, 0)


def _cal():
    with open(os.path.join(SAMPLE, "campaign_calendar.md"), encoding="utf-8") as f:
        return f.read()


class TestParse(unittest.TestCase):
    def test_parse_count(self):
        acts = E.parse_activities(_cal())
        self.assertGreaterEqual(len(acts), 25)

    def test_section_dates(self):
        acts = E.parse_activities(_cal())
        dates = {a["date"].strftime("%m-%d") for a in acts}
        self.assertIn("10-09", dates)
        self.assertIn("10-22", dates)

    def test_image_extracted(self):
        acts = E.parse_activities(_cal())
        with_img = [a for a in acts if a["image"]]
        self.assertTrue(all(a["image"].startswith("http") for a in with_img))
        self.assertGreater(len(with_img), 10)


class TestGroup(unittest.TestCase):
    def setUp(self):
        self.g = E.group_activities(E.parse_activities(_cal()))

    def test_dedup_merges_multidate(self):
        # 「麦当劳 X PEACEMINUSONE」棒球帽版在 10-08 与 10-09 都出现 → 合并为一条
        pc = [g for g in self.g if "PEACEMINUSONE" in g["title"]]
        self.assertEqual(len(pc), 2, "棒球帽版与徽章版应算两条（文案不同）")
        hat = [g for g in pc if "棒球帽" in g["body"]][0]
        self.assertGreaterEqual(len(hat["dates"]), 2)

    def test_group_count_less_than_raw(self):
        raw = E.parse_activities(_cal())
        self.assertLess(len(self.g), len(raw))


class TestClassify(unittest.TestCase):
    def test_party(self):
        self.assertEqual(E.classify("过家家派对上线", ""), "门店活动")
        self.assertEqual(E.classify("乐享90分钟高质量亲子时间", ""), "门店活动")

    def test_limited(self):
        self.assertEqual(E.classify("第三周周边即将开售✨限定主题丝巾！", ""), "联名限定")
        self.assertEqual(E.classify("麦当劳 X PEACEMINUSONE", "周边第二弹——联名徽章即将发售"), "联名限定")

    def test_new_product(self):
        self.assertEqual(E.classify("🫐一口爆汁！蓝莓爆爆珠麦旋风上新", ""), "新品上市")

    def test_lottery(self):
        self.assertEqual(E.classify("预约麦金喜抽奖，🉐[积分霸王餐]", ""), "抽奖福利")

    def test_promo(self):
        self.assertEqual(E.classify("学生专属！49元150天麦金学期卡💳", ""), "优惠福利")

    def test_unknown(self):
        self.assertEqual(E.classify("随便一个标题", ""), "其他")


class TestLaunch(unittest.TestCase):
    def test_explicit_datetime(self):
        dt, _ = E.extract_launch("周边第二弹——联名徽章即将发售\n10月15日10:45开售", datetime(2026, 10, 15).date())
        self.assertEqual(dt, datetime(2026, 10, 15, 10, 45))

    def test_time_only_uses_activity_date(self):
        dt, _ = E.extract_launch("更有APP专享积分抢先购10:40开抢", datetime(2026, 10, 8).date())
        self.assertEqual(dt, datetime(2026, 10, 8, 10, 40))

    def test_no_launch(self):
        dt, _ = E.extract_launch("地道的黑巧，风味浓郁醇厚", datetime(2026, 10, 14).date())
        self.assertIsNone(dt)

    def test_does_not_misfire_on_price(self):
        # 「15.9元起」里的数字不应被当成时间
        dt, _ = E.extract_launch("鸡薯双全盒仅需15.9元起", datetime(2026, 10, 9).date())
        self.assertIsNone(dt)


class TestCountdown(unittest.TestCase):
    def test_days_hours(self):
        s = E.countdown(datetime(2026, 10, 15, 10, 45), NOW)
        self.assertTrue(s.startswith("还有 5 天"))
        self.assertIn("小时", s)

    def test_started(self):
        self.assertEqual(E.countdown(datetime(2026, 10, 1), NOW), "已开始")

    def test_minutes_only(self):
        s = E.countdown(datetime(2026, 10, 9, 15, 30), NOW)
        self.assertIn("分钟", s)
        self.assertNotIn("天", s)


class TestRadar(unittest.TestCase):
    def setUp(self):
        import json
        with open(os.path.join(SAMPLE, "mall_points_party.json"), encoding="utf-8") as f:
            party = json.load(f)
        with open(os.path.join(SAMPLE, "mall_points_goods.json"), encoding="utf-8") as f:
            goods = json.load(f)
        with open(os.path.join(SAMPLE, "my_account.json"), encoding="utf-8") as f:
            acc = json.load(f)
        self.r = E.build_radar(_cal(), party, goods, acc, now=NOW)

    def test_buckets_nonempty(self):
        self.assertGreater(len(self.r["active"]), 5)
        self.assertGreaterEqual(len(self.r["upcoming"]), 3)

    def test_launch_board_sorted(self):
        lb = self.r["launch_board"]
        self.assertTrue(all(lb[i]["launch"] <= lb[i + 1]["launch"] for i in range(len(lb) - 1)))

    def test_no_past_in_upcoming(self):
        for a in self.r["upcoming"]:
            self.assertGreater(a["next_date"], self.r["today"])

    def test_markdown_renders(self):
        md = E.render_markdown(self.r)
        self.assertIn("麦麦活动雷达", md)
        self.assertIn("开抢倒计时", md)
        self.assertIn("限定周边", md)
        self.assertIn("门店活动", md)

    def test_account_expired_point(self):
        self.assertEqual(self.r["account"]["expiredPoint"], "5581")

    def test_summarize(self):
        s = E.summarize(self.r)
        self.assertIn("正在进行", s)

    def test_launch_board_excludes_started(self):
        for a in self.r["launch_board"]:
            self.assertGreater(a["launch"], NOW)

    def test_json_serializable(self):
        import json
        import radar_cli
        json.dumps(radar_cli._jsonable(self.r), ensure_ascii=False)


# ---------------------------------------------------------------------------
# 今日手气 · 麦门签（六爻引擎）
# ---------------------------------------------------------------------------

_MENU = None


def _menu():
    global _MENU
    if _MENU is None:
        _MENU = Q.load_menu()
    return _MENU


def _lines(bits):
    return [{"pos": i + 1, "yang": b, "moving": False, "mark": "少阳", "coins": [3, 3, 2]}
            for i, b in enumerate(bits)]


class TestGanzhi(unittest.TestCase):
    def test_day_ganzhi_verified(self):
        # 对照公开黄历：2026-10-09 为丙午年 戊戌月 丙辰日
        self.assertEqual(Q.day_ganzhi(datetime(2026, 10, 9))[2], "丙辰")

    def test_day_ganzhi_anchors(self):
        self.assertEqual(Q.day_ganzhi(datetime(2000, 1, 1))[2], "戊午")
        self.assertEqual(Q.day_ganzhi(datetime(1949, 10, 1))[2], "甲子")

    def test_month_zhi(self):
        self.assertEqual(Q.month_zhi(datetime(2026, 10, 9)), "戌")   # 寒露后 → 戌月
        self.assertEqual(Q.month_zhi(datetime(2026, 10, 5)), "酉")   # 寒露前 → 酉月


class TestGuaTable(unittest.TestCase):
    def test_count(self):
        self.assertEqual(len(Q.GUA_TABLE), 64)

    def test_known(self):
        self.assertEqual(Q.GUA_TABLE[("乾", "巽")]["name"], "天风姤")
        self.assertEqual(Q.GUA_TABLE[("乾", "巽")]["gong"], "乾")
        self.assertEqual(Q.GUA_TABLE[("乾", "巽")]["shi"], 1)
        self.assertEqual(Q.GUA_TABLE[("乾", "乾")]["name"], "乾为天")
        self.assertEqual(Q.GUA_TABLE[("坎", "乾")]["gong"], "坤")
        self.assertEqual(Q.GUA_TABLE[("离", "乾")]["name"], "火天大有")


class TestLiuqin(unittest.TestCase):
    def test_qian_wei_tian(self):
        h = Q.build(dt=NOW, lines=_lines([1, 1, 1, 1, 1, 1]))
        self.assertEqual([l["liuqin"] for l in h["six"]],
                         ["子孙", "妻财", "父母", "官鬼", "兄弟", "父母"])

    def test_tian_feng_gou(self):
        h = Q.build(dt=NOW, lines=_lines([0, 1, 1, 1, 1, 1]))
        self.assertEqual(h["ben"]["name"], "天风姤")
        self.assertEqual(h["ben"]["shi"], 1)
        self.assertEqual([l["liuqin"] for l in h["six"]],
                         ["父母", "子孙", "兄弟", "官鬼", "兄弟", "父母"])


class TestBuild(unittest.TestCase):
    def test_reproducible(self):
        a = Q.build(dt=NOW, seed=20261009)
        b = Q.build(dt=NOW, seed=20261009)
        self.assertEqual(a["ben"]["name"], b["ben"]["name"])
        self.assertEqual([l["zhi"] for l in a["six"]], [l["zhi"] for l in b["six"]])

    def test_shi_ying_distance(self):
        h = Q.build(dt=NOW, seed=7)
        shi = [l for l in h["six"] if l["role"] == "世"]
        ying = [l for l in h["six"] if l["role"] == "应"]
        self.assertEqual(len(shi), 1)
        self.assertEqual(len(ying), 1)
        self.assertEqual(abs(shi[0]["pos"] - ying[0]["pos"]), 3)

    def test_six_lines(self):
        h = Q.build(dt=NOW, seed=3)
        self.assertEqual(len(h["six"]), 6)
        self.assertTrue(all(len(l["zhi"]) == 1 for l in h["six"]))
        self.assertTrue(all(l["shen"] in Q.LIUSHEN for l in h["six"]))


class TestFortunePick(unittest.TestCase):
    def test_pick_from_menu(self):
        h, p = Q.build_and_pick(dt=NOW, seed=20261009, meals=_menu())
        codes = {m["code"] for m in _menu()}
        self.assertIn(p["main"]["code"], codes)
        self.assertEqual(len(p["alts"]), 2)
        for a in p["alts"]:
            self.assertIn(a["code"], codes)

    def test_pick_reproducible(self):
        _, p1 = Q.build_and_pick(dt=NOW, seed=11, meals=_menu())
        _, p2 = Q.build_and_pick(dt=NOW, seed=11, meals=_menu())
        self.assertEqual(p1["main"]["code"], p2["main"]["code"])

    def test_markdown(self):
        h, p = Q.build_and_pick(dt=NOW, seed=5, meals=_menu())
        md = Q.render_markdown(h, p)
        self.assertIn("今日手气", md)
        self.assertIn("天意之选", md)

    def test_json_serializable(self):
        import json
        h, p = Q.build_and_pick(dt=NOW, seed=5, meals=_menu())
        json.dumps({"hexagram": h, "pick": p}, ensure_ascii=False)

    def test_compliance_no_divination_words(self):
        # 合规红线：输出中不得出现占卜/预测类措辞
        h, p = Q.build_and_pick(dt=NOW, seed=5, meals=_menu())
        md = Q.render_markdown(h, p)
        for w in ("占卜", "预测", "运势", "吉凶", "算命", "灵验"):
            self.assertNotIn(w, md)


if __name__ == "__main__":
    unittest.main(verbosity=2)
