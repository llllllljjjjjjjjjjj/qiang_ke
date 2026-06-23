---
description: 站点实战经验索引（验证码与加密处理范式，脱敏）
alwaysApply: false
---

# Sites 实战经验索引

> **适用范围**：`sites/` 下已文档化的子项目。
> **优先级**：若与本文件或某 README 中的表述冲突，**始终以 `01-core-constitution.md`（协议优先、真实数据优先、调试路线 A/B/C、禁止 Selenium/Playwright/Puppeteer 采集）为准**。
> **不含**：任何第三方打码 token、Cookie、AccessKey、账号口令。

---

## 一、横向模式（通用套路）

| 模式 | 典型用法 | 代表场景 |
|------|----------|----------|
| **Python 请求 + Node 加密子进程** | `requests`/`curl_cffi` 主流程；加密、`anti_content`、`w`、RSA、WASM glue 放 Node，`subprocess` 或 **stdio JSON-RPC 长连接** | 拼多多、京东、抖音 |
| **滑块：识别 + 类人轨迹 + 服务端加密载荷** | OpenCV/模板匹配 ↔ 低置信回退云码；轨迹分段缓动 + Y 抖动；再把轨迹交给 SDK/WASM 生成 `tk`/`ct`/`captchaBody` | 京东、抖音、云片 |
| **第三方双图滑块 API** | `type` 与 **字段名**必须与文档一致（常见坑：`10107` vs `20111`，`image` vs `slide_image`/`background_image`）；返回 `data` 有时是 **字符串坐标** 有时是对象，需兼容解析 | 抖店、华润 |
| **WASM / jcap / rmc** | 异步初始化：`getCTData` 类同步路径可能为 null → **热身等待**或重建实例；**同一 WASM `instanceId`/`ii` 必须与加密侧缓存的 D 实例一致** | 京东 |
| **encodeURI 对齐** | Python `urllib.parse.quote` 默认与 JS `encodeURI` 不一致（如逗号）→ 使用 **`safe=` 与 JS 对齐**，否则服务端校验失败 | 京东 |
| **TLS / Header 维度** | `curl_cffi` impersonate 指定 Chrome 版本；Boss 等站 **`wt2`/`zp_at` 登录 Cookie + 完整 Client Hints** 与签名同等重要 | Boss 直聘 |
| **签名升级后弃纯离线 signer** | 业务升级签名体系后，旧 `signer.js` 直连可能作废 → **CDP 桥**让浏览器内 axios 代签 | 小红书 |
| **CDP 桥（路线 C）** | AdsPower 起真实会话 → Python `websocket-client` + `Runtime.evaluate` / 注入 webpack 全局 → **维持首页 feed 来源约束** | 小红书 |
| **阿里云 NVC** | JSONP `nvcPrepare` → Node **补环境**加载 `awsc.js`/`nvc.js` → `getNVCVal()` → `nvcAnalyze`；UMID/UAB 常需 stub | 阿里云验证 |
| **极验 4 定制** | load / verify 多步；`w` 可由 **Node vm + 修补 JS** 或 **纯算法 AES/RSA 备用路径**；`gct`/`em` 环境令牌与 `trackOffset` 绑定 | 华润定制 |

---

## 二、验证码与校验链路

边界：
- 只做授权范围内的校验接口、参数、轨迹、加密字段还原
- 只交付 Python 协议侧复现
- 不以绕过风控、批量破解为交付目标

策略优先级：
1. 纯算优先
2. 必要时 Node 补环境
3. 混淆重时叠加 `ast-deobfuscation`
4. Hook 只用于分析阶段
5. 第三方打码仅在用户明确要求时使用

厂商线索：

| 框架/线索 | 常见参数 |
|-----------|----------|
| 极验 | `gt`, `challenge`, `w` |
| 网易易盾 | `token`, `acToken`, `data` |
| 腾讯防水墙 | `aid`, `cap_cd`, `sess` |
| 阿里验证 | `nc_token`, `bizId`, `sig` |
| 数美 | `riskToken`, `request_id` |
| 瑞数等 | `_sd`, `_fd` 类动态字段 |

---

## 三、工具使用决策树

```
需要执行什么操作？
├─ 访问页面/触发请求？ → adspower-local-api (AdsPower 浏览器)
│   ├─ open-browser - 打开浏览器
│   ├─ navigate - 导航页面
│   ├─ evaluate_script - 执行 JS
│   ├─ screenshot - 页面截图
│   ├─ get-page-html - 获取页面 HTML
│   ├─ click-element - 点击元素
│   ├─ fill-input - 填写输入框
│   └─ get-profile-cookies - 获取 Cookie
│
├─ 分析代码逻辑？ → js-reverser (仅静态)
│   ├─ deobfuscate_code - 脱混淆
│   ├─ detect_crypto - 识别加密
│   └─ summarize_code - 代码分析
│
├─ 读写文件？ → filesystem
│   ├─ read_text_file - 读取
│   ├─ write_file - 写入
│   └─ create_directory - 创建目录
│
└─ 执行命令？ → run_in_terminal
    ├─ python xxx.py - 运行脚本
    └─ node xxx.js - 执行 JS
```

**工具优先级**：

1. **adspower-local-api**（AdsPower 浏览器操作）
   - ✅ 访问页面、触发请求 (`navigate`)
   - ✅ 执行 JS、获取返回值 (`evaluate_script`)
   - ✅ 页面截图、获取 HTML (`screenshot`, `get-page-html`)
   - ✅ 元素交互 (`click-element`, `fill-input` 等)

2. **ast-deobfuscation Skill**（代码脱混淆）
   - ✅ 处理普通混淆（字符串数组、控制流平坦化）
   - ❌ **不适用于 JSVMP**（虚拟机保护无法反混淆）

3. **js-reverser**（静态代码分析）
   - ✅ 代码理解、搜索
   - ❌ **禁止**浏览器相关功能

4. **chrome-devtools-mcp**（备用浏览器操作 - 不推荐）
   - ⚠️ 仅当 AdsPower 不可用时使用
   - ❌ 容易被检测，不推荐常规使用

5. **filesystem**（文件读写）
   - ✅ 保存加密代码、补环境代码

**⚠️ JSVMP 处理决策**：
```
遇到 JSVMP 加密？
├─ 用户要求做纯算？
│   ├─ 是 → 分析字节码 → 还原算法 → Python 实现（2-5天）
│   └─ 否 → ✅ 直接扣取 JS 文件 → 补环境运行（推荐）
└─ 普通混淆？
    └─ 使用 ast-deobfuscation Skill 脱混淆 → 扣代码 → 补环境
```

---

## 四、后续使用方式

1. **定点查阅**：提到某站时优先 **`sites/<name>/README.md`** 与 **`docs/*.md`**，本文件只做索引。
2. **不复述密钥**：云码 token、Cookie、`real_fingerprint.json` 内容等 **never** 贴入对话或规则。
3. **真实样本优先**：站点经验只能帮助缩小范围，不能替代真实抓包、真实响应和真实端到端对照。
4. **验证码 + 加密耦合任务**：Plan 里必须写清 **初始化接口 / 校验接口 / 票据字段 / 加密是否与登录同源**，并附至少一组真实样本证据。
5. **新增站点**：建议同步更新本文件「横向模式」表（可选）。

---

## 五、与其它规则的边界

| 主题 | 本文件 | `01-core-constitution.md` |
|------|--------|---------------------------|
| 真实数据优先、端到端验证、禁止占位验收 | 仅做补充提醒 | **唯一强制源** |
| 调试路线 A/B/C、禁止自动化采集 | 不重复强调 | **唯一强制源** |
| 具体站点参数与文件锚点 | **本文件** | 仅通用 Phase |
| 验证码类型与厂商线索 | 互补 | 协议视角边界 |
