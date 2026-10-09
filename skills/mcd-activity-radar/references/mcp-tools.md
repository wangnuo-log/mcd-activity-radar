# 麦当劳 MCP Tool 说明与字段映射

本技能共涉及 **7 个**麦当劳 MCP Tool，按「是否在运行时自动调用」分三类：

| 类别 | Tool | 说明 |
|---|---|---|
| **① 运行时自动调用**（`--live` 每次生成雷达） | `campaign-calendar`、`mall-points-products`（×2）、`query-my-account` | 雷达的数据来源 |
| **② 数据来源**（离线样本采集自，运行时不联网） | `query-nearby-stores`、`query-meals` | 「今日手气」选餐池；真实返回已脱敏固化为 `sample_data/menu.json` |
| **③ 开发探测 / 可选** | `now-time-info` | 倒计时基准的服务器时间校准（离线 demo 用本机时间） |

下文逐项说明字段与语义；文末「后续调用链」列出用户要「行动」时才触发的工具。

---

## 1. `campaign-calendar` —— 活动日历（核心）

**用途**：查询麦当劳中国当月的营销活动日历，返回进行中、往期和未来日期的活动。

**入参**

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `specifiedDate` | string | 否 | 基准日期 `yyyy-MM-dd`。传入则返回该日及前后各一个有活动的日子（共 3 天）；不传返回当月全部 |

**返回**：markdown 文本，结构如下

```
### 当前时间：2026-10-09 15:09:49

### 活动列表：

#### 2026年10月9日 今日
-   **活动标题**：麦当劳 X PEACEMINUSONE
    **活动内容介绍**：GD同款联名复古棒球帽
任意餐品消费加39.9元即可得
10月8日10:45开售
    **活动图片介绍**：
    <img src="https://cms-cdn.mcd.cn/img/...jpg" ...>

#### 2026年10月15日
-   **活动标题**：...
```

**关键业务语义（实测总结）**

1. `往期回顾` / `今日` / 无后缀 三种小节标签；`今日` 小节列出的是**当前全部在进行的活动**（可能十几条），不是当天才开始的。
2. **同一活动会跨多天重复出现**（如「PEACEMINUSONE」在 10-08、10-09、10-15 都出现）。
3. **同名不等于同活动**：10-08/10-09 是「棒球帽」，10-15 是「徽章第二弹」，标题相同但文案不同。
4. 开售时间写在**文案正文**里（「10月15日10:45开售」「积分抢先购10:40开抢」），需要正则抽取。

---

## 2. `mall-points-products` —— 商城/活动商品列表

**用途**：查询麦麦商城内可用积分兑换或现金购买的商品。

**入参**

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `catRuleIds` | string | 否 | 类目筛选，逗号分隔；不传返回全部 |

**类目取值**

| 值 | 含义 |
|---|---|
| `1>4` | 商品券（非预付优惠券） |
| `2` | 实物商品 |
| `2>8` | 周边产品 |
| `2>9` | 实物礼品卡 |
| `1>6>20` | 生日类派对 |
| `1>6>21` | 主题类派对 |
| `1>6>22` | 麦麦体验营 |
| `1>6>25` | 品鉴会 |
| `1>6>34` | 读书会 |
| `1>6>40` | 积分兑换活动 |

**本技能用法**

- `catRuleIds=2>8` → 限定周边（Nike 联名鞋、联名礼盒等）
- `catRuleIds=1>6>20,1>6>21,1>6>22,1>6>25,1>6>34,1>6>40` → 可预约的门店活动

**返回字段**（`data[]`）

| 字段 | 类型 | 说明 |
|---|---|---|
| `spuName` | string | 商品名称 |
| `spuId` | integer | 商品 ID，**预约门店活动时必需** |
| `point` | string | 所需积分 |
| `price` | string | 所需金额（现金） |
| `selling` | string | 商品卖点 |
| `upTime` / `downTime` | string | 可兑换起止时间 |
| `spuImage` | string | 商品图 |
| `catName` | string | 类目名称（生日类派对/品鉴会/…） |
| `status` | integer | 1-仓库中 2-上架 3-售罄 4-下架 5-预热 |

---

## 3. `query-my-account` —— 我的积分账户

**入参**：无

**返回字段**（`data`）

| 字段 | 说明 |
|---|---|
| `availablePoint` | 可用积分 |
| `accumulativePoint` | 累计积分 |
| `usedPoint` | 已使用积分 |
| `frozenPoint` | 冻结积分 |
| `expiredPoint` | 已过期积分 |
| `currentMouthExpirePoint` | **本月将过期积分**（资产提醒的关键字段） |
| `nextMouthExpirePoint` | 下月将过期积分 |
| `lastMouthExpirePoint` | 上月已过期积分 |

> 该工具会把「积分」统一按 `currency`（麦享会积分）返回。可用积分可能是小数（如 `61.8`）。

---

## 4. `now-time-info` —— 服务器当前时间（可选）

**入参**：无

**返回**：`timestamp` / `datetime` / `formatted` / `date` / `dayOfWeek` / `timezone` 等。

用于校准倒计时基准。**离线 demo 及 `--live` 默认均使用本机时间**；如需与服务器严格对齐，
可在生成倒计时前调用它取时间戳。

---

## 5. `query-nearby-stores` —— 附近门店（「今日手气」数据来源）

**用途**：定位餐厅，取 `storeCode`（`query-meals` 的必需入参）。

**入参**

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `beType` | integer | 是 | 业务类型，门店用 `1` |
| `searchType` | integer | 是 | 检索方式，按城市+关键词为 `2` |
| `city` | string | 是* | 城市名（如 `深圳市`） |
| `keyword` | string | 否 | 区域/地标关键词（如 `罗湖`） |

**返回**：门店列表，含 `storeCode` / 门店名 / 地址。

> 本技能在**采集样本阶段**用真实门店（示例取深圳罗湖某店）拉取菜单，随后脱敏固化为离线样本；
> 运行时不联网。若要让随机选餐彩蛋基于**实时菜单**，可先调本工具再调 `query-meals` 覆盖选餐池。

---

## 6. `query-meals` —— 门店在售菜单（「今日手气」选餐池）

**用途**：查询指定门店的实时在售餐品（汉堡 / 小食 / 饮品 / 麦咖啡 / 开心乐园餐等）。

**入参**

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `storeCode` | string | 是 | 门店编码（来自 `query-nearby-stores`） |
| `orderType` | integer | 是 | 点餐类型，堂食/外送等（示例用 `1`） |
| `beType` | integer | 是 | 业务类型 `1` |

**返回字段**：餐品 `code` / 名称 / 价格 / 分类 / 图片等。

> 「今日手气」的选餐池来自本工具的真实返回，已脱敏固化为 `sample_data/menu.json`（80+ 在售餐品），
> 供 `--demo` 离线跑通。

---

## 后续调用链（用户要「行动」时）

### A. 预约门店派对 / 品鉴会

```
mall-points-products (catRuleIds=1>6>20,...)   → 取 spuId
    → query-party-city    {spuId}              → 可选城市
    → query-party-store   {spuId, code, lat, lng} → 城市下门店
    → query-party-store-date {spuId, storeCode}   → 可预约日期
    → query-party-store-session {spuId, storeCode, ...} → 场次
    → party-order-create                        → 下单
```

### B. 把新品 / 活动餐吃掉

```
query-nearby-stores {beType:1, searchType:2}  → 门店
    → query-meals {storeCode, orderType, beType} → 菜单
    → calculate-price → create-order
```

### C. 用积分兑换限定周边

```
mall-points-products (catRuleIds=2>8) → spuId
    → mall-product-detail {spuId} → SKU
    → mall-create-order
```

### D. 领券

```
available-coupons → auto-bind-coupons → query-my-coupons
```

---

## 错误码

| code | 原因 | 处理 |
|---|---|---|
| 401 | Token 无效 / 过期 / 未提供 | 检查 `MCD_MCP_TOKEN` |
| 429 | 超过 600 次/分钟 | 降低请求频率 |
