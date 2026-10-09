<p align="center">
  <img src="docs/banner.svg" alt="麦麦活动雷达" width="720">
</p>

# 📡 麦麦活动雷达 · MCD Activity Radar

> **一句话扫清麦当劳这个月有什么值得抢**——新品、联名限定周边、限时优惠、门店派对，
> 自动分类、按开抢时间排倒计时，再也不会错过「10月15日10:45 联名徽章开售」。

麦当劳程序员节创意开发大赛参赛作品 · 基于**麦当劳中国 MCP** 开发 · 非麦当劳官方产品

[![Type](https://img.shields.io/badge/Type-MCP%20Skill-DA291C?style=flat)](https://github.com/M-China/mcd-mcp-server)
[![Powered by](https://img.shields.io/badge/Powered%20by-mcd--mcp-FFC72C?style=flat&labelColor=27251F)](https://open.mcd.cn/mcp)
[![WorkBuddy](https://img.shields.io/badge/Developed%20with-WorkBuddy-27251F?style=flat)](https://www.workbuddy.cn)
[![License](https://img.shields.io/badge/License-MIT-27251F?style=flat)](LICENSE)

---

## 😤 你有没有过这种时候

- 刷到「麦当劳 × GD 联名棒球帽」的时候，**已经卖完了**
- 听说昨天有 **Nike 联名鞋 8888 积分兑换**，点进去发现**活动昨天结束**
- 想给孩子约一场麦麦生日派对，翻了半天 App 也不知道**哪家店能约、要约到几号**
- 月底一看账户——**5581 积分过期了**，自己完全不知道

麦当劳的活动信息散落在推文、App、公众号、各种群里。
**这个技能就是把这些信息收拢成一张雷达图。**

## ✨ 它做什么

| 能力 | 说明 |
|---|---|
| ⏰ **开抢倒计时** | 从营销文案里精确抽出「10月15日10:45开售」，算出「还有 5 天 19 小时」 |
| 🔥 **正在进行** | 当前全部在搞的活动，按类别分组 |
| 📅 **即将到来** | 未来活动，标好开抢时间 |
| 🎁 **限定周边** | 积分兑换的限量周边（Nike 联名鞋、联名礼盒…），含兑换窗口 |
| 🎉 **门店活动** | 可预约的派对/品鉴会/体验营，含价格与 spuId |
| 👤 **你的账户** | 积分余额 + ⚠️ **即将过期积分提醒** |
| 🎲 **今日手气（彩蛋）** | 选择困难时，以卦象作随机符号，从真实菜单里替你挑一个 |

## 🖥️ 效果预览

```text
# 📡 麦麦活动雷达

> 数据时间：2026-10-09 15:14 ｜ 非麦当劳官方产品

## ⏰ 开抢倒计时
| 倒计时 | 开抢时间 | 活动 | 类别 |
|---|---|---|---|
| **还有 8 小时 46 分钟** | 10-10 00:00 | 预约麦金喜抽奖，🉐[积分霸王餐] | 抽奖福利 |
| **还有 5 天 19 小时** | 10-15 10:45 | 麦当劳 X PEACEMINUSONE | 联名限定 |
| **还有 12 天 19 小时** | 10-22 10:45 | 第三周周边即将开售✨限定主题丝巾！ | 联名限定 |

## 🔥 正在进行（14）
- **[门店活动] 乐享90分钟高质量亲子时间**
- **[联名限定] 麦当劳 X PEACEMINUSONE**  GD同款联名复古棒球帽
- **[新品上市] 韩式风味蘸酱上新❤️就「酱」心有所「薯」**
  ...

## 🎁 限定周边（积分兑换 · 限量）
| 商品 | 积分 | 卖点 | 窗口 |
|---|---:|---|---|
| Nike Book 2 麦当劳特别联名款 | 8888 | 每人限购一双，每日 14:00 准时开抢 | 2026-06-05 ~ 06-05 |
| 酸黄瓜吧唧礼盒 | 800 | 限量 150 份，先兑先得 | 2026-08-14 ~ 08-14 |

## 👤 你的账户
- 可用积分：**61.8**
- 累计积分：6424.8
- 已过期积分：5581
```

完整输出见 [`docs/demo-output.md`](docs/demo-output.md)。

## 🎲 彩蛋：今日手气 · 麦门签

「今天吃什么」是终极选择困难。这个彩蛋让**传统卦象替你决定**——
以卦象作**随机符号**，从**今日真实在售餐品**里挑一个「天意之选」。

```bash
python radar_cli.py --fortune            # 只出一签
python radar_cli.py --fortune --seed 42  # 固定种子，可复现
```

```text
# 今日手气 · 麦门签

> 2026-10-09（周五）| 月建：戌 | 日辰：丙辰 | 起卦：铜钱法

本卦：天地否（乾宫，三爻世） → 山地剥

| 爻位      | 六神 | 六亲 | 纳支 | 爻象   |
|-----------|------|------|------|--------|
| 上爻 ·应  | 青龙 | 父母 | 戌土 | ▅▅▅▅▅ |
| 五爻      | 玄武 | 兄弟 | 申金 | ▅▅▅▅▅ ○ |
| 三爻 ·世  | 螣蛇 | 妻财 | 卯木 | ▅▅ ▅▅ |

世爻五行 木，六神 螣蛇 → 今日手气：甜蜜

天意之选：新地 ¥14.5
```

**为什么不是随口一点**：起卦、装卦（纳甲、纳支、八宫归属、世应、六亲、六神）全部是
**查表型确定性计算**，封装在一个纯标准库文件里（`qian_engine.py`），不靠大模型心算，
同种子结果完全可复现。日干支用儒略日公式推算，已对照公开黄历校验（2026-10-09 = 丙辰日）。

> ⚖️ **定位说明**：这是**娱乐性的随机选餐游戏**——卦象仅作随机符号，**不做占卜与预测**，
> 不构成任何建议。

## 🚀 快速开始

### 方式一：离线体验（**无需 Token，30 秒跑通**）

```bash
git clone <本仓库地址>
cd mcd-activity-radar/skills/mcd-activity-radar/scripts

# 内置真实活动样本，直接出报告
python radar_cli.py --demo

# 看看 10 月 20 日视角下的雷达
python radar_cli.py --demo --today 2026-10-20

# 只看联名限定
python radar_cli.py --demo --only 联名限定

# 跑自测（41 项）
python selftest.py
```

### 方式二：接入真实麦当劳 MCP

1. 申请 MCP Token：[https://open.mcd.cn/mcp](https://open.mcd.cn/mcp)（手机号登录 → 控制台 → 激活）
2. 在 WorkBuddy 的【专家·技能·连接器】→【连接器】→【自定义连接器】→【配置 MCP】中，
   填入 [`mcp-config.example.json`](mcp-config.example.json) 的内容，把 `${MCD_MCP_TOKEN}` 换成你的真实 Token，保存并**启用**。
3. 设置环境变量后运行：

```bash
export MCD_MCP_TOKEN="你的Token"
python radar_cli.py --live
```

### 方式三：作为 WorkBuddy Skill 使用

```bash
cp -r skills/mcd-activity-radar ~/.workbuddy/skills/
```

（Windows 为 `%USERPROFILE%\.workbuddy\skills\`）

装好后直接在对话框里说：

```
麦当劳最近有什么活动
有什么联名周边要开抢
帮我看看这个月有什么值得抢的
```

## 🧠 它是怎么做到「不靠大模型算」的

这是本项目和「让 AI 念一遍活动列表」最本质的区别：

```
麦当劳 MCP                          确定性引擎                       WorkBuddy Agent
─────────────                      ──────────────                   ────────────────
campaign-calendar        ──→   解析日期小节                   ──→   用人话讲给用户听
mall-points-products             按(标题+文案)去重
query-my-account                 正则抽「10月15日10:45开售」
now-time-info                    算倒计时 / 分类
```

**为什么必须这样做：**

1. 让大模型心算「还有几天几小时」**不可靠也不可复现**，正则 + `datetime` 才算得准；
2. 活动日历里同一活动**跨多天重复出现**，靠模型去重会漏；
3. 同名活动文案不同（联名第一弹棒球帽 / 第二弹徽章）是**两条**，模型容易合并错；
4. 引擎有 **41 项自测**兜底，改逻辑不怕回归。

## 📁 目录结构

```
mcd-activity-radar/
├── README.md                        # 本文件
├── CONTEST_DECLARATION.md           # 参赛声明（官方原文，未改动）
├── MCP_INTEGRATION.md               # MCP Tool 清单 / 调用流程 / 业务价值
├── mcp-config.example.json          # 脱敏配置（仅环境变量占位符）
├── workbuddy.md                     # WorkBuddy 开发对话上下文
├── LICENSE
├── docs/
│   ├── demo-output.md               # 一次完整的雷达输出（含手气签）
│   ├── live-walkthrough.md          # 端到端实跑记录（MCP 真机调用留证）
│   ├── demo.html                    # 麦当劳风格可视化页（单文件，可直接打开）
│   └── banner.svg
└── skills/mcd-activity-radar/       # ← Skill 本体
    ├── SKILL.md                     # Agent 加载入口
    ├── scripts/
    │   ├── mcd_client.py            # 麦当劳 MCP Streamable HTTP 客户端（纯标准库）
    │   ├── radar_engine.py          # 解析 / 去重 / 抽时间 / 分类 / 渲染
    │   ├── radar_html.py            # 麦当劳风格单文件 HTML 渲染框架
    │   ├── qian_engine.py           # 今日手气·麦门签（确定性六爻装卦引擎）
    │   ├── radar_cli.py             # 命令行入口
    │   ├── selftest.py              # 41 项自测
    │   └── sample_data/             # 脱敏真实样本（活动 + 菜单，离线 demo 用）
    └── references/
        ├── mcp-tools.md             # Tool 字段映射与调用链
        └── activity-taxonomy.md     # 情报分类规则
```

## 👥 适合谁用

- **麦门信徒**：不想错过任何一场联名、限定周边
- **薅羊毛党**：想第一时间知道有什么券、什么活动
- **宝爸宝妈**：想给孩子约麦麦派对、体验营
- **积分大户**：不想让积分白白过期
- **效率党**：一句话扫清当月活动，不想自己刷 App

## 🔒 信息安全

本仓库**不含任何真实 Token、密钥或账号凭证**，配置一律使用 `${MCD_MCP_TOKEN}` 占位符。
`sample_data/` 内的数据来自公开 MCP 接口的真实返回，**已去除账户 ID**。详见 [`CONTEST_DECLARATION.md`](CONTEST_DECLARATION.md)。

## ⚖️ 合规自查

- 无真实 Token / 密钥，配置仅用占位符
- 不含他人个人信息
- 不贬低、不对比麦当劳品牌与产品
- 不调用抽奖类工具代抽，抽奖活动仅做**提醒**
- 不宣扬暴食、奢靡、拜金
- 「今日手气」彩蛋定位为**娱乐性随机选餐**，卦象仅作随机符号，不做占卜与预测
- `CONTEST_DECLARATION.md` 使用官方原文，一字未改
- 代码全部原创

## 📄 许可

MIT License，详见 [LICENSE](LICENSE)。
「麦当劳」「McDonald's」及相关商标归其权利人所有，本仓库不构成对任何商标的授权。

---

### 如果这个雷达帮你抢到过一次限定，点个 ⭐ Star 吧！

**本项目为麦当劳程序员节创意开发大赛参赛作品，由参赛者独立开发，非麦当劳官方产品。**
餐品信息、价格及供应状态以麦当劳官方渠道的实时结果为准。
