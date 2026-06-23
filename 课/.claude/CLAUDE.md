# 自动逆向 Agent —— 项目文档

> **项目定位**：本地部署的 Web/JS 协议逆向自动化 Agent，基于 Claude Code + Node.js + Python 工具链。
> **核心目标**：输入目标站点 → Agent 自动完成情报收集 → 流量分析 → 加密定位 → 代码还原 → 端到端验证。

---

## 项目结构

```
逆向agent/
├── .claude/
│   ├── CLAUDE.md              # 本文件：项目总览
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
│   └── verify-e2e.py          # 端到端验证脚本（Python + JS）
├── sites/
│   ├── _templates/            # 新站点文档模板
│   │   ├── README.md
│   │   ├── plan.md
│   │   └── docs/
│   │       ├── api.md
│   │       ├── crypto.md
│   │       └── notes.md
│   └── {domain}/              # 各目标站点工作目录（按域名）
│       ├── README.md
│       ├── plan.md
│       ├── src/
│       │   ├── encrypt.js     # 扣取的加密代码
│       │   ├── env.js         # 补环境代码
│       │   └── solver.py      # Python 协议请求主程序
│       └── docs/
│           ├── api.md
│           ├── crypto.md
│           └── notes.md
├── .venv/                     # Python 虚拟环境（项目级）
└── .qoder/                    # Qoder 历史配置（兼容保留）
```

---

## 运行环境

- **OS**: Windows 10/11 (win32)
- **Node.js**: 18+ (建议 v20+)
- **Python**: 3.10+（使用项目内 `.venv`）
- **Claude Code**: 最新版 CLI
- **浏览器**: AdsPower / Chrome DevTools / CDP 桥（按需）

---

## Agent 自动逆向五阶段

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Phase 0    │ ──► │  Phase 1    │ ──► │  Phase 2    │ ──► │  Phase 3    │ ──► │  Phase 4    │
│ 情报收集    │     │ 流量分析    │     │ 定位加密    │     │ 编写 Plan   │     │ 代码还原    │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

| 阶段 | 目标 | 关键动作 | 产出 |
|------|------|----------|------|
| **Phase 0** 情报收集 | 识别技术栈与加密特征 | WebSearch、GitHub 搜索、指纹比对 | `docs/notes.md` 技术摘要 |
| **Phase 1** 流量分析 | 抓包获取真实请求样本 | 抓关键请求、记录 Headers/Body/Cookie | `docs/api.md` 接口文档 |
| **Phase 2** 定位加密 | 找到加密函数与算法 | Hook `fetch`/`XHR`、`console.trace` | `docs/crypto.md` 定位报告 |
| **Phase 3** 编写 Plan | 制定还原方案并获确认 | 写 `plan.md`，用户确认加密方式与路线 | `plan.md` 方案文档 |
| **Phase 4** 代码还原 | 扣代码/补环境/纯算 | 扣取 JS、补环境、Python 协议脚本 | `src/` + 端到端验证 |

---

## 快速开始

### 1. 初始化新站点

```bash
# 自动创建站点目录结构
python scripts/init-site.py --domain example.com --url https://www.example.com
```

### 2. 进入自动逆向流程

```bash
# 在 Claude Code 中，输入目标 URL 即可触发 Agent
cd sites/example.com
# Agent 自动按 Phase 0→4 执行
```

### 3. 手动触发各阶段

```text
/reverse --phase 0 --target https://www.example.com   # 情报收集
/reverse --phase 1 --target https://www.example.com   # 流量分析
/reverse --phase 2 --target https://www.example.com   # 定位加密
/reverse --phase 3                                     # 编写 Plan
/reverse --phase 4                                     # 代码还原
```

---

## 核心约束（不可突破）

1. **协议优先**：最终交付必须是 Python 协议请求脚本，禁止浏览器自动化采集。
2. **真实数据优先**：所有分析必须以真实抓包样本为准，禁止占位符/猜测。
3. **Plan 准入**：Phase 3 必须产出 `plan.md` 并获得用户确认，才能进入 Phase 4。
4. **端到端验证**：必须完成"浏览器实测值 → 本地还原值 → 服务端响应"的真实链路对照。
5. **缺什么补什么**：补环境严禁搬运全量 JSDOM，只补执行路径真正依赖的项。

---

## 工具链决策树

```
需要执行什么操作？
├─ 访问页面/触发请求？    → AdsPower / chrome-devtools-mcp
├─ 分析代码逻辑？          → js-reverser / ast-deobfuscation
├─ 读写文件？              → filesystem MCP
├─ 执行本地命令？          → Bash / run_in_terminal
└─ 情报搜索？              → WebSearch / WebFetch
```

---

## 配套规则文件

- `rules/01-core-constitution.md` — 核心宪法（安全边界、Phase 准入、验收标准）
- `rules/02-reverse-playbook.md` — 操作手册（详细 Phase、调试路线 A/B/C、Hook 规范）
- `rules/03-env-supplement.md` — 补环境定义与监控框架（大厂标准版 watch、DOM 模板）
- `rules/04-jsvmp-guide.md` — JSVMP 与极难加密通用逆向指南
- `rules/05-sites-index.md` — 站点实战经验索引（验证码与加密范式）

---

**版本**: 2026-06-02
