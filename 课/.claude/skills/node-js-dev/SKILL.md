---
name: node-js-dev
description: >
  1. 提供 Node.js 项目的开发、调试、构建和逆向辅助。
  2. 当用户涉及 npm 包分析、JavaScript/TypeScript 反混淆、Node 原生插件分析、Electron 应用逆向时调用。
  3. 核心价值：高效处理 Node 生态工具链，安全分析 npm 包及打包产物。
version: 1.0.0
allowed_tools: [Read, Edit, Bash, Grep, Glob]
tags: [nodejs, npm, javascript, typescript, electron]
author: reverse-agent
risk_level: LOW
---

# Node.js Development Skill

## 概述
本技能覆盖 Node.js 项目开发、npm 包逆向分析、JavaScript 反混淆及 Electron 应用调试。

## 前置条件
- Node.js >= 18.x
- npm >= 9.x
- 建议启用 Corepack：`corepack enable`

## 工作流程
1. **项目初始化**：`npm init` / 使用已有 package.json
2. **依赖分析**：
   - 安装：`npm install`
   - 审计：`npm audit`
   - 依赖树：`npm ls --depth=0`
3. **代码反混淆**（逆向场景）：
   - 使用 `js-beautify` 或 `prettier` 格式化
   - 使用 `de4js` 或 AST 工具（@babel/parser）解混淆
4. **Electron 逆向**：
   - 提取 asar：`npx asar extract app.asar ./source`
   - 分析主进程与预加载脚本
5. **原生模块分析**：
   - 使用 `dumpbin /exports` (Win) 或 `nm -D` (Linux) 查看 .node 文件导出

## 最佳实践
- 分析不可信 npm 包时先在隔离容器安装。
- 使用 `npm ci` 保证生产依赖可复现。
- 优先使用 `npx` 调用项目本地 CLI 工具。

## 示例
用户：这个 npm 包看起来可疑，帮我分析入口文件。
→ 读取 package.json 的 main/bin 字段 → 分析入口脚本行为 → 检查 postinstall 钩子。

## 故障排查
- **node-gyp 编译失败**：检查 Python / VS Build Tools 安装。
- **模块找不到**：确认 NODE_PATH 或使用 `npm ls` 排查幽灵依赖。
