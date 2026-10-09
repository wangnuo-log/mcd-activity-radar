"""麦麦活动雷达 · HTML 渲染框架（麦当劳风格）。

产出**单文件 HTML**（样式与脚本全部内联，零外部依赖）：
  - 双击即可在浏览器打开查看
  - 可直接部署到 GitHub Pages 作为在线 demo

设计约定
--------
  - 品牌色：麦当劳红 #DA291C + 金黄 #FFC72C（仅用配色基因）
  - 所有图形均为自绘（同心圆雷达图标），**不使用麦当劳官方 Logo**
  - 想换风格：只改 STYLE 常量里的 CSS 变量即可，结构不用动

用法
----
    from radar_html import render_html
    html = render_html(radar)
"""
import html as _html


def esc(s):
    return _html.escape("" if s is None else str(s), quote=True)


# 情报类别 -> 徽章配色 class
CATEGORY_CLASS = {
    "联名限定": "c-red",
    "新品上市": "c-amber",
    "门店活动": "c-green",
    "抽奖福利": "c-purple",
    "优惠福利": "c-blue",
    "其他": "c-gray",
}

STYLE = """
:root{
  --red:#DA291C; --yellow:#FFC72C; --ink:#1A1A1A; --muted:#6B6B6B;
  --bg:#FFFBF5; --card:#FFFFFF; --line:#F1E4D2; --line-soft:#F7EEE2;
}
*{box-sizing:border-box;margin:0;padding:0}
body{
  font-family:system-ui,-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
  background:var(--bg);color:var(--ink);line-height:1.6;-webkit-font-smoothing:antialiased;
}
.wrap{max-width:980px;margin:0 auto;padding:0 20px}
a{color:var(--red)}

.hero{background:var(--red);color:#fff;padding:36px 0 40px;position:relative}
.hero:after{content:"";position:absolute;left:0;right:0;bottom:0;height:6px;background:var(--yellow)}
.brand{display:flex;align-items:center;gap:16px}
.brand h1{font-size:30px;font-weight:800;letter-spacing:.5px;line-height:1.2}
.brand .tag{font-size:14px;color:#FFE9B8;margin-top:2px}
.meta{margin-top:18px;font-size:12.5px;color:#FFD9A0;display:flex;flex-wrap:wrap;gap:6px 18px}
.meta b{color:#fff;font-weight:600}

.sec{margin-top:34px}
.sec>h2{font-size:17px;font-weight:800;display:flex;align-items:center;gap:9px;margin-bottom:14px}
.sec>h2 .dot{width:4px;height:17px;border-radius:2px;background:var(--red)}
.sec>h2 .cnt{background:var(--yellow);color:var(--ink);font-size:11.5px;font-weight:700;
  border-radius:999px;padding:2px 9px;line-height:1.5}

.count-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(215px,1fr));gap:13px}
.count-card{background:var(--card);border:1px solid var(--line);border-left:5px solid var(--red);
  border-radius:12px;padding:15px 17px}
.count-card .t{font-size:12.5px;color:var(--muted);margin-bottom:7px;
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.count-card .cd{font-size:25px;font-weight:800;color:var(--red);
  font-variant-numeric:tabular-nums;letter-spacing:-.5px}
.count-card .sm{font-size:11.5px;color:var(--muted);margin-top:4px}

.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:13px}
.stat{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px}
.stat .n{font-size:24px;font-weight:800;color:var(--ink);font-variant-numeric:tabular-nums}
.stat .l{font-size:12px;color:var(--muted);margin-top:2px}

.filters{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:14px}
.filters button{font:inherit;font-size:12.5px;padding:5px 13px;border-radius:999px;cursor:pointer;
  background:var(--card);border:1px solid var(--line);color:var(--muted);transition:.15s}
.filters button:hover{border-color:var(--red);color:var(--red)}
.filters button.on{background:var(--red);border-color:var(--red);color:#fff;font-weight:600}

.act{background:var(--card);border:1px solid var(--line);border-radius:12px;
  padding:13px 15px;margin-bottom:10px;display:flex;gap:14px;align-items:flex-start}
.act img{width:70px;height:70px;border-radius:10px;object-fit:cover;flex:0 0 auto;background:var(--line-soft)}
.act .body{min-width:0;flex:1}
.act .hd{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin-bottom:5px}
.act .ti{font-size:14.5px;font-weight:700;line-height:1.35}
.act .tx{font-size:12.8px;color:var(--muted);white-space:pre-line;
  display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.act .when{font-size:11.5px;color:var(--red);font-weight:600;margin-top:5px}

.badge{font-size:11px;font-weight:600;padding:2px 8px;border-radius:999px;white-space:nowrap;
  border:1px solid transparent}
.c-red{background:#FDECEA;color:#B31D12;border-color:#F8CFCA}
.c-amber{background:#FFF6E0;color:#8A5A00;border-color:#FBE0A8}
.c-green{background:#EAF6EC;color:#1E6B36;border-color:#CCE7D3}
.c-purple{background:#F2EDFB;color:#5B3CA6;border-color:#DED2F5}
.c-blue{background:#EAF2FB;color:#1B5FA8;border-color:#CFE1F5}
.c-gray{background:#F3F1EE;color:#5F5E5A;border-color:#E2DFD9}

.date-h{font-size:12.5px;font-weight:700;color:var(--muted);margin:16px 0 8px}

table{width:100%;border-collapse:collapse;background:var(--card);
  border:1px solid var(--line);border-radius:12px;overflow:hidden;font-size:13px}
th{background:#FFF4E2;color:#7A4A00;font-size:12px;font-weight:700;text-align:left;padding:10px 13px}
td{padding:10px 13px;border-top:1px solid var(--line-soft);color:#333;vertical-align:top}
td.num{font-variant-numeric:tabular-nums;text-align:right;white-space:nowrap;font-weight:600}
td.mut{color:var(--muted);font-size:12.3px}

.acct{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:13px}
.acct .k{font-size:12px;color:var(--muted)}
.acct .v{font-size:21px;font-weight:800;margin-top:2px;font-variant-numeric:tabular-nums}
.acct .warn{color:var(--red)}

.foot{margin-top:44px;padding:22px 0 0;border-top:1px solid var(--line);
  font-size:12px;color:var(--muted);text-align:center;line-height:1.9}
.foot code{background:var(--line-soft);padding:1px 6px;border-radius:5px;font-size:11.5px}

.qian{border:1px solid var(--line);border-radius:14px;overflow:hidden;background:#FFFDF8}
.qian-hd{background:var(--red);color:#fff;padding:13px 18px;display:flex;flex-wrap:wrap;
  gap:6px 16px;align-items:baseline}
.qian-hd .gn{font-size:21px;font-weight:800;letter-spacing:2px}
.qian-hd .gs{font-size:12px;color:#FFE0B0}
.qian-hd .gt{margin-left:auto;font-size:11.5px;color:#FFD9A0}
.qian-bd{padding:16px 18px 18px}
.qian-tbl{width:100%;border-collapse:collapse;font-size:12.5px;margin-bottom:14px}
.qian-tbl th{background:#FFF4E2;color:#7A4A00;font-size:11.5px;font-weight:700;
  text-align:left;padding:7px 10px}
.qian-tbl td{padding:7px 10px;border-top:1px solid var(--line-soft);color:#333}
.qian-tbl .glyph{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;color:#B31D12;
  letter-spacing:1px;white-space:nowrap}
.qian-tbl .role{display:inline-block;font-size:10px;font-weight:700;color:#fff;background:var(--red);
  border-radius:4px;padding:0 4px;margin-left:5px}
.qian-taste{font-size:13px;color:#444;margin-bottom:12px;line-height:1.75}
.qian-taste b{color:var(--red)}
.qian-pick{background:#FFF6E0;border:1px dashed #EFC46B;border-radius:10px;padding:13px 16px}
.qian-pick .lab{font-size:11.5px;color:#8A5A00;font-weight:700;margin-bottom:6px}
.qian-pick .m{font-size:16px;font-weight:800;color:var(--red);font-variant-numeric:tabular-nums}
.qian-pick .m .p{font-size:13px;color:#8A5A00;font-weight:600}
.qian-pick .alt{font-size:12.5px;color:#6B6B6B;margin-top:7px;line-height:1.8}
.qian-note{font-size:11px;color:var(--muted);margin-top:11px;line-height:1.7}
"""


def _radar_icon():
    # 自绘同心圆雷达图标（不使用麦当劳官方 Logo）
    return (
        '<svg viewBox="0 0 48 48" width="46" height="46" aria-hidden="true">'
        '<circle cx="24" cy="24" r="21" fill="none" stroke="#FFC72C" stroke-width="2.4" opacity=".95"/>'
        '<circle cx="24" cy="24" r="13.5" fill="none" stroke="#FFC72C" stroke-width="2" opacity=".6"/>'
        '<circle cx="24" cy="24" r="5" fill="#FFC72C"/>'
        '<line x1="24" y1="24" x2="39" y2="10" stroke="#FFC72C" stroke-width="3" stroke-linecap="round"/>'
        "</svg>"
    )


def _badge(cat):
    return '<span class="badge %s">%s</span>' % (
        CATEGORY_CLASS.get(cat, "c-gray"), esc(cat))


def _act_card(a, when=None):
    img = ""
    if a.get("image"):
        img = ('<img src="%s" alt="" loading="lazy" '
               "onerror=\"this.style.display='none'\">" % esc(a["image"]))
    txt = esc(a.get("body") or "")
    tail = ('<div class="when">%s</div>' % esc(when)) if when else ""
    return (
        '<article class="act" data-cat="%s">%s<div class="body">'
        '<div class="hd">%s<span class="ti">%s</span></div>'
        '<div class="tx">%s</div>%s</div></article>'
        % (esc(a.get("category", "其他")), img, _badge(a.get("category", "其他")),
           esc(a.get("title", "")), txt, tail)
    )


def _fmt_date(d):
    return "%d 月 %d 日" % (d.month, d.day)


# ---------------- 今日手气（娱乐彩蛋）----------------

_POSN = ["", "初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]


def _fortune_block(hexa, pick):
    b = hexa["ben"]
    arrow = (" → " + hexa["bian"]["name"]) if hexa.get("bian") else ""
    L = ['<section class="sec"><h2><span class="dot"></span>今日手气 · 麦门签'
         '<span class="cnt">娱乐</span></h2>', '<div class="qian">']
    L.append('<div class="qian-hd"><span class="gn">%s</span>'
             '<span class="gs">%s宫 · %s世%s</span>'
             '<span class="gt">%s · 月建%s · %s日</span></div>'
             % (esc(b["name"]), esc(b["gong"]), esc(_POSN[b["shi"]]), esc(arrow),
                esc(hexa["date"]), esc(hexa["month_zhi"]), esc(hexa["day_gz"])))
    L.append('<div class="qian-bd">')
    L.append('<table class="qian-tbl"><thead><tr><th>爻位</th><th>六神</th>'
             '<th>六亲</th><th>纳支</th><th>卦画</th></tr></thead><tbody>')
    for l in sorted(hexa["six"], key=lambda x: -x["pos"]):
        glyph = "▅▅▅▅▅" if l["yang"] else "▅▅ ▅▅"
        role = ('<span class="role">%s</span>' % esc(l["role"])) if l.get("role") else ""
        mv = " ○" if l["moving"] else ""
        L.append('<tr><td>%s%s</td><td>%s</td><td>%s</td><td>%s%s</td>'
                 '<td class="glyph">%s%s</td></tr>'
                 % (esc(l["pos_name"]), role, esc(l["shen"]), esc(l["liuqin"]),
                    esc(l["zhi"]), esc(l["wuxing"]), glyph, mv))
    L.append("</tbody></table>")

    L.append('<div class="qian-taste">世爻五行 <b>%s</b>，六神 <b>%s</b> → 今日手气 '
             '<b>%s</b>。<br>%s</div>'
             % (esc(pick["wuxing"]), esc(pick["shen"]), esc(pick["taste"]),
                esc(pick["taste_desc"])))

    m = pick["main"]
    alts = " · ".join("%s ¥%s" % (esc(a["name"]), esc(a["price"])) for a in pick["alts"])
    L.append('<div class="qian-pick"><div class="lab">天意之选</div>'
             '<div class="m">%s <span class="p">¥%s</span></div>'
             '<div class="alt">另有两只备选：%s</div></div>'
             % (esc(m["name"]), esc(m["price"]), alts))
    L.append('<div class="qian-note">玩法说明：以传统卦象作为<b>随机符号</b>的娱乐性选餐游戏，'
             '不做占卜与预测，不构成任何建议；餐品价格与供应以门店实时为准。</div>')
    L.append("</div></div></section>")
    return "".join(L)


def render_fortune_only(hexa, pick):
    """只输出「今日手气」的独立单文件 HTML。"""
    L = ["<!DOCTYPE html>", '<html lang="zh-CN">', "<head>", '<meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width,initial-scale=1">',
         "<title>今日手气 · 麦门签</title>", "<style>%s</style>" % STYLE, "</head>",
         "<body>", '<main class="wrap" style="padding-top:30px">',
         _fortune_block(hexa, pick), "</main>", "</body>", "</html>"]
    return "\n".join(L)


def render_html(radar, repo_url="", fortune=None):
    gen = radar["generated_at"].strftime("%Y-%m-%d %H:%M")
    acc = radar.get("account") or {}
    L = []

    L.append("<!DOCTYPE html>")
    L.append('<html lang="zh-CN">')
    L.append("<head>")
    L.append('<meta charset="utf-8">')
    L.append('<meta name="viewport" content="width=device-width,initial-scale=1">')
    L.append("<title>麦麦活动雷达 · 麦当劳当月活动一屏看完</title>")
    L.append('<meta name="description" content="麦当劳当月活动雷达：开抢倒计时、联名限定周边、'
             '可预约门店活动，基于麦当劳 MCP 数据。">')
    L.append("<style>%s</style>" % STYLE)
    L.append("</head>")
    L.append("<body>")

    # ---------------- Hero ----------------
    L.append('<header class="hero"><div class="wrap"><div class="brand">')
    L.append(_radar_icon())
    L.append('<div><h1>麦麦活动雷达</h1>'
             '<p class="tag">麦当劳当月活动 · 一屏看完 · 开抢不错过</p></div>')
    L.append("</div>")
    L.append('<div class="meta"><span>数据时间 <b>%s</b></span>'
             '<span>数据来源 <b>麦当劳 MCP</b></span>'
             "<span>非麦当劳官方产品</span></div>" % esc(gen))
    L.append("</div></header>")

    L.append('<main class="wrap">')

    # ---------------- 开抢倒计时 ----------------
    lb = radar.get("launch_board") or []
    if lb:
        L.append('<section class="sec"><h2><span class="dot"></span>开抢倒计时'
                 '<span class="cnt">%d</span></h2><div class="count-grid">' % len(lb))
        for a in lb[:6]:
            cd = (a.get("countdown") or "").replace("还有 ", "")
            L.append('<div class="count-card"><div class="t">%s</div>'
                     '<div class="cd">%s</div>'
                     '<div class="sm">%s 开抢</div></div>'
                     % (esc(a["title"]), esc(cd),
                        a["launch"].strftime("%m-%d %H:%M")))
        L.append("</div></section>")

    # ---------------- 概览 ----------------
    L.append('<section class="sec"><h2><span class="dot"></span>本次雷达概览</h2>'
             '<div class="stats">')
    for n, l in ((len(radar.get("active") or []), "正在进行"),
                 (len(radar.get("upcoming") or []), "即将到来"),
                 (len(lb), "开抢倒计时"),
                 (len(radar.get("goods") or []), "限定周边"),
                 (len(radar.get("parties") or []), "可预约门店活动")):
        L.append('<div class="stat"><div class="n">%d</div><div class="l">%s</div></div>' % (n, l))
    L.append("</div></section>")

    # ---------------- 活动流 ----------------
    active = radar.get("active") or []
    upcoming = radar.get("upcoming") or []
    cats = []
    for a in active + upcoming:
        c = a.get("category", "其他")
        if c not in cats:
            cats.append(c)

    if active or upcoming:
        L.append('<section class="sec" data-dynamic><h2><span class="dot"></span>活动情报</h2>')
        L.append('<div class="filters"><button data-cat="all" class="on">全部</button>')
        for c in cats:
            L.append('<button data-cat="%s">%s</button>' % (esc(c), esc(c)))
        L.append("</div>")

        if active:
            L.append('<div class="date-h">正在进行 · %d 条</div>' % len(active))
            for a in active:
                L.append(_act_card(a))

        if upcoming:
            L.append('<div class="date-h">即将到来 · %d 条</div>' % len(upcoming))
            cur = None
            for a in upcoming:
                if a.get("next_date") and a["next_date"] != cur:
                    cur = a["next_date"]
                    L.append('<div class="date-h">%s</div>' % esc(_fmt_date(cur)))
                when = a.get("countdown") and ("%s · %s" % (
                    a["launch"].strftime("%m-%d %H:%M") if a.get("launch") else "", a["countdown"]))
                L.append(_act_card(a, when=when))
        L.append("</section>")

    # ---------------- 今日手气（娱乐彩蛋）----------------
    if fortune:
        L.append(_fortune_block(*fortune))

    # ---------------- 限定周边 ----------------
    goods = radar.get("goods") or []
    if goods:
        L.append('<section class="sec"><h2><span class="dot"></span>限定周边'
                 '<span class="cnt">%d</span></h2>' % len(goods))
        L.append("<table><thead><tr><th>商品</th><th>积分</th><th>卖点</th>"
                 "<th>兑换窗口</th></tr></thead><tbody>")
        for g in goods:
            L.append("<tr><td><b>%s</b></td><td class=\"num\">%s</td>"
                     "<td class=\"mut\">%s</td><td class=\"mut\">%s ~ %s</td></tr>"
                     % (esc(g.get("spuName")), esc(g.get("point")), esc(g.get("selling")),
                        esc((g.get("upTime") or "")[:10]), esc((g.get("downTime") or "")[:10])))
        L.append("</tbody></table></section>")

    # ---------------- 门店活动 ----------------
    parties = radar.get("parties") or []
    if parties:
        L.append('<section class="sec"><h2><span class="dot"></span>可预约门店活动'
                 '<span class="cnt">%d</span></h2>' % len(parties))
        L.append("<table><thead><tr><th>活动</th><th>类目</th><th>价格</th>"
                 "<th>spuId</th></tr></thead><tbody>")
        for p in parties:
            L.append("<tr><td>%s</td><td class=\"mut\">%s</td>"
                     "<td class=\"num\">¥%s</td><td class=\"mut\">%s</td></tr>"
                     % (esc(p.get("spuName")), esc(p.get("catName")),
                        esc(p.get("price")), esc(p.get("spuId"))))
        L.append("</tbody></table></section>")

    # ---------------- 账户 ----------------
    if acc:
        L.append('<section class="sec"><h2><span class="dot"></span>你的账户</h2>'
                 '<div class="acct">')
        L.append('<div class="stat"><div class="k">可用积分</div>'
                 '<div class="v">%s</div></div>' % esc(acc.get("availablePoint", "-")))
        L.append('<div class="stat"><div class="k">累计积分</div>'
                 '<div class="v">%s</div></div>' % esc(acc.get("accumulativePoint", "-")))
        exp = acc.get("expiredPoint")
        if exp not in (None, "0", "0.0"):
            L.append('<div class="stat"><div class="k">已过期积分</div>'
                     '<div class="v warn">%s</div></div>' % esc(exp))
        cur_exp = acc.get("currentMouthExpirePoint")
        if cur_exp not in (None, "0", "0.0"):
            L.append('<div class="stat"><div class="k">本月将过期</div>'
                     '<div class="v warn">%s</div></div>' % esc(cur_exp))
        L.append("</div></section>")

    # ---------------- 往期 ----------------
    past = radar.get("past") or []
    if past:
        L.append('<section class="sec"><h2><span class="dot"></span>往期回顾</h2>')
        L.append('<div class="date-h">最近 %d 条</div>' % min(len(past), 8))
        for a in past[:8]:
            L.append('<div class="act"><div class="body"><div class="hd">%s'
                     '<span class="ti">%s</span></div></div></div>'
                     % (_badge(a.get("category", "其他")), esc(a.get("title", ""))))
        L.append("</section>")

    L.append("</main>")

    # ---------------- Footer ----------------
    link = (' · <a href="%s">GitHub 仓库</a>' % esc(repo_url)) if repo_url else ""
    L.append('<footer class="foot"><div class="wrap">'
             "本页面为麦当劳程序员节创意开发大赛参赛作品，由参赛者独立开发，"
             "<b>非麦当劳官方产品</b>。<br>"
             "餐品信息、价格及供应状态以麦当劳官方渠道的实时结果为准。<br>"
             "<code>python radar_cli.py --demo --html &gt; demo.html</code> · "
             "由 <code>radar_html.py</code> 生成%s</div></footer>" % link)

    L.append("<script>")
    L.append("document.querySelectorAll('.filters button').forEach(function(b){")
    L.append("  b.addEventListener('click',function(){")
    L.append("    var c=b.dataset.cat;")
    L.append("    document.querySelectorAll('.filters button').forEach(function(x){")
    L.append("      x.classList.toggle('on',x===b);});")
    L.append("    document.querySelectorAll('.act').forEach(function(el){")
    L.append("      el.style.display=(c==='all'||el.dataset.cat===c)?'':'none';});")
    L.append("    document.querySelectorAll('.sec[data-dynamic]').forEach(function(s){")
    L.append("      var vis=s.querySelectorAll('.act').length;")
    L.append("      var shown=0;")
    L.append("      s.querySelectorAll('.act').forEach(function(e){")
    L.append("        if(e.style.display!=='none'){shown++;}});")
    L.append("      s.style.display=(shown>0||c==='all')?'':'none';});")
    L.append("  });")
    L.append("});")
    L.append("</script>")

    L.append("</body>")
    L.append("</html>")
    return "\n".join(L)
