---
description: 自动逆向 Agent 操作手册（详细 Phase、调试路线、Hook 规范、命令示例）
alwaysApply: false
---

# 自动逆向 Agent 操作手册

> 本文件是 `01-core-constitution.md` 的配套操作手册。
> 当需要详细步骤、路线选择、Hook 细节或命令示例时再读取。
> 若与主规则冲突，始终以 `01-core-constitution.md` 为准。

## 1. 术语约定

- **调试路线**：指 Phase 1/2 使用的浏览器与抓包/断点方案，即路线 A/B/C
- **执行优先级**：先确定调试路线，再选择工作流 skill

## 2. Phase 手册

### Phase 0：情报收集

- 触发条件：用户未明确说"跳过情报收集"或"直接调试"
- 动作：接收目标 URL 后，禁止立即打开浏览器
- 搜索建议：
  - `"{target_url} 逆向"`
  - `"{target_url} reverse"`
  - `"{target_url} 加密"`
  - `"{target_domain} jsvmp"`
  - `"{target_domain} 签名"`
- 产出：技术栈判断、已知加密/混淆特征、候选风控类型、易踩坑点
- 落盘：把摘要、候选方向、已排除方向写入 `sites/{domain}/docs/notes.md`

### Phase 1：流量与协议分析

核心思想：先看浏览器实际发了什么请求，再决定分析什么代码。

必须产出：
- 接口列表：URL、Method、Content-Type
- 请求参数清单：参数名、值、是否明文
- 至少一组真实请求/响应样本
- 哪些参数需要逆向

建议步骤：
1. 打开目标页面
2. 抓关键请求
3. 记录 Headers、Body、Cookie、Query、Response
4. 对比明文输入与请求中的密文字段
5. 标记前置接口、验证码接口、公钥接口、票据接口

落盘：
- `docs/api.md`：接口、样本、响应、Cookie 传递链
- `docs/notes.md`：当前调试路线、失败尝试、排除理由

### Phase 2：定位加密逻辑

核心思想：从动态参数名倒推到写入点、调用链和加密函数。

必须产出：
- 加密函数或关键写入点文件位置
- 算法类型、密钥/IV/模式或其来源
- 浏览器实测输入/输出
- 本地复现输入/输出对照

建议步骤：
1. 搜参数名、加密关键词、请求写入点
2. 在请求发送前断住
3. 看调用栈，找到真实写入函数
4. Hook `fetch` / `XHR` / `CryptoJS` / `SubtleCrypto`
5. 对比中间值与最终值

落盘：
- `docs/crypto.md`：函数位置、Hook 命中、输入输出对照
- `docs/notes.md`：未解释差异、下一步验证计划

### Phase 3：写 Plan

未经用户确认，严禁进入 Phase 4。

`plan.md` 最少包含：
1. 接口信息
2. 请求参数
3. 真实样本对照
4. 加密方式与实证依据
5. 验证码或人机校验链路
6. 实现方案
7. 验证计划

用户确认项至少包含：
- 加密方式是否正确
- 选择纯算还是补环境
- 选择纯 Python 还是 Python + Node.js
- 是否按真实样本做端到端验证

### Phase 4：代码还原

建议实现顺序：
1. 写最小签名器/加密器
2. 做浏览器值与本地值逐字节对照
3. 写 Python 主流程
4. 接入验证码或票据链路
5. 做真实样本端到端验证

完成前必须确认：
- 浏览器实测动态字段 vs 本地还原动态字段
- 浏览器实测请求结构 vs Python 实际请求结构
- 服务端响应是否达到与浏览器同级别的有效结果

## 3. 验证码与校验链路

边界：
- 只做授权范围内的校验接口、参数、轨迹、加密字段还原
- 只交付 Python 协议侧复现
- 不以绕过风控、批量破解为交付目标

类型识别：

| 类型 | 协议侧关注点 |
|------|--------------|
| 滑块 / 拼图 | 初始化图资源、缺口偏移、轨迹或等价加密载荷 |
| 点选 / 文字顺序 | 坐标序列编码、提交顺序、签名 |
| 旋转 / 角度 | 角度如何进入请求体或签名 |
| 行为 / 无感 | 行为数据采集字段、压缩/加密方式、下游 token 衔接 |
| 短信 / 图形字符 | OCR 或用户指定的合规打码通道 |
| JSVMP / VM | 先实证 opcode/环境访问，再谈补环境 |

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

## 4. 调试路线 A/B/C

> `adspower-browser` 和 `js-reverse-mcp` 是两个独立的浏览器进程，不能协同共享状态。

### 路线 A：AdsPower
- 优点：指纹安全
- 适用：需要真实浏览器指纹，但不依赖断点/源码搜索
- 缺点：难以做深度定位

### 路线 B：js-reverse-mcp
- 优点：源码搜索、断点、调用栈完整
- 适用：调试优先、站点对指纹不敏感
- 缺点：普通 Chrome 可能被风控

### 路线 C：CDP 桥
- 优点：指纹安全 + 可编程调试
- 适用：既要真实指纹又要深度调试
- 缺点：实现和维护成本更高

路线选择：
```text
需要指纹保护？
  ├─ 是 -> 路线 A 或 C
  └─ 否 -> 路线 B
```

## 5. MCP 分工

| Phase | 路线 A | 路线 B | 路线 C |
|-------|--------|--------|--------|
| Phase 1 | AdsPower + Hook | `js-reverse-mcp` 抓请求 | AdsPower + Python CDP |
| Phase 2 | 不推荐 | `js-reverse-mcp` 断点/搜索/调用栈 | Python CDP Debugger |
| Wasm | `ida-pro-mcp` | `ida-pro-mcp` | `ida-pro-mcp` |

常见故障：

| 场景 | 检测 | 处理 |
|------|------|------|
| AdsPower 未启动 | `check-status` 失败 | 提示用户启动客户端 |
| `js-reverse-mcp` 未连页面 | `list_scripts` 为空 | 先 `new_page` 或 `select_page` |
| Hook 未生效 | 页面已初始化完毕 | 先注入再导航，或刷新页面 |
| 浏览器断开 | WebSocket 异常 | 尝试重连一次 |

## 6. PowerShell 与命令示例

Windows 下使用正确 PowerShell 语法：

| 操作 | 正确命令 | 错误命令 |
|------|---------|----------|
| 创建目录 | `New-Item -ItemType Directory -Force -Path path1,path2` | `mkdir -p path/{a,b}` |
| 下载文件 | `Invoke-WebRequest -Uri URL -OutFile PATH` | `curl -L -o PATH URL` |
| Python 执行 | `.venv\Scripts\python.exe script.py` | `python script.py` |
| 查看文件 | `Get-Content PATH -TotalCount N` | `head -N PATH` |
| 多条命令 | `cmd1; cmd2` | `cmd1 && cmd2` |

执行规范：
- 多行 Python 不用 `-c`
- 长命令优先落脚本
- 大输出优先写文件

## 7. Hook 注入规范

### 路线 B
1. 首选 `inject_before_load`
2. 先 Hook 后导航
3. 或注入后刷新
4. 用 console 日志或调用栈回收证据

### 路线 C
1. 用 CDP 的 `Page.addScriptToEvaluateOnNewDocument`
2. 用 `Runtime.consoleAPICalled` 或 `Runtime.evaluate` 回收结果

### 路线 A
1. 仅适合页面加载后做轻量 Hook
2. 不适合深度断点调试

通用：
- 可 Hook `fetch`、`XHR`、`CryptoJS.MD5/AES/SHA256`
- 必须记录输入输出，不能只记录"命中过"
