# 🛡️ 自动逆向 Agent

> **本地部署的 Web/JS 协议逆向自动化系统**
> 基于 Claude Code + Node.js + Python 工具链，输入目标站点即可自动完成情报收集 → 流量分析 → 加密定位 → 代码还原 → 端到端验证。

---

## 📁 项目结构

```
逆向agent/
├── .claude/
│   ├── CLAUDE.md              # 项目总览与快速开始
│   ├── settings.json          # Claude Code 配置（自动加载规则）
│   └── rules/                 # 逆向规则库（自动注入上下文）
│       ├── 01-core-constitution.md    # 核心宪法（边界、准入、验收）
│       ├── 02-reverse-playbook.md     # 操作手册（Phase、路线、Hook）
│       ├── 03-env-supplement.md       # 补环境定义与标准
│       ├── 04-jsvmp-guide.md          # JSVMP 与极难加密指南
│       └── 05-sites-index.md          # 站点实战经验索引
├── scripts/
│   ├── init-site.py           # 初始化新站点目录脚手架
│   ├── hook-templates.js      # 浏览器 Hook 注入模板库
│   ├── env-detector.js        # 缺失环境自动探测框架
│   └── verify-e2e.py          # 端到端验证脚本
├── sites/
│   ├── _templates/            # 新站点文档模板
│   └── {domain}/              # 各目标站点工作目录
│       ├── README.md
│       ├── plan.md
│       ├── src/
│       │   ├── encrypt.js     # 扣取的加密代码
│       │   ├── env.js         # 补环境代码
│       │   └── solver.py      # Python 协议请求主程序
│       └── docs/
│           ├── api.md         # 接口文档与真实样本
│           ├── crypto.md      # 加密定位与 Hook 记录
│           └── notes.md       # 阶段快照与调试笔记
├── .venv/                     # Python 虚拟环境
└── README.md                  # 本文件
```

---

## 🚀 快速开始

### 环境要求

- **OS**: Windows 10/11
- **Node.js**: 18+ (建议 v20+)
- **Python**: 3.10+（使用项目内 `.venv`）
- **Claude Code**: 最新版 CLI

### 1. 初始化新站点

```bash
# 激活虚拟环境（Windows PowerShell）
.venv\Scripts\activate

# 初始化站点脚手架
python scripts/init-site.py --domain toutiao.com --url https://www.toutiao.com
```

### 2. 启动自动逆向 Agent

在 Claude Code 中，进入站点目录后，Agent 会自动加载规则并按阶段执行：

```bash
cd sites/toutiao.com
# 然后向 Claude Code 描述你的逆向目标即可触发 Agent 工作流
```

### 3. 各阶段手动触发

Agent 的自动逆向分为 5 个阶段：

| 阶段 | 名称 | 命令/触发方式 | 产出 |
|------|------|---------------|------|
| **Phase 0** | 情报收集 | `WebSearch` 自动搜索 | `docs/notes.md` 技术摘要 |
| **Phase 1** | 流量分析 | 浏览器抓包 + `hook-templates.js` | `docs/api.md` 接口文档 |
| **Phase 2** | 定位加密 | Hook 注入 + 调用栈分析 | `docs/crypto.md` 定位报告 |
| **Phase 3** | 编写 Plan | 编写 `plan.md` 并获用户确认 | `plan.md` 方案文档 |
| **Phase 4** | 代码还原 | 扣代码 / 补环境 / 纯算 | `src/` 代码产出 |
| **Phase 5** | 端到端验证 | `python scripts/verify-e2e.py` | 验证报告 |

---

## 🧰 脚本工具说明

### `scripts/init-site.py` — 站点初始化

```bash
python scripts/init-site.py --domain <domain> --url <url> [--skip-phase0]
```

根据域名创建 `sites/{domain}/` 完整目录结构和初始文档。

### `scripts/hook-templates.js` — Hook 模板库

在浏览器控制台执行，或通过网络注入：

```javascript
// 流量分析阶段
AutoReverseHook.injectPhase1("a_bogus");

// 加密定位阶段
AutoReverseHook.injectPhase2();

// 全量注入
AutoReverseHook.injectAll("sign");
```

### `scripts/env-detector.js` — 环境自动探测

```bash
node scripts/env-detector.js --target sites/example.com/src/encrypt.js --output sites/example.com/src/env.js --max-iter 10
```

自动运行加密 JS，捕获报错并生成对应的补环境代码。

### `scripts/verify-e2e.py` — 端到端验证

```bash
python scripts/verify-e2e.py --domain example.com --url "https://api.example.com/data" --func generateSign --params '{"offset":0}'
```

调用加密函数生成参数，发送真实 HTTP 请求，验证服务端响应。

---

## 📜 核心约束

1. **协议优先**：最终交付必须是 Python 协议请求脚本，禁止浏览器自动化采集。
2. **真实数据优先**：所有分析必须以真实抓包样本为准，禁止占位符/猜测。
3. **Plan 准入**：Phase 3 必须产出 `plan.md` 并获得用户确认，才能进入 Phase 4。
4. **端到端验证**：必须完成"浏览器实测值 → 本地还原值 → 服务端响应"的真实链路对照。
5. **缺什么补什么**：补环境严禁搬运全量 JSDOM，只补执行路径真正依赖的项。

---

## 🗂️ 规则文件索引

| 文件 | 用途 | 加载方式 |
|------|------|----------|
| `01-core-constitution.md` | 安全边界、Phase 准入、验收标准 | `alwaysApply: true` |
| `02-reverse-playbook.md` | 详细 Phase 手册、调试路线 A/B/C、Hook 规范 | 按需读取 |
| `03-env-supplement.md` | 补环境定义、监控框架、DOM 模板库 | 按需读取 |
| `04-jsvmp-guide.md` | JSVMP 架构拆解、五步法、AI 辅助方案 | 按需读取 |
| `05-sites-index.md` | 站点实战经验索引、验证码与加密范式 | 按需读取 |

---

## 🔄 工作流示意

```
用户输入目标 URL
      │
      ▼
┌─────────────┐
│  Phase 0    │ ──► WebSearch 情报收集 ──► 写入 docs/notes.md
│ 情报收集    │
└─────────────┘
      │
      ▼
┌─────────────┐
│  Phase 1    │ ──► 浏览器抓包 / Hook 注入 ──► 写入 docs/api.md
│ 流量分析    │
└─────────────┘
      │
      ▼
┌─────────────┐
│  Phase 2    │ ──► 加密定位 / 调用栈分析 ──► 写入 docs/crypto.md
│ 定位加密    │
└─────────────┘
      │
      ▼
┌─────────────┐
│  Phase 3    │ ──► 编写 plan.md ──► 用户确认
│ 编写 Plan   │
└─────────────┘
      │ (用户确认后)
      ▼
┌─────────────┐
│  Phase 4    │ ──► 扣代码 / 补环境 / 纯算 ──► src/ 产出
│ 代码还原    │
└─────────────┘
      │
      ▼
┌─────────────┐
│  Phase 5    │ ──► verify-e2e.py 验证 ──► e2e_report.json
│ 端到端验证  │
└─────────────┘
      │
      ▼
   🎉 完成
```

---

## 📌 使用提示

- **新站点**：始终先用 `init-site.py` 创建目录，再开始逆向工作。
- **情报收集**：Phase 0 可跳过，但强烈建议执行，常能找到现成思路。
- **JSVMP 处理**：直接扣代码 + 补环境，不要尝试纯算还原（除非用户明确要求）。
- **补环境**：使用 `env-detector.js` 自动探测缺失项，再手动精调指纹返回值。
- **验证**：最终必须使用 `verify-e2e.py` 做真实请求验证，不能仅靠离线对比。

---

**版本**: 2026-06-02
